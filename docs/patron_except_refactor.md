# Patrón para Refactorizar `except Exception`

## Estado: EN PROGRESO (2/140+ casos completados)

### Patrón Implementado

Reemplazar `except Exception` genérico por manejo específico de excepciones:

```python
# ANTES:
try:
    operacion_bd()
except Exception as e:
    logger.error(f"Error: {e}")

# DESPUÉS:
try:
    operacion_bd()
except (DatabaseError, sqlite3.Error) as e:
    logger.error(f"Error de base de datos: {e}", exc_info=True)
except (ConnectionError, TimeoutError) as e:
    logger.error(f"Error de conexión: {e}", exc_info=True)
except Exception as e:
    logger.error(f"Error inesperado: {e}", exc_info=True)
```

### Casos Críticos por Tipo

#### Base de Datos
- `DatabaseError, sqlite3.Error` - Errores de BD
- `ConnectionError` - Problemas de conexión
- `IntegrityError` - Violaciones de integridad

#### Seguridad
- `ValueError` - Datos de entrada inválidos
- `PermissionError` - Problemas de permisos
- `AuthenticationError` - Fallos de autenticación

#### UI/Sistema
- `AttributeError` - Problemas de objeto/método
- `FileNotFoundError` - Archivos faltantes
- `ImportError` - Problemas de importación

### Archivos por Priorizar

1. **controller.py** - 19 casos (🔄 2/19 completados)
2. **model.py** - 30+ casos  
3. **security_features.py** - 3 casos
4. **view.py** - 4 casos
5. **submodules/** - 90+ casos

### Próximos Pasos

1. Completar casos críticos en archivos principales
2. Implementar en submódulos (auth, sessions, permissions)
3. Validar que el manejo específico funciona correctamente
4. Crear tests para cada tipo de excepción

### Importaciones Necesarias

```python
import sqlite3
from sqlite3 import DatabaseError, IntegrityError
from PyQt6.QtCore import QException  # Para errores de Qt
```

### Notas

- Mantener `except Exception` como último catch para casos no previstos
- Siempre usar `exc_info=True` para logging detallado
- Priorizar casos de seguridad y base de datos