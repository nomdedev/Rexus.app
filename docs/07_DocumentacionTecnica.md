# 📚 DOCUMENTACIÓN TÉCNICA - REXUS.APP

## 🏗️ Arquitectura del Sistema

### Estructura General
Rexus.app sigue una arquitectura modular basada en componentes, implementando el patrón MVC (Model-View-Controller) con capas adicionales de seguridad y optimización.

```
rexus/
├── core/                    # Núcleo del sistema
│   ├── auth_manager.py      # Gestión de autenticación y autorización
│   └── __init__.py
├── utils/                   # Utilidades del sistema
│   ├── security.py          # Funciones de seguridad
│   ├── logging_config.py    # Configuración de logging
│   ├── error_handler.py     # Manejo centralizado de errores
│   ├── performance_monitor.py # Monitoreo de rendimiento
│   ├── database_manager.py  # Gestión de base de datos
│   ├── intelligent_cache.py # Sistema de cache inteligente
│   ├── lazy_loader.py       # Carga bajo demanda
│   ├── backup_compressor.py # Compresión de backups
│   └── optimization_manager.py # Gestor de optimizaciones
├── modules/                 # Módulos funcionales
│   ├── administracion/      # Módulo de administración
│   ├── auditoria/          # Módulo de auditoría
│   ├── compras/            # Módulo de compras
│   ├── configuracion/      # Módulo de configuración
│   ├── herrajes/           # Módulo de herrajes
│   ├── inventario/         # Módulo de inventario
│   ├── logistica/          # Módulo de logística
│   ├── mantenimiento/      # Módulo de mantenimiento
│   ├── obras/              # Módulo de obras
│   ├── pedidos/            # Módulo de pedidos
│   ├── usuarios/           # Módulo de usuarios
│   └── vidrios/            # Módulo de vidrios
```

## 🔒 Seguridad

### Sistema de Autenticación
- **Hash de contraseñas**: PBKDF2 con salt aleatorio
- **Validación de entrada**: Sanitización automática anti-XSS
- **Prevención SQL Injection**: Prepared statements y validación

### Roles y Permisos
```python
from rexus.core.auth_manager import AuthManager, UserRole, Permission

# Verificar permisos
if AuthManager.check_permission(Permission.VIEW_DASHBOARD):
    # Usuario tiene permisos
    pass
```

### Funciones de Seguridad
```python
from rexus.utils.security import SecurityUtils

# Hash de contraseña
hashed = SecurityUtils.hash_password("mi_contraseña")

# Verificar contraseña
is_valid = SecurityUtils.verify_password("mi_contraseña", hashed)

# Sanitizar entrada
clean_input = SecurityUtils.sanitize_input(user_input)
```

## 📊 Sistema de Logging

### Configuración
```python
from rexus.utils.logging_config import get_logger, log_user_action

# Obtener logger
logger = get_logger('mi_modulo')

# Logging de acción de usuario
log_user_action("login", "usuario123", "Inicio de sesión exitoso")
```

### Tipos de Logs
- **main.log**: Eventos generales de la aplicación
- **security.log**: Eventos de seguridad y autenticación
- **error.log**: Errores y excepciones
- **audit.log**: Auditoría de acciones de usuario

## 🛡️ Manejo de Errores

### Decorador de Protección
```python
from rexus.utils.error_handler import error_boundary, safe_execute

@error_boundary
def mi_funcion_critica():
    # Código que puede fallar
    return resultado

# Ejecución segura
resultado = safe_execute(funcion_riesgosa, default_return="valor_por_defecto")
```

## ⚡ Sistema de Caché

### Cache Inteligente
```python
from rexus.utils.intelligent_cache import cached_query, invalidate_cache

@cached_query(ttl=300)  # Cache por 5 minutos
def consulta_pesada(parametro):
    # Consulta que se cachea automáticamente
    return resultado

# Invalidar cache
invalidate_cache("pattern_*")
```

## 🔄 Carga Bajo Demanda

### Lazy Loading
```python
from rexus.utils.lazy_loader import lazy_import, preload_essential_modules

@lazy_import("modulo.pesado")
def usar_modulo_pesado(modulo, *args):
    return modulo.funcion_costosa(*args)

# Precargar módulos esenciales
preload_essential_modules()
```

## 📊 Monitoreo de Rendimiento

### Monitor en Tiempo Real
```python
from rexus.utils.performance_monitor import performance_timer, PerformanceMonitor

@performance_timer
def funcion_a_monitorear():
    # Función monitoreada automáticamente
    return resultado

# Obtener métricas
monitor = PerformanceMonitor()
stats = monitor.get_system_stats()
```

## 💾 Gestión de Base de Datos

### Pool de Conexiones
```python
from rexus.utils.database_manager import DatabaseManager

# Obtener conexión del pool
with DatabaseManager.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tabla")
    resultados = cursor.fetchall()
```

## 🗜️ Compresión de Backups

### Sistema Automático
```python
from rexus.utils.backup_compressor import compress_backup, auto_compress_logs

# Comprimir backup manual
resultado = compress_backup("archivo.backup")

# Compresión automática de logs antiguos
comprimidos = auto_compress_logs(age_days=7)
```

## 🎛️ Gestión de Optimizaciones

### Manager Central
```python
from rexus.utils.optimization_manager import initialize_optimizations, get_optimization_report

# Inicializar todos los sistemas de optimización
initialize_optimizations()

# Obtener reporte de rendimiento
reporte = get_optimization_report()
```

## 🔧 Configuración

### Variables de Entorno (.env)
```env
# Configuración de base de datos
DB_PATH=rexus_production.db
DB_BACKUP_INTERVAL=3600

# Configuración de logging
LOG_LEVEL=INFO
LOG_ROTATION_SIZE=10MB

# Configuración de cache
CACHE_DEFAULT_TTL=300
CACHE_MAX_SIZE=1000

# Configuración de seguridad
SECURITY_HASH_ROUNDS=100000
SESSION_TIMEOUT=1800
```

### Configuración JSON (config/rexus_config.json)
```json
{
    "app": {
        "name": "Rexus.app",
        "version": "2.0.0",
        "debug": false
    },
    "security": {
        "enable_xss_protection": true,
        "enable_sql_injection_protection": true,
        "enable_audit_logging": true
    },
    "performance": {
        "enable_cache": true,
        "enable_lazy_loading": true,
        "enable_compression": true
    }
}
```

## 🧪 Testing

### Ejecutar Tests
```bash
# Tests de seguridad
python tools/security/validate_security_fixes.py

# Tests de rendimiento
python tools/testing/performance_validation.py

# Preparación para producción
python tools/deployment/prepare_production.py
```

### Estructura de Tests
```
tests/
├── test_security.py        # Tests de seguridad
├── test_performance.py     # Tests de rendimiento
├── test_database.py        # Tests de base de datos
└── test_integration.py     # Tests de integración
```

## 🚀 Despliegue

### Preparación
1. Instalar dependencias: `pip install -r requirements_updated.txt`
2. Configurar variables de entorno
3. Ejecutar validaciones: `python tools/deployment/prepare_production.py`
4. Verificar configuración: `python -c "from rexus.utils.security import SecurityUtils; print('OK')"`

### Producción
```bash
# Inicializar optimizaciones
python -c "from rexus.utils.optimization_manager import initialize_optimizations; initialize_optimizations()"

# Ejecutar aplicación
python run.py
```

## 📝 Convenciones de Código

### Estilo
- PEP 8 compliance
- Type hints obligatorios para funciones públicas
- Docstrings en formato Google Style
- Manejo de errores explícito

### Ejemplo de Función
```python
def procesar_datos(datos: List[Dict[str, Any]], filtro: Optional[str] = None) -> List[Dict[str, Any]]:
    """Procesa una lista de datos aplicando filtros opcionales.
    
    Args:
        datos: Lista de diccionarios con los datos a procesar
        filtro: Filtro opcional a aplicar
        
    Returns:
        Lista de datos procesados
        
    Raises:
        ValueError: Si los datos están vacíos
        TypeError: Si el formato de datos es incorrecto
    """
    if not datos:
        raise ValueError("Los datos no pueden estar vacíos")
    
    # Procesar datos...
    return datos_procesados
```

## 🔍 Debugging

### Logs de Debug
```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Información de debug")
logger.info("Información general")
logger.warning("Advertencia")
logger.error("Error")
logger.critical("Error crítico")
```

### Profiling
```python
from rexus.utils.performance_monitor import performance_timer

@performance_timer
def funcion_a_optimizar():
    # Función que se va a perfilar
    pass
```

## 📈 Métricas y Monitoreo

### Métricas Disponibles
- Tiempo de respuesta de funciones
- Uso de CPU y memoria
- Hit ratio del cache
- Tasa de errores
- Tiempo de carga de módulos

### Dashboard de Métricas
```python
from rexus.utils.optimization_manager import get_optimization_report

# Obtener reporte completo
reporte = get_optimization_report()
print(f"Cache hit ratio: {reporte['cache_system']['hit_ratio']:.2%}")
print(f"Módulos cargados: {reporte['lazy_loading']['loaded_modules']}")
```

---

*Documentación técnica generada para Rexus.app v2.0*
