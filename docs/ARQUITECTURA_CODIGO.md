# Arquitectura y Organización del Código - Rexus.app

## Estructura General del Proyecto

```
Rexus.app/
├── run.py                  # 🚀 Punto de entrada principal UNIFICADO
├── demo_app.py            # 🔧 Aplicación demo/fallback
├── requirements.txt       # 📦 Dependencias
│
├── src/                   # 📁 Código fuente principal
│   ├── main/             # 🎯 Aplicación principal
│   │   └── app.py        # MainWindow y lógica principal
│   ├── core/             # ⚙️ Funcionalidades core
│   │   ├── config.py     # Configuración
│   │   ├── database.py   # Conexiones BD
│   │   ├── security.py   # Sistema de seguridad
│   │   └── login_dialog.py # Diálogo de autenticación
│   ├── modules/          # 📋 Módulos de negocio
│   │   ├── inventario/   # Gestión de inventario
│   │   ├── contabilidad/ # Gestión financiera
│   │   ├── obras/        # Gestión de proyectos
│   │   ├── pedidos/      # Gestión de pedidos
│   │   ├── logistica/    # Gestión logística
│   │   ├── herrajes/     # Catálogo herrajes
│   │   ├── vidrios/      # Catálogo vidrios
│   │   ├── compras/      # Gestión compras
│   │   ├── mantenimiento/ # Mantenimiento
│   │   ├── usuarios/     # Gestión usuarios
│   │   ├── auditoria/    # Logs y auditoría
│   │   └── configuracion/ # Configuración sistema
│   ├── utils/            # 🛠️ Utilidades
│   └── widgets/          # 🎨 Widgets personalizados
│
├── tests/                # 🧪 Pruebas organizadas por módulo
├── docs/                 # 📚 Documentación técnica
├── config/               # ⚙️ Archivos de configuración
├── logs/                 # 📝 Archivos de log
├── resources/            # 🎨 Recursos (iconos, estilos)
├── scripts/              # 🔧 Scripts de utilidad
└── static/               # 📄 Archivos estáticos
```

## Principios de Arquitectura

### 1. Patrón MVC (Model-View-Controller)
Cada módulo sigue estrictamente el patrón MVC:

```python
# Estructura de cada módulo
module_name/
├── __init__.py
├── model.py       # Lógica de datos y BD
├── view.py        # Interfaz de usuario
└── controller.py  # Lógica de negocio y coordinación
```

### 2. Factory Pattern
La clase `MainWindow` usa Factory Pattern para crear módulos:

```python
def _create_module_widget(self, module_name: str) -> QWidget:
    """Factory method para crear widgets de módulos"""
    module_factory = {
        "Inventario": self._create_inventario_module,
        "Contabilidad": self._create_contabilidad_module,
        # ... más módulos
    }
    
    creation_method = module_factory.get(module_name)
    return creation_method() if creation_method else self._create_fallback_module(module_name)
```

### 3. Dependency Injection
Los controladores reciben sus dependencias al ser creados:

```python
# En cada módulo
model = ModuleModel(db_connection)
view = ModuleView()
controller = ModuleController(model, view)
```

### 4. Sistema de Fallback
Cada módulo tiene un sistema robusto de fallback:

```python
try:
    # Intentar crear módulo real
    return real_module()
except Exception:
    # Fallback a módulo demo/placeholder
    return self._create_fallback_module(module_name)
```

## Convenciones de Código

### 1. Nomenclatura
- **Métodos privados**: Prefijo `_` (ej: `_create_module`)
- **Métodos públicos**: Sin prefijo (ej: `show_module`)
- **Constantes**: MAYÚSCULAS (ej: `DB_CONNECTION_TIMEOUT`)
- **Clases**: PascalCase (ej: `MainWindow`)
- **Variables**: snake_case (ej: `user_data`)

### 2. Type Hints
Usar type hints en todos los métodos públicos:

```python
def show_module(self, module_name: str) -> None:
    """Docstring descriptivo"""
    pass

def _create_widget(self, title: str, data: Dict[str, Any]) -> QWidget:
    """Docstring descriptivo"""
    pass
```

### 3. Documentación
- **Docstrings**: Para todas las clases y métodos públicos
- **Comentarios inline**: Solo cuando la lógica no es obvia
- **Documentación técnica**: En carpeta `docs/`

### 4. Gestión de Errores
```python
try:
    # Operación principal
    result = risky_operation()
except SpecificException as e:
    # Log específico
    print(f"Error específico: {e}")
    # Fallback o recovery
    result = fallback_operation()
except Exception as e:
    # Log general
    print(f"Error inesperado: {e}")
    # Graceful degradation
    return default_value
```

## Flujo de Datos

### 1. Inicialización
```
run.py → src/main/app.py → LoginDialog → MainWindow → Módulos
```

### 2. Navegación de Módulos
```
User Click → show_module() → _create_module_widget() → Factory → MVC Module
```

### 3. Gestión de Estado
- **Usuario actual**: Almacenado en `MainWindow.user_data`
- **Permisos**: Manejados por `SecurityManager`
- **Sesión**: Controlada por sistema de autenticación

## Patrones de Diseño Implementados

### 1. Singleton
- `SecurityManager`: Una instancia por aplicación
- `DatabaseConnection`: Pool de conexiones

### 2. Observer
- Señales PyQt6 para comunicación entre componentes
- Event-driven architecture para actualizaciones de UI

### 3. Command Pattern
- Acciones de usuario encapsuladas en comandos
- Facilita undo/redo y logging

### 4. Strategy Pattern
- Diferentes estrategias de conexión BD
- Múltiples temas/estilos intercambiables

## Reglas de Desarrollo

### ✅ Hacer
1. **Seguir la estructura MVC** en todos los módulos
2. **Usar type hints** en métodos públicos
3. **Implementar fallbacks** para operaciones críticas
4. **Documentar APIs públicas** con docstrings
5. **Mantener métodos pequeños** (<50 líneas)
6. **Usar factory pattern** para creación de objetos complejos
7. **Separar lógica de UI** de lógica de negocio

### ❌ No Hacer
1. **No crear archivos en raíz** sin justificación
2. **No duplicar código** entre módulos
3. **No hardcodear rutas** o configuraciones
4. **No mezclar lógica de BD** con UI
5. **No crear tests de un solo uso** en raíz
6. **No importar módulos específicos** en core
7. **No violar encapsulación** accediendo a `_private_methods`

## Herramientas de Calidad

### 1. Linting
```bash
# En development
pylint src/
black src/
isort src/
```

### 2. Testing
```bash
# Tests organizados por módulo
pytest tests/module_name/
pytest tests/integration/
```

### 3. Documentación
```bash
# Generar docs
sphinx-build docs/ docs/_build/
```

## Versionado y Releases

### Semantic Versioning
- **MAJOR**: Cambios incompatibles de API
- **MINOR**: Nueva funcionalidad compatible
- **PATCH**: Bug fixes compatibles

### Release Process
1. Update version en `__init__.py`
2. Update CHANGELOG.md
3. Run full test suite
4. Create release tag
5. Deploy documentation

---

**Mantenido por:** Equipo de Desarrollo Rexus  
**Última actualización:** 2025-01-15  
**Versión documento:** 1.0.0