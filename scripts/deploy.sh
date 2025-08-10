#!/bin/bash
# Script de Despliegue Automatizado para Rexus.app
# Soporta despliegue en desarrollo, staging y producción

set -e  # Salir si hay errores

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuración por defecto
DEFAULT_ENV="development"
DEFAULT_BRANCH="main"
PROJECT_NAME="rexus"
APP_DIR="/opt/rexus"
BACKUP_DIR="/var/backups/rexus"
LOG_DIR="/var/log/rexus"
SYSTEMD_SERVICE="rexus.service"

# Función para mostrar ayuda
show_help() {
    echo -e "${BLUE}Script de Despliegue Automatizado - Rexus.app v2.0.0${NC}"
    echo ""
    echo "Uso: $0 [OPCIONES]"
    echo ""
    echo "Opciones:"
    echo "  -e, --environment   Entorno (development|staging|production) [default: development]"
    echo "  -b, --branch        Rama de Git a desplegar [default: main]"
    echo "  -u, --update        Solo actualizar código sin reinstalar dependencias"
    echo "  -r, --rollback      Rollback a la versión anterior"
    echo "  -c, --check         Solo verificar configuración sin desplegar"
    echo "  -h, --help          Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  $0 -e production -b release/v2.0.0"
    echo "  $0 --environment staging --update"
    echo "  $0 --rollback"
    echo "  $0 --check"
}

# Función para logging
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        "INFO")
            echo -e "${GREEN}[INFO]${NC} $timestamp - $message"
            ;;
        "WARN")
            echo -e "${YELLOW}[WARN]${NC} $timestamp - $message"
            ;;
        "ERROR")
            echo -e "${RED}[ERROR]${NC} $timestamp - $message"
            ;;
        "DEBUG")
            echo -e "${BLUE}[DEBUG]${NC} $timestamp - $message"
            ;;
    esac
}

# Función para verificar prerrequisitos
check_prerequisites() {
    log "INFO" "Verificando prerrequisitos..."
    
    # Verificar si se ejecuta como root o con sudo
    if [[ $EUID -ne 0 ]] && [[ "$ENVIRONMENT" == "production" ]]; then
        log "ERROR" "Este script debe ejecutarse como root en producción"
        exit 1
    fi
    
    # Verificar comandos necesarios
    local required_commands=("git" "python3" "pip3" "systemctl")
    for cmd in "${required_commands[@]}"; do
        if ! command -v $cmd &> /dev/null; then
            log "ERROR" "Comando requerido no encontrado: $cmd"
            exit 1
        fi
    done
    
    # Verificar Python 3.8+
    local python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    if [[ $(echo "$python_version >= 3.8" | bc -l) -eq 0 ]]; then
        log "ERROR" "Python 3.8+ requerido, encontrado: $python_version"
        exit 1
    fi
    
    log "INFO" "Prerrequisitos verificados ✓"
}

# Función para configurar directorios
setup_directories() {
    log "INFO" "Configurando directorios..."
    
    local directories=("$APP_DIR" "$BACKUP_DIR" "$LOG_DIR" "$APP_DIR/uploads" "$APP_DIR/temp" "$APP_DIR/static")
    
    for dir in "${directories[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir"
            log "INFO" "Directorio creado: $dir"
        fi
    done
    
    # Configurar permisos
    if [[ "$ENVIRONMENT" == "production" ]]; then
        chown -R www-data:www-data "$APP_DIR"
        chmod -R 755 "$APP_DIR"
        chmod -R 777 "$APP_DIR/uploads" "$APP_DIR/temp" "$LOG_DIR"
    fi
    
    log "INFO" "Directorios configurados ✓"
}

# Función para realizar backup
create_backup() {
    if [[ ! -d "$APP_DIR" ]]; then
        log "WARN" "No hay instalación previa para respaldar"
        return 0
    fi
    
    log "INFO" "Creando backup de la versión actual..."
    
    local backup_timestamp=$(date '+%Y%m%d_%H%M%S')
    local backup_path="$BACKUP_DIR/rexus_backup_$backup_timestamp"
    
    # Crear backup del código
    cp -r "$APP_DIR" "$backup_path"
    
    # Crear backup de la base de datos (solo esquema y datos críticos)
    if command -v sqlcmd &> /dev/null; then
        log "INFO" "Creando backup de base de datos..."
        sqlcmd -S localhost -E -Q "BACKUP DATABASE rexus_${ENVIRONMENT} TO DISK = '$backup_path/database_backup.bak'"
    fi
    
    # Comprimir backup
    tar -czf "$backup_path.tar.gz" -C "$BACKUP_DIR" "$(basename $backup_path)"
    rm -rf "$backup_path"
    
    # Mantener solo los últimos 5 backups
    ls -t "$BACKUP_DIR"/rexus_backup_*.tar.gz | tail -n +6 | xargs -r rm
    
    log "INFO" "Backup creado: $backup_path.tar.gz ✓"
    echo "$backup_path.tar.gz" > "$BACKUP_DIR/latest_backup.txt"
}

# Función para hacer rollback
rollback() {
    log "INFO" "Iniciando rollback..."
    
    local latest_backup_file="$BACKUP_DIR/latest_backup.txt"
    if [[ ! -f "$latest_backup_file" ]]; then
        log "ERROR" "No hay backup disponible para rollback"
        exit 1
    fi
    
    local backup_path=$(cat "$latest_backup_file")
    if [[ ! -f "$backup_path" ]]; then
        log "ERROR" "Archivo de backup no encontrado: $backup_path"
        exit 1
    fi
    
    # Detener servicio
    stop_service
    
    # Restaurar backup
    log "INFO" "Restaurando desde backup: $backup_path"
    rm -rf "$APP_DIR"
    tar -xzf "$backup_path" -C "$(dirname $APP_DIR)"
    
    # Restaurar base de datos si existe
    local db_backup="$(dirname $backup_path)/$(basename $backup_path .tar.gz)/database_backup.bak"
    if [[ -f "$db_backup" ]]; then
        log "INFO" "Restaurando base de datos..."
        sqlcmd -S localhost -E -Q "RESTORE DATABASE rexus_${ENVIRONMENT} FROM DISK = '$db_backup' WITH REPLACE"
    fi
    
    # Reiniciar servicio
    start_service
    
    log "INFO" "Rollback completado ✓"
}

# Función para clonar/actualizar código
deploy_code() {
    log "INFO" "Desplegando código desde rama: $BRANCH"
    
    if [[ -d "$APP_DIR/.git" ]]; then
        # Actualizar repositorio existente
        cd "$APP_DIR"
        git fetch origin
        git checkout "$BRANCH"
        git pull origin "$BRANCH"
        log "INFO" "Código actualizado ✓"
    else
        # Clonar repositorio
        log "INFO" "Clonando repositorio..."
        git clone -b "$BRANCH" https://github.com/company/rexus.git "$APP_DIR"
        cd "$APP_DIR"
        log "INFO" "Repositorio clonado ✓"
    fi
    
    # Mostrar información del commit
    local commit_hash=$(git rev-parse HEAD)
    local commit_message=$(git log -1 --pretty=format:"%s")
    log "INFO" "Commit desplegado: $commit_hash - $commit_message"
}

# Función para instalar dependencias
install_dependencies() {
    if [[ "$UPDATE_ONLY" == "true" ]]; then
        log "INFO" "Saltando instalación de dependencias (--update)"
        return 0
    fi
    
    log "INFO" "Instalando dependencias Python..."
    
    cd "$APP_DIR"
    
    # Crear entorno virtual si no existe
    if [[ ! -d "venv" ]]; then
        python3 -m venv venv
        log "INFO" "Entorno virtual creado"
    fi
    
    # Activar entorno virtual
    source venv/bin/activate
    
    # Actualizar pip
    pip install --upgrade pip
    
    # Instalar dependencias
    if [[ -f "requirements.txt" ]]; then
        pip install -r requirements.txt
        log "INFO" "Dependencias Python instaladas ✓"
    else
        log "WARN" "Archivo requirements.txt no encontrado"
    fi
    
    # Instalar dependencias específicas del entorno
    local env_requirements="requirements_${ENVIRONMENT}.txt"
    if [[ -f "$env_requirements" ]]; then
        pip install -r "$env_requirements"
        log "INFO" "Dependencias específicas de $ENVIRONMENT instaladas ✓"
    fi
}

# Función para configurar la aplicación
configure_app() {
    log "INFO" "Configurando aplicación para entorno: $ENVIRONMENT"
    
    cd "$APP_DIR"
    
    # Establecer variable de entorno
    export REXUS_ENV="$ENVIRONMENT"
    
    # Generar configuraciones por defecto si no existen
    if [[ ! -f "config/${ENVIRONMENT}.json" ]]; then
        python3 -c "
from config.config_manager import ConfigManager
import os
os.environ['REXUS_ENV'] = '$ENVIRONMENT'
manager = ConfigManager()
manager.generate_default_configs()
print('Configuraciones generadas')
"
        log "INFO" "Configuraciones por defecto generadas"
    fi
    
    # Validar configuración
    python3 -c "
from config.config_manager import ConfigManager
import os
import sys
os.environ['REXUS_ENV'] = '$ENVIRONMENT'
manager = ConfigManager()
validation = manager.validate_config()
if not validation['valid']:
    print('❌ Errores en configuración:')
    for error in validation['errors']:
        print(f'   - {error}')
    sys.exit(1)
else:
    print('✅ Configuración válida')
"
    
    log "INFO" "Configuración validada ✓"
}

# Función para ejecutar migraciones de base de datos
run_migrations() {
    log "INFO" "Ejecutando migraciones de base de datos..."
    
    cd "$APP_DIR"
    
    # Verificar si hay scripts de migración
    if [[ -d "scripts/database" ]]; then
        # Ejecutar migraciones pendientes
        for migration_file in scripts/database/migrations/*.sql; do
            if [[ -f "$migration_file" ]]; then
                log "INFO" "Ejecutando migración: $(basename $migration_file)"
                sqlcmd -S localhost -E -i "$migration_file"
            fi
        done
    fi
    
    # Ejecutar script de seguridad si existe
    if [[ -f "scripts/database/add_security_columns.sql" ]]; then
        log "INFO" "Aplicando mejoras de seguridad de BD..."
        sqlcmd -S localhost -E -i "scripts/database/add_security_columns.sql"
    fi
    
    log "INFO" "Migraciones completadas ✓"
}

# Función para ejecutar tests
run_tests() {
    if [[ "$ENVIRONMENT" == "production" ]]; then
        log "INFO" "Saltando tests en producción"
        return 0
    fi
    
    log "INFO" "Ejecutando tests..."
    
    cd "$APP_DIR"
    source venv/bin/activate
    
    # Ejecutar tests críticos
    if command -v pytest &> /dev/null; then
        python -m pytest tests/security/ tests/performance/ -v --tb=short
        log "INFO" "Tests ejecutados ✓"
    else
        log "WARN" "pytest no disponible, saltando tests"
    fi
}

# Función para configurar servicio systemd
setup_service() {
    if [[ "$ENVIRONMENT" != "production" ]] && [[ "$ENVIRONMENT" != "staging" ]]; then
        log "INFO" "Configuración de servicio no requerida para $ENVIRONMENT"
        return 0
    fi
    
    log "INFO" "Configurando servicio systemd..."
    
    # Crear archivo de servicio
    cat > "/etc/systemd/system/$SYSTEMD_SERVICE" << EOF
[Unit]
Description=Rexus.app - Sistema de Gestión
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=$APP_DIR
Environment=REXUS_ENV=$ENVIRONMENT
ExecStart=$APP_DIR/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    # Recargar systemd
    systemctl daemon-reload
    systemctl enable "$SYSTEMD_SERVICE"
    
    log "INFO" "Servicio systemd configurado ✓"
}

# Función para detener servicio
stop_service() {
    if systemctl is-active --quiet "$SYSTEMD_SERVICE"; then
        log "INFO" "Deteniendo servicio..."
        systemctl stop "$SYSTEMD_SERVICE"
        log "INFO" "Servicio detenido ✓"
    fi
}

# Función para iniciar servicio
start_service() {
    log "INFO" "Iniciando servicio..."
    systemctl start "$SYSTEMD_SERVICE"
    
    # Verificar que el servicio esté funcionando
    sleep 5
    if systemctl is-active --quiet "$SYSTEMD_SERVICE"; then
        log "INFO" "Servicio iniciado correctamente ✓"
    else
        log "ERROR" "Error iniciando servicio"
        systemctl status "$SYSTEMD_SERVICE"
        exit 1
    fi
}

# Función para verificar el despliegue
verify_deployment() {
    log "INFO" "Verificando despliegue..."
    
    # Verificar servicio
    if [[ "$ENVIRONMENT" == "production" ]] || [[ "$ENVIRONMENT" == "staging" ]]; then
        if ! systemctl is-active --quiet "$SYSTEMD_SERVICE"; then
            log "ERROR" "Servicio no está funcionando"
            return 1
        fi
    fi
    
    # Verificar que la aplicación responda (si tiene servidor web)
    cd "$APP_DIR"
    source venv/bin/activate
    
    # Test básico de importación
    python3 -c "
import sys
sys.path.append('.')
try:
    from main import main
    print('✅ Aplicación se puede importar correctamente')
except Exception as e:
    print(f'❌ Error importando aplicación: {e}')
    sys.exit(1)
"
    
    log "INFO" "Verificación completada ✓"
}

# Función para mostrar resumen del despliegue
show_summary() {
    log "INFO" "=== RESUMEN DEL DESPLIEGUE ==="
    echo ""
    echo -e "${GREEN}✅ Despliegue completado exitosamente${NC}"
    echo -e "${BLUE}Entorno:${NC} $ENVIRONMENT"
    echo -e "${BLUE}Rama:${NC} $BRANCH"
    echo -e "${BLUE}Directorio:${NC} $APP_DIR"
    echo -e "${BLUE}Logs:${NC} $LOG_DIR"
    
    if [[ -f "$BACKUP_DIR/latest_backup.txt" ]]; then
        local backup_file=$(cat "$BACKUP_DIR/latest_backup.txt")
        echo -e "${BLUE}Backup:${NC} $backup_file"
    fi
    
    echo ""
    echo -e "${YELLOW}Comandos útiles:${NC}"
    echo "  Ver logs: journalctl -u $SYSTEMD_SERVICE -f"
    echo "  Restart: systemctl restart $SYSTEMD_SERVICE"
    echo "  Status: systemctl status $SYSTEMD_SERVICE"
    echo "  Rollback: $0 --rollback"
    echo ""
}

# Parsear argumentos
ENVIRONMENT="$DEFAULT_ENV"
BRANCH="$DEFAULT_BRANCH"
UPDATE_ONLY="false"
ROLLBACK_MODE="false"
CHECK_ONLY="false"

while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -b|--branch)
            BRANCH="$2"
            shift 2
            ;;
        -u|--update)
            UPDATE_ONLY="true"
            shift
            ;;
        -r|--rollback)
            ROLLBACK_MODE="true"
            shift
            ;;
        -c|--check)
            CHECK_ONLY="true"
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            log "ERROR" "Opción desconocida: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validar entorno
if [[ ! "$ENVIRONMENT" =~ ^(development|staging|production)$ ]]; then
    log "ERROR" "Entorno inválido: $ENVIRONMENT"
    log "INFO" "Entornos válidos: development, staging, production"
    exit 1
fi

# Main script execution
main() {
    log "INFO" "Iniciando despliegue de Rexus.app v2.0.0"
    log "INFO" "Entorno: $ENVIRONMENT | Rama: $BRANCH"
    
    # Verificar prerrequisitos
    check_prerequisites
    
    # Modo rollback
    if [[ "$ROLLBACK_MODE" == "true" ]]; then
        rollback
        show_summary
        exit 0
    fi
    
    # Modo verificación solamente
    if [[ "$CHECK_ONLY" == "true" ]]; then
        cd "$APP_DIR" 2>/dev/null || { log "ERROR" "Directorio de aplicación no existe"; exit 1; }
        configure_app
        verify_deployment
        log "INFO" "Verificación completada"
        exit 0
    fi
    
    # Configurar directorios
    setup_directories
    
    # Crear backup antes del despliegue
    create_backup
    
    # Detener servicio si está corriendo
    stop_service
    
    # Desplegar código
    deploy_code
    
    # Instalar dependencias
    install_dependencies
    
    # Configurar aplicación
    configure_app
    
    # Ejecutar migraciones
    run_migrations
    
    # Ejecutar tests
    run_tests
    
    # Configurar servicio
    setup_service
    
    # Iniciar servicio
    start_service
    
    # Verificar despliegue
    verify_deployment
    
    # Mostrar resumen
    show_summary
}

# Ejecutar script principal
main "$@"
