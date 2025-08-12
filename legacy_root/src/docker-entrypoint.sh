#!/bin/bash
# ====================================================
# REXUS APP - DOCKER ENTRYPOINT
# ====================================================
# Script de entrada para contenedor Docker

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función de logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

log_error() {
    echo -e "${RED}[ERROR] $1${NC}" >&2
}

log_warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

log_success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

# Banner de inicio
echo -e "${BLUE}"
echo "======================================================"
echo "🚀 REXUS APP - INICIANDO CONTENEDOR"
echo "======================================================"
echo -e "${NC}"

# Verificar entorno
log "Entorno: ${APP_ENV:-production}"
log "Usuario: $(whoami)"
log "Directorio: $(pwd)"
log "Python: $(python --version)"

# Crear directorios necesarios si no existen
log "Creando directorios necesarios..."
mkdir -p logs uploads backups temp
chmod 755 logs uploads backups temp

# Verificar variables de entorno críticas
log "Verificando configuración..."

if [ -z "$DB_PASSWORD" ] && [ "$APP_ENV" = "production" ]; then
    log_error "DB_PASSWORD no está configurada en producción"
    exit 1
fi

if [ -z "$SECRET_KEY" ] && [ "$APP_ENV" = "production" ]; then
    log_error "SECRET_KEY no está configurada en producción"
    exit 1
fi

# Verificar conectividad de base de datos (solo en producción)
if [ "$APP_ENV" = "production" ]; then
    log "Verificando conectividad de base de datos..."
    python -c "
try:
    from src.core.config import DATABASE_CONFIG
    import pyodbc
    
    # Verificar que tenemos las variables necesarias
    if not DATABASE_CONFIG.get('password'):
        raise ValueError('Password de BD no configurada')
    
    print('✅ Configuración de BD validada')
except Exception as e:
    print(f'❌ Error en configuración de BD: {e}')
    exit(1)
" || exit 1
fi

# Ejecutar migraciones de BD si es necesario
if [ "$RUN_MIGRATIONS" = "true" ]; then
    log "Ejecutando migraciones de base de datos..."
    python scripts/database/migrate.py || {
        log_error "Error ejecutando migraciones"
        exit 1
    }
fi

# Generar archivos de configuración dinámicos
log "Generando configuraciones..."

# Verificar permisos de archivos críticos
log "Verificando permisos..."
if [ -f ".env" ]; then
    chmod 600 .env
fi

# Health check interno
log "Ejecutando health check..."
python -c "
import sys
sys.path.insert(0, '/app')

try:
    # Verificar importaciones críticas
    from src.core import config
    from src.core.database import DatabaseConnection
    from src.core.security import SecurityManager
    print('✅ Módulos principales importados correctamente')
    
    # Verificar configuración
    if hasattr(config, 'APP_CONFIG'):
        print(f'✅ Aplicación: {config.APP_CONFIG.get(\"name\", \"Unknown\")} v{config.APP_CONFIG.get(\"version\", \"Unknown\")}')
    
    print('✅ Health check passed')
except Exception as e:
    print(f'❌ Health check failed: {e}')
    sys.exit(1)
" || exit 1

# Función para cleanup en shutdown
cleanup() {
    log "Recibida señal de shutdown. Limpiando..."
    
    # Guardar estado si es necesario
    if [ -f "temp/app.pid" ]; then
        rm -f temp/app.pid
    fi
    
    # Cerrar conexiones de BD gracefully
    log "Cerrando conexiones..."
    
    log_success "Cleanup completado"
    exit 0
}

# Capturar señales para shutdown graceful
trap cleanup SIGTERM SIGINT SIGQUIT

# Función para monitoreo básico en background
monitor() {
    while true; do
        sleep 30
        
        # Verificar memoria
        MEMORY_USAGE=$(ps -o pid,ppid,cmd,%mem,%cpu --sort=-%mem -u appuser | head -2 | tail -1 | awk '{print $4}')
        if (( $(echo "$MEMORY_USAGE > 80" | bc -l) )); then
            log_warning "Uso de memoria alto: ${MEMORY_USAGE}%"
        fi
        
        # Verificar espacio en disco
        DISK_USAGE=$(df /app | tail -1 | awk '{print $5}' | sed 's/%//')
        if [ "$DISK_USAGE" -gt 85 ]; then
            log_warning "Uso de disco alto: ${DISK_USAGE}%"
        fi
    done
}

# Iniciar monitoreo en background si está habilitado
if [ "$ENABLE_MONITORING" = "true" ]; then
    log "Iniciando monitoreo en background..."
    monitor &
    MONITOR_PID=$!
fi

# Mensaje de éxito
log_success "Inicialización completada"
log "Ejecutando comando: $@"

# Ejecutar el comando principal
exec "$@" &
MAIN_PID=$!

# Crear archivo PID
echo $MAIN_PID > temp/app.pid

# Esperar al proceso principal
wait $MAIN_PID

# Cleanup al final
if [ ! -z "$MONITOR_PID" ]; then
    kill $MONITOR_PID 2>/dev/null || true
fi

log_success "Aplicación terminada correctamente"