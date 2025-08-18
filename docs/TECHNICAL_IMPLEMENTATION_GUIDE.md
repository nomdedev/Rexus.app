# Technical Implementation Guide - Rexus.app v2.0.0

**Target Audience:** Developers, Technical Teams, System Architects  
**Date:** August 18, 2025  
**Version:** 2.0.0 Production Ready

## 🔧 Technical Stack & Architecture

### Core Technologies
- **Language:** Python 3.10+
- **GUI Framework:** PyQt6
- **Database:** Microsoft SQL Server (ODBC 17)
- **Architecture Pattern:** MVC (Model-View-Controller)
- **Package Manager:** pip
- **Testing:** pytest (recommended)

### Dependencies
```txt
# Core Requirements
PyQt6>=6.5.0
pyodbc>=4.0.39
bcrypt>=4.0.1
requests>=2.31.0
python-dateutil>=2.8.2

# Optional (Performance)
psutil>=5.9.0
cachetools>=5.3.0
```

---

## 🏗️ System Architecture

### Directory Structure (Production)
```
rexus.app/
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── CLAUDE.md                       # Master configuration guide
├── rexus/                          # Core application package
│   ├── __init__.py
│   ├── core/                       # Core system components
│   │   ├── database.py             # Database connection management
│   │   └── app_config.py           # Application configuration
│   ├── utils/                      # Utility modules
│   │   ├── app_logger.py           # Centralized logging
│   │   ├── cache_manager.py        # Cache management
│   │   ├── sql_query_manager.py    # External SQL file management
│   │   ├── security.py             # Security utilities
│   │   ├── performance_monitor.py  # Performance monitoring
│   │   └── error_recovery.py       # Error recovery system
│   ├── modules/                    # Business logic modules
│   │   ├── herrajes/               # Hardware module
│   │   ├── vidrios/                # Glass module
│   │   ├── usuarios/               # User management
│   │   ├── compras/                # Purchase management
│   │   ├── pedidos/                # Order management
│   │   └── administracion/         # Administration
│   ├── ui/                         # User interface components
│   │   ├── templates/              # UI templates
│   │   └── standard_components.py  # Reusable UI components
│   └── main/                       # Main application logic
├── sql/                            # External SQL scripts
│   ├── common/                     # Shared SQL utilities
│   ├── herrajes/                   # Hardware-specific queries
│   ├── vidrios/                    # Glass-specific queries
│   ├── usuarios/                   # User management queries
│   └── [other_modules]/
├── tests/                          # Test suite
├── docs/                           # Documentation
├── examples/                       # Usage examples
└── scripts/                        # Utility scripts
```

---

## 🔌 Database Integration

### Connection Management
```python
# rexus/core/database.py
from rexus.core.database import get_inventario_connection, get_users_connection

# Business data connection
inv_conn = get_inventario_connection()

# User management connection  
users_conn = get_users_connection()

# Connection validation
if inv_conn and hasattr(inv_conn, 'connection') and inv_conn.connection:
    # Connection is valid and ready
    cursor = inv_conn.cursor()
```

### SQL Query Management
```python
# Using SQLQueryManager for external SQL files
from rexus.utils.sql_query_manager import SQLQueryManager

sql_manager = SQLQueryManager()

# Load external SQL query
query = sql_manager.get_query('usuarios', 'obtener_usuario_por_id')

# Execute with parameters
cursor.execute(query, (user_id,))
```

---

## 📝 Logging Implementation

### Standard Logging Pattern
```python
from rexus.utils.app_logger import get_logger

class ExampleModule:
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
    
    def example_operation(self):
        try:
            self.logger.info("Starting operation")
            # Business logic here
            self.logger.info("Operation completed successfully")
            return result
        except ValueError as e:
            self.logger.error(f"Validation error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise
```

