# Sistema de Backup Automatizado - Rexus.app

## 🎯 Descripción General

Sistema integral de backup automatizado diseñado específicamente para la aplicación Rexus.app. Proporciona respaldo completo y confiable de las **3 bases de datos críticas** del sistema:

- **`users`**: Autenticación, usuarios y permisos
- **`inventario`**: Datos principales de negocio (inventario, obras, pedidos, etc.)
- **`auditoria`**: Trazabilidad y registro de eventos críticos

## 🚀 Características Principales

### ✅ Funcionalidades Implementadas

- **Backup Completo Automatizado**: Respaldo de las 3 bases de datos + configuración + archivos críticos
- **Programación Automática**: Ejecución diaria programada (configurable)
- **Verificación de Integridad**: Checksums MD5 para validar backups
- **Compresión Inteligente**: Reducción de espacio con gzip
- **Rotación Automática**: Limpieza de backups antiguos (configurable)
- **Sistema de Restore**: Restauración completa desde cualquier backup
- **Logging Completo**: Trazabilidad de todas las operaciones
- **Interfaz Interactiva**: Menú fácil de usar
- **Manifiestos JSON**: Metadatos detallados de cada backup

### 🔧 Arquitectura del Sistema

```
tools/development/backup/
├── sistema_backup_automatizado.py    # Sistema principal
├── backup_config.json                # Configuración detallada  
├── ejecutar_backup.bat               # Script de ejecución Windows
└── README.md                          # Esta documentación

backups/                              # Directorio de backups (creado automáticamente)
├── databases/                        # Backups de bases de datos (.bak/.bak.gz)
├── config/                          # Archivos de configuración (.env, requirements.txt)
├── application/                     # Archivos críticos (core, utils, qss, docs)
├── logs/                           # Logs del sistema de backup
├── temp/                           # Archivos temporales
└── restore/                        # Espacio de trabajo para restauraciones
```

## 🛠️ Instalación y Configuración

### Prerrequisitos

1. **Python 3.8+** con las siguientes librerías:
   ```bash
   pip install pyodbc schedule python-dotenv
   ```

2. **SQL Server Command Line Tools** (`sqlcmd`):
   - Descargar desde: [Microsoft SQL Server Command Line Utilities](https://docs.microsoft.com/en-us/sql/tools/sqlcmd-utility)
   - Verificar instalación: `sqlcmd /?`

3. **Permisos de Base de Datos**:
   ```sql
   -- El usuario de la aplicación debe tener estos permisos:
   GRANT BACKUP DATABASE TO [rexus_user];
   GRANT RESTORE DATABASE TO [rexus_user];
   GRANT CREATE ANY DATABASE TO [rexus_user];  -- Solo para testing
   ```

4. **Variables de Entorno** configuradas en `.env`:
   ```env
   DB_SERVER=tu_servidor
   DB_USERNAME=tu_usuario
   DB_PASSWORD=tu_password
   DB_USERS=users
   DB_INVENTARIO=inventario
   DB_AUDITORIA=auditoria
   ```

### Configuración Inicial

1. **Verificar estructura del proyecto**:
   ```bash
   # Ejecutar desde la raíz del proyecto Rexus.app
   ls -la  # Debe mostrar directorios: rexus/, tools/, docs/, etc.
   ```

2. **Crear directorio de backups**:
   ```bash
   mkdir backups
   ```

3. **Probar conectividad**:
   ```bash
   python tools/development/backup/sistema_backup_automatizado.py
   # Seleccionar opción 1 para crear un backup de prueba
   ```

## 💻 Uso del Sistema

### Ejecución Interactiva

**En Windows**:
```cmd
tools\development\backup\ejecutar_backup.bat
```

**En Linux/Mac**:
```bash
cd /path/to/rexus.app
python tools/development/backup/sistema_backup_automatizado.py
```

### Menú Principal

```
🔧 Opciones disponibles:
1. 🚀 Crear backup completo ahora
2. 📅 Configurar backup automático
3. 📋 Listar backups disponibles
4. 🔄 Restaurar desde backup
5. 🏃 Ejecutar programador de backups
6. 🚪 Salir
```

### Casos de Uso Comunes

#### 1. Backup Manual Inmediato
```python
# Opción 1 del menú
# Crea backup completo con timestamp único
# Ejemplo: 20250806_143052
```

#### 2. Configurar Backup Automático
```python
# Opción 2 del menú
# Programa ejecución diaria a las 2:00 AM
# Para cambiar hora, editar BackupConfig.schedule_time
```

#### 3. Restaurar Sistema Completo
```python
# Opción 4 del menú
# Seleccionar backup por timestamp
# Confirmar restauración (⚠️ CUIDADO: Sobrescribe datos actuales)
```

## 📊 Estructura de Backups

### Archivos Generados

#### Backup de Bases de Datos
```
backups/databases/
├── users_20250806_143052.bak.gz        # Base de datos usuarios (comprimido)
├── inventario_20250806_143052.bak.gz   # Base de datos inventario (comprimido)  
└── auditoria_20250806_143052.bak.gz    # Base de datos auditoría (comprimido)
```

#### Backup de Configuración
```
backups/config/20250806_143052/
├── .env                                 # Variables de entorno
├── requirements.txt                     # Dependencias Python
├── CLAUDE.md                           # Instrucciones del proyecto
└── pyproject.toml                      # Configuración del proyecto
```

#### Backup de Aplicación
```
backups/application/20250806_143052/
├── rexus/core/                         # Núcleo de la aplicación
├── rexus/utils/                        # Utilidades compartidas
├── resources/qss/                      # Estilos de interfaz
├── docs/checklists/                    # Documentación crítica
└── scripts/sql/                        # Scripts SQL del sistema
```

#### Manifiestos y Logs
```
backups/
├── backup_manifest_20250806_143052.json  # Metadatos completos del backup
└── logs/
    └── backup_2025-08-06.log            # Log detallado de operaciones
```

### Ejemplo de Manifiesto JSON

```json
{
  "timestamp": "20250806_143052",
  "type": "full",
  "started_at": "2025-08-06T14:30:52.123456",
  "completed_at": "2025-08-06T14:35:18.987654",
  "status": "completed",
  "databases": {
    "users": {
      "status": "completed",
      "file": "C:\\...\\backups\\databases\\users_20250806_143052.bak.gz",
      "size_bytes": 1048576,
      "checksum": "a1b2c3d4e5f6...",
      "timestamp": "20250806_143052"
    }
    // ... más bases de datos
  },
  "config": {
    "status": "completed",
    "files": [
      {
        "source": "C:\\...\\Rexus.app\\.env",
        "backup": "C:\\...\\backups\\config\\20250806_143052\\.env",
        "size": 1024,
        "checksum": "f6e5d4c3b2a1..."
      }
      // ... más archivos
    ]
  },
  "integrity_check": [
    "✓ users: Integridad verificada",
    "✓ inventario: Integridad verificada", 
    "✓ auditoria: Integridad verificada"
  ]
}
```

## 🔒 Seguridad y Mejores Prácticas

### Seguridad de Backups

1. **Almacenamiento Seguro**:
   - Los backups contienen datos sensibles (usuarios, contraseñas hash, datos de negocio)
   - Considerar cifrado para backups en ubicaciones remotas
   - Restringir permisos de carpeta `backups/`

2. **Credenciales**:
   - Nunca incluir contraseñas en plain text en scripts
   - Usar variables de entorno (`.env`)
   - Rotar credenciales regularmente

3. **Acceso**:
   - Solo administradores deben tener acceso al sistema de backup
   - Auditar quien ejecuta backups y restauraciones
   - Logs detallados para trazabilidad

### Mejores Prácticas

1. **Frecuencia de Backup**:
   - **Producción**: Backup diario automático + backup manual antes de cambios críticos
   - **Desarrollo**: Backup semanal o antes de cambios grandes
   - **Testing**: Backup antes de ejecutar migration scripts

2. **Verificación**:
   - Probar restauración mensualmente en ambiente de testing
   - Verificar integridad de backups automáticamente
   - Monitorear espacio en disco

3. **Retención**:
   - **Diarios**: 30 días (por defecto)
   - **Semanales**: 12 semanas
   - **Mensuales**: 12 meses
   - **Anuales**: 5 años (para auditoría)

4. **Monitoreo**:
   - Revisar logs diariamente
   - Configurar alertas para fallos de backup
   - Dashboard de estado de backups

## 🚨 Procedimientos de Emergencia

### Escenario 1: Corrupción de Base de Datos

```bash
# 1. Detener aplicación Rexus.app
# 2. Identificar último backup válido
python tools/development/backup/sistema_backup_automatizado.py
# Opción 3: Listar backups disponibles

# 3. Restaurar desde backup
# Opción 4: Restaurar desde backup
# CUIDADO: Confirma que quieres sobrescribir datos actuales

# 4. Verificar integridad post-restauración
# 5. Reiniciar aplicación
```

### Escenario 2: Pérdida Completa del Servidor

```bash
# 1. Configurar nuevo servidor SQL Server
# 2. Restaurar variables de entorno (.env)
# 3. Ejecutar restauración completa
# 4. Verificar conectividad desde Rexus.app
# 5. Probar funcionalidades críticas
```

### Escenario 3: Backup Corrupto

```bash
# 1. Verificar integridad de otros backups
# Opción 3: Listar backups disponibles

# 2. Usar backup más reciente válido
# 3. Investigar causa de corrupción (espacio en disco, permisos, etc.)
# 4. Ajustar configuración para prevenir repetición
```

## 📈 Monitoreo y Mantenimiento

### Logs a Revisar Regularmente

1. **backup_YYYY-MM-DD.log**: Operaciones diarias
2. **Manifiestos JSON**: Metadatos de cada backup
3. **Sistema operativo**: Espacio en disco, permisos

### Métricas Importantes

- **Tiempo de backup**: Debe ser consistente (alertar si aumenta >50%)
- **Tamaño de backup**: Monitorear crecimiento de datos
- **Tasa de éxito**: Debe ser 100% en producción
- **Espacio disponible**: Mantener al menos 20GB libres

### Mantenimiento Periódico

#### Semanal
- Revisar logs de backups
- Verificar espacio en disco
- Probar restore en ambiente de desarrollo

#### Mensual
- Ejecutar limpieza profunda de archivos temporales
- Actualizar documentación si hay cambios
- Revisar configuración de retención

#### Trimestral
- Probar restore completo en ambiente de testing
- Actualizar procedimientos de emergencia
- Capacitar al equipo en procedimientos de backup

## ⚡ Optimización y Personalización

### Configuración Avanzada

Editar la clase `BackupConfig` en `sistema_backup_automatizado.py`:

```python
config = BackupConfig(
    backup_dir="backups",                # Directorio base
    max_backups=30,                      # Días de retención
    compress=True,                       # Compresión (recomendado)
    verify_integrity=True,               # Verificación (recomendado)
    schedule_time="02:00",               # Hora de backup automático
    email_notifications=False,          # Notificaciones por email
    encrypt_backups=False                # Cifrado (futuro)
)
```

### Personalización de Horarios

```python
# Múltiples horarios
schedule.every().day.at("02:00").do(backup_full)
schedule.every().monday.at("01:00").do(backup_verify)
schedule.every().first_monday.at("00:00").do(backup_cleanup_deep)
```

### Integración con Sistemas Externos

```python
# Ejemplo: Copiar backups a almacenamiento en la nube
def upload_to_cloud(backup_files):
    # Implementar subida a AWS S3, Azure Blob, etc.
    pass

# Ejemplo: Notificaciones Slack/Teams
def send_backup_notification(status, details):
    # Implementar webhook a Slack/Teams
    pass
```

## 🐛 Solución de Problemas

### Errores Comunes

#### 1. "sqlcmd no encontrado"
```bash
# Instalar SQL Server Command Line Tools
# Windows: Descargar desde Microsoft
# Linux: sudo apt-get install mssql-tools
```

#### 2. "Error de conexión a base de datos"
```bash
# Verificar variables de entorno
echo $DB_SERVER $DB_USERNAME $DB_PASSWORD

# Probar conexión manual
sqlcmd -S $DB_SERVER -U $DB_USERNAME -P $DB_PASSWORD -Q "SELECT @@VERSION"
```

#### 3. "Espacio insuficiente"
```bash
# Verificar espacio disponible
df -h

# Limpiar backups antiguos manualmente
python sistema_backup_automatizado.py
# Ajustar max_backups en configuración
```

#### 4. "Permisos insuficientes"
```sql
-- Otorgar permisos necesarios
GRANT BACKUP DATABASE TO [tu_usuario];
GRANT RESTORE DATABASE TO [tu_usuario];
```

### Debugging

Activar logging detallado:

```python
# En sistema_backup_automatizado.py
logger.setLevel(logging.DEBUG)

# Ver logs en tiempo real
tail -f backups/logs/backup_$(date +%Y-%m-%d).log
```

## 📚 Referencias Adicionales

- [Documentación oficial SQL Server BACKUP](https://docs.microsoft.com/en-us/sql/t-sql/statements/backup-transact-sql)
- [Buenas prácticas de backup SQL Server](https://docs.microsoft.com/en-us/sql/relational-databases/backup-restore/backup-overview-sql-server)
- [Guía de recuperación ante desastres](https://docs.microsoft.com/en-us/sql/relational-databases/backup-restore/restore-and-recovery-overview-sql-server)

## 🤝 Soporte

Para reportar problemas o solicitar mejoras:

1. **Issues del proyecto**: Crear ticket en el repositorio
2. **Logs**: Incluir siempre logs relevantes (`backups/logs/`)
3. **Configuración**: Incluir configuración sanitizada (sin contraseñas)

---

**© 2025 Rexus.app - Sistema de Backup Automatizado v1.0**