### Log Levels & Usage
```python
logger.debug("Detailed diagnostic information")      # Development only
logger.info("General operational messages")          # Normal flow
logger.warning("Warning conditions")                 # Potential issues
logger.error("Error conditions")                     # Recoverable errors
logger.critical("Critical error conditions")         # System failures
```

---

## ⚡ Performance Monitoring

### SQL Query Performance
```python
from rexus.utils.performance_monitor import sql_performance_monitor

@sql_performance_monitor('obtener_lista_productos')
def obtener_productos(self, filtros=None):
    # This function will be automatically monitored
    # Slow queries (>1s) will generate warnings
    return self.sql_manager.execute_query(...)

# Get performance reports
from rexus.utils.performance_monitor import performance_monitor
report = performance_monitor.get_optimization_report()
```

### General Performance Monitoring
```python
from rexus.utils.performance_monitor import performance_timer

@performance_timer
def expensive_operation():
    # Operations >1s will be logged as slow
    pass
```

---

## 🛡️ Error Recovery System

### Database Operations
```python
from rexus.utils.error_recovery import database_operation_recovery

class UsuariosModel:
    @database_operation_recovery('obtener_usuario')
    def obtener_usuario(self, user_id):
        # Automatic retry + cache + offline fallback
        # Connection repair if database issues
        # Returns cached data as fallback
        pass
```

### Custom Recovery Configuration
```python
from rexus.utils.error_recovery import get_error_recovery_manager, RecoveryConfig

# Custom configuration for critical operations
config = RecoveryConfig(
    max_retries=5,
    base_delay=2.0,
    enable_cache=True,
    cache_duration=600,  # 10 minutes
    enable_offline_mode=True
)

recovery_manager = get_error_recovery_manager()

@recovery_manager.with_recovery(config, 'critical_operation')
def critical_business_operation():
    # High-reliability operation with extended retry policy
    pass
```

---

## 🎨 UI Component Implementation

### Base Module View Pattern
```python
from rexus.ui.templates.base_module_view import BaseModuleView
from rexus.ui.standard_components import StandardComponents

class ModuloView(BaseModuleView):
    def __init__(self):
        super().__init__()
        self.module_name = "mi_modulo"  # Always set this
        self.setup_ui()
        self.apply_theme()  # REQUIRED for consistent styling
    
    def setup_ui(self):
        # Use standard components for consistency
        self.main_table = StandardComponents.create_table(
            columns=self.get_column_definitions(),
            enable_sorting=True
        )
        
        self.control_panel = StandardComponents.create_control_panel()
        self.stats_panel = StandardComponents.create_stats_panel()
```

### Standard Component Usage
```python
# Create consistent UI elements
table = StandardComponents.create_table(
    columns=[
        {'name': 'id', 'label': 'ID', 'width': 80},
        {'name': 'nombre', 'label': 'Nombre', 'width': 200},
    ],
    enable_sorting=True,
    enable_filtering=True
)

buttons = StandardComponents.create_button_panel([
    ('Nuevo', 'primary'),
    ('Editar', 'secondary'),
    ('Eliminar', 'danger')
])
```

---

## 💾 MVC Pattern Implementation

### Model Layer (Data & Business Logic)
```python
# rexus/modules/ejemplo/model.py
from rexus.utils.app_logger import get_logger
from rexus.utils.sql_query_manager import SQLQueryManager
from rexus.core.database import get_inventario_connection

class EjemploModel:
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self.sql_manager = SQLQueryManager()
        self.db_connection = get_inventario_connection()
    
    def obtener_datos(self, filtros=None):
        """Business logic only - no UI concerns"""
        try:
            query = self.sql_manager.get_query('ejemplo', 'obtener_datos')
            cursor = self.db_connection.cursor()
            cursor.execute(query, filtros or {})
            return cursor.fetchall()
        except Exception as e:
            self.logger.error(f"Error obtaining data: {e}")
            raise
```

### View Layer (User Interface)
```python
# rexus/modules/ejemplo/view.py
from rexus.ui.templates.base_module_view import BaseModuleView
from PyQt6.QtCore import pyqtSignal

class EjemploView(BaseModuleView):
    # Signals for controller communication
    obtener_datos_signal = pyqtSignal(dict)
    crear_registro_signal = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.module_name = "ejemplo"
        self.setup_ui()
        self.apply_theme()
    
    def actualizar_tabla_datos(self, datos):
        """Update UI with data from controller"""
        # UI updates only - no business logic
        pass
```

### Controller Layer (Coordination)
```python
# rexus/modules/ejemplo/controller.py
from PyQt6.QtCore import QObject

class EjemploController(QObject):
    def __init__(self, model=None, view=None):
        super().__init__()
        self.model = model
        self.view = view
        self.conectar_senales()
    
    def conectar_senales(self):
        if self.view:
            self.view.obtener_datos_signal.connect(self.cargar_datos)
    
    def cargar_datos(self, filtros=None):
        """Coordinate between model and view"""
        try:
            datos = self.model.obtener_datos(filtros)
            if self.view:
                self.view.actualizar_tabla_datos(datos)
        except Exception as e:
            if self.view:
                self.view.mostrar_error(f"Error loading data: {e}")
```

---

## 🔐 Security Implementation

### Input Sanitization
```python
from rexus.utils.unified_sanitizer import sanitize_string

# Always sanitize user input
username_clean = sanitize_string(username, max_length=50)
```

### SQL Injection Prevention
```python
# ✅ GOOD: Parameterized queries
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

# ❌ BAD: String concatenation
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

### Authentication Pattern
```python
from rexus.modules.usuarios.submodules.auth_manager import AuthenticationManager

auth_manager = AuthenticationManager()
result = auth_manager.autenticar_usuario_seguro(username, password)

if result['success']:
    user_data = result['user_data']
    # Proceed with authenticated user
else:
    # Handle authentication failure
    if result['bloqueado']:
        # Account locked due to failed attempts
        pass
```

---

## 🧪 Testing Patterns

### Unit Test Example
```python
# tests/test_example_module.py
import pytest
from rexus.modules.ejemplo.model import EjemploModel

class TestEjemploModel:
    @pytest.fixture
    def model(self):
        return EjemploModel()
    
    def test_obtener_datos(self, model):
        """Test data retrieval functionality"""
        result = model.obtener_datos({'activo': True})
        assert isinstance(result, list)
        assert len(result) >= 0
    
    def test_crear_registro(self, model):
        """Test record creation"""
        datos_test = {'nombre': 'Test', 'descripcion': 'Test record'}
        result = model.crear_registro(datos_test)
        assert result is not None
```

### Integration Test Example
```python
def test_module_integration():
    """Test complete MVC integration"""
    from rexus.modules.ejemplo.model import EjemploModel
    from rexus.modules.ejemplo.controller import EjemploController
    
    model = EjemploModel()
    controller = EjemploController(model=model)
    
    # Test controller-model interaction
    controller.cargar_datos({'activo': True})
    # Assertions here
```

---

## 🚀 Deployment Considerations

### Production Configuration
```python
# Environment-specific settings
PRODUCTION_CONFIG = {
    'DEBUG': False,
    'LOG_LEVEL': 'INFO',
    'CACHE_DURATION': 3600,
    'MAX_RETRIES': 5,
    'CONNECTION_TIMEOUT': 30,
    'ENABLE_PERFORMANCE_MONITORING': True
}
```

### Resource Optimization
```python
# Memory management
from rexus.utils.cache_manager import get_cache_manager

cache = get_cache_manager()
cache.set_size_limit(100)  # Limit cache entries

# Connection pooling
from rexus.core.database import set_connection_pool_size
set_connection_pool_size(10)  # Max 10 concurrent connections
```

### Health Checks
```python
def system_health_check():
    """Comprehensive system health verification"""
    health_status = {
        'database': check_database_connectivity(),
        'cache': check_cache_availability(),
        'performance': check_performance_metrics(),
        'error_recovery': check_recovery_system()
    }
    return all(health_status.values())
```

---

## 📊 Monitoring & Analytics

### Performance Metrics Collection
```python
from rexus.utils.performance_monitor import performance_monitor

# Get comprehensive performance report
report = performance_monitor.get_optimization_report()

metrics = {
    'sql_performance': report['sql_performance'],
    'cache_hit_rate': report['cache_performance']['hit_rate'],
    'slow_operations': len(report['slow_operations']),
    'recommendations': report['recommendations']
}
```

### Error Analytics
```python
from rexus.utils.error_recovery import get_error_recovery_manager

recovery_manager = get_error_recovery_manager()
stats = recovery_manager.get_recovery_statistics()

error_analytics = {
    'total_errors': stats['total_errors'],
    'recovery_success_rate': stats['success_rate'],
    'most_common_errors': stats['most_common_errors'],
    'avg_recovery_time': stats['avg_recovery_time']
}
```

---

## 🔄 Migration Guidelines

### From Legacy Code
1. **Update Imports:**
   ```python
   # Old
   from legacy_root.utils import something
   
   # New  
   from rexus.utils import something
   ```

2. **Migrate Hardcoded SQL:**
   ```python
   # Old
   query = "SELECT * FROM table WHERE condition"
   
   # New
   query = self.sql_manager.get_query('module', 'query_name')
   ```

3. **Add Error Recovery:**
   ```python
   # Wrap existing functions
   @with_error_recovery('operation_name')
   def existing_function():
       # Existing code here
       pass
   ```

### Database Schema Updates
```sql
-- Create recovery tracking table
CREATE TABLE recovery_log (
    id INT IDENTITY(1,1) PRIMARY KEY,
    operation_name NVARCHAR(100),
    error_type NVARCHAR(50),
    success BIT,
    timestamp DATETIME DEFAULT GETDATE()
);
```

---

## 🎯 Best Practices Summary

### Code Quality
- ✅ **Always use parameterized SQL queries**
- ✅ **Implement proper exception hierarchy (specific → general)**
- ✅ **Use centralized logging with get_logger()**
- ✅ **Apply error recovery decorators to critical operations**
- ✅ **Follow MVC pattern strictly (no business logic in views)**

### Performance
- ✅ **Monitor SQL query performance with decorators**
- ✅ **Implement caching for frequently accessed data**  
- ✅ **Use connection pooling for database operations**
- ✅ **Profile and optimize slow operations (>1s)**

### Security  
- ✅ **Sanitize all user inputs**
- ✅ **Use secure password hashing (bcrypt)**
- ✅ **Implement rate limiting for authentication attempts**
- ✅ **Validate database connections before operations**

### Maintainability
- ✅ **External SQL files for all queries**
- ✅ **Comprehensive error recovery mechanisms**
- ✅ **Consistent UI components across modules**
- ✅ **Automated testing for all critical paths**

---

## 📞 Support & Resources

### Documentation Links
- **Master Guide:** `CLAUDE.md`
- **Fixes Documentation:** `docs/FIXES_COMPREHENSIVE_GUIDE.md`
- **Usage Examples:** `examples/`
- **API Reference:** Auto-generated from docstrings

### Development Tools
- **Testing:** `python -m pytest tests/`
- **Performance Analysis:** Check `performance_monitor.get_optimization_report()`
- **Error Analysis:** Review `error_recovery_manager.get_recovery_statistics()`

### Contact Information
- **Technical Lead:** Rexus Development Team
- **Documentation:** In-code docstrings + `/docs` directory  
- **Issues:** Log through application error recovery system

---

**📅 Document Version:** 2.0.0  
**📅 Last Updated:** August 18, 2025  
**✅ Status:** PRODUCTION READY