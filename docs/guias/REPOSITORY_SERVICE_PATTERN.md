# Repository Pattern + Service Layer

## 📚 Arquitectura de Acceso a Datos y Lógica de Negocio

Este documento describe la arquitectura **Repository Pattern + Service Layer** implementada en Rexus.app para separar responsabilidades y mejorar la mantenibilidad.

---

## 🎯 Objetivos

### Problema Resuelto
Antes de esta implementación, los modelos de Rexus.app tenían:
- ❌ Lógica de negocio mezclada con acceso a datos
- ❌ Código difícil de testear (acoplado a BD)
- ❌ Duplicación de consultas SQL
- ❌ Dificultad para cambiar de ORM/BD

### Solución Implementada
Con Repository Pattern + Service Layer:
- ✅ **Separación clara**: Repositories manejan datos, Services manejan lógica
- ✅ **Testabilidad**: Mock fácil de repositories y services
- ✅ **Reutilización**: Consultas centralizadas en repositories
- ✅ **Flexibilidad**: Cambiar infraestructura sin afectar negocio

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                        UI Layer                              │
│                    (Controllers/Views)                       │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Service Layer                             │
│              (Lógica de Negocio)                             │
│  - Validaciones                                             │
│  - Reglas de negocio                                        │
│  - Coordinación entre repos                                 │
│  - Manejo de transacciones                                  │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                  Repository Layer                            │
│                 (Acceso a Datos)                             │
│  - Queries SQL                                              │
│  - Mapeo ORM a entidades                                    │
│  - Caching de queries                                       │
│  - Transacciones de BD                                      │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                   Database Layer                             │
│              (SQL Server / Otros)                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Estructura de Directorios

```
rexus/
├── repositories/               # Capa de Repositorios
│   ├── __init__.py
│   ├── base.py                # BaseRepository abstracto
│   └── inventario/
│       └── productos_repository.py
│
├── services/                   # Capa de Servicios
│   ├── __init__.py
│   ├── base.py                # BaseService abstracto
│   └── inventario/
│       └── productos_service.py
│
└── modules/                    # Módulos existentes (refactorizando gradualmente)
    └── 02_inventario/
        └── model.py           # Modelo antiguo (a migrar)
```

---

## 🔧 Componentes

### 1. BaseRepository

**Propósito**: Proporciona interfaz estándar para acceso a datos.

**Ubicación**: [rexus/repositories/base.py](../rexus/repositories/base.py)

**Operaciones CRUD básicas**:
```python
from rexus.repositories.base import BaseRepository, RepositoryConfig

class MiRepositorio(BaseRepository):
    def __init__(self, db_connection, sql_manager):
        super().__init__(
            db_connection=db_connection,
            sql_manager=sql_manager,
            config=RepositoryConfig(
                table_name='mi_tabla',
                primary_key='id',
                soft_delete=True
            )
        )

    # Implementar métodos abstractos:
    def find_by_id(self, id): ...
    def find_all(self, filters=None, limit=None, offset=None): ...
    def create(self, entity): ...
    def update(self, entity): ...
    def delete(self, id): ...
```

**Métodos utilidad heredados**:
- `find_one(filters)` - Busca una entidad
- `find_by_ids(ids)` - Busca múltiples por IDs
- `exists(id)` - Verifica existencia
- `count(filters)` - Cuenta entidades
- `create_many(entities)` - Creación en batch
- `update_many(entities)` - Actualización en batch
- `delete_many(ids)` - Eliminación en batch

---

### 2. BaseService

**Propósito**: Proporciona funcionalidad común para lógica de negocio.

**Ubicación**: [rexus/services/base.py](../rexus/services/base.py)

**Validaciones incluidas**:
```python
from rexus.services.base import BaseService, ValidationError

class MiServicio(BaseService):
    def crear_entidad(self, data):
        # Validar campos requeridos
        errors = self.validate_required(data, ['nombre', 'email'])
        if errors:
            return ServiceResult(success=False, validation_errors=errors)

        # Validar longitud
        errors.extend(self.validate_length(
            data['nombre'],
            min_length=3,
            max_length=50,
            field_name='nombre'
        ))

        # Validar número
        errors.extend(self.validate_numeric(
            data['edad'],
            min_value=18,
            max_value=100,
            field_name='edad'
        ))
```

**Métodos de caché**:
- `_cache_get(key)` - Obtener del caché
- `_cache_set(key, value, ttl)` - Guardar en caché
- `_cache_delete(key)` - Eliminar key
- `_cache_invalidate_pattern(pattern)` - Invalidar por patrón

**Logging estructurado**:
- `_log_operation(operation, details)` - Registrar operación
- `_log_error(operation, error, details)` - Registrar error

**Ejecución segura**:
- `execute_safely(operation, callable_func)` - Ejecuta con manejo de errores

---

### 3. Servicio Concreto: ProductoService

**Propósito**: Lógica de negocio de productos de inventario.

**Ubicación**: [rexus/services/inventario/productos_service.py](../rexus/services/inventario/productos_service.py)

**Ejemplo de uso**:
```python
from rexus.services.inventario.productos_service import ProductoService

# Inicializar
service = ProductoService(
    db_connection=mi_conexion,
    sql_manager=mi_sql_manager,
    cache_manager=mi_cache_manager
)

# Crear producto
result = service.create_producto({
    'descripcion': 'Ventana aluminio 2x1',
    'categoria': 'Perfiles',
    'precio_unitario': 150.00,
    'stock_actual': 50,
    'stock_minimo': 10
})

if result.success:
    print(f"Producto creado: {result.data}")
else:
    print(f"Error: {result.error}")
    if hasattr(result, 'validation_errors'):
        print(f"Validaciones: {result.validation_errors}")

# Listar productos con filtros
result = service.list_productos(
    categoria='Perfiles',
    low_stock=True,
    limit=10
)

productos = result.data

# Ajustar stock
result = service.adjust_stock(
    producto_id=123,
    cantidad=-5,  # Restar 5 unidades
    motivo='Venta'
)

if result.success:
    print(f"Nuevo stock: {result.data['stock_actual']}")
    if result.data['stock_bajo']:
        print("⚠️ Alerta: Stock bajo")
```

---

## 📝 Guía de Migración

### Paso 1: Crear Repository para tu módulo

```python
# rexus/repositories/tu_modulo/entity_repository.py
from rexus.repositories.base import BaseRepository, RepositoryConfig

class EntityRepository(BaseRepository):
    def __init__(self, db_connection, sql_manager):
        super().__init__(
            db_connection=db_connection,
            sql_manager=sql_manager,
            config=RepositoryConfig(table_name='tu_tabla')
        )

    def find_by_id(self, id):
        # Implementar búsqueda por ID
        pass

    def find_all(self, filters=None, limit=None, offset=None):
        # Implementar búsqueda con filtros
        pass

    def create(self, entity):
        # Implementar creación
        pass

    def update(self, entity):
        # Implementar actualización
        pass

    def delete(self, id):
        # Implementar eliminación (soft delete)
        pass
```

### Paso 2: Crear Service para tu módulo

```python
# rexus/services/tu_modulo/entity_service.py
from rexus.services.base import BaseService, ServiceResult

class EntityService(BaseService):
    def __init__(self, db_connection, sql_manager=None, cache_manager=None):
        super().__init__(
            repository=EntityRepository(db_connection, sql_manager),
            cache_manager=cache_manager
        )

    def create_entity(self, data):
        # Validaciones
        errors = self._validate_entity(data)
        if errors:
            return self.create_result(
                success=False,
                error="Validación falló",
                validation_errors=[e.__dict__ for e in errors]
            )

        # Lógica de negocio
        try:
            entity = self.repository.create(data)
            self._cache_invalidate_pattern('entities:*')
            return self.create_result(success=True, data=entity)
        except Exception as e:
            return self.create_result(success=False, error=str(e))

    def _validate_entity(self, data):
        # Implementar validaciones específicas
        return []
```

### Paso 3: Actualizar Controller para usar Service

**Antes (código antiguo)**:
```python
class Controller:
    def __init__(self):
        self.model = InventarioModel(db_connection, sql_manager)

    def crear_producto(self, producto_data):
        # Lógica de negocio mezclada con controller
        if not producto_data.get('descripcion'):
            return {'error': 'Descripción requerida'}

        producto = self.model.crear_producto(producto_data)
        return producto
```

**Después (refactorizado)**:
```python
class Controller:
    def __init__(self):
        self.producto_service = ProductoService(
            db_connection=db_connection,
            sql_manager=sql_manager,
            cache_manager=cache_manager
        )

    def crear_producto(self, producto_data):
        # Controller solo delega al service
        result = self.producto_service.create_producto(producto_data)
        return result.to_dict() if result.success else {'error': result.error}
```

---

## ✅ Beneficios Obtenidos

### Testabilidad
```python
# Tests unitarios sin BD
def test_producto_service_validacion():
    mock_repo = Mock(spec=ProductoRepository)
    mock_cache = Mock()
    service = ProductoService(
        db_connection=None,
        sql_manager=None,
        cache_manager=mock_cache
    )
    service.repository = mock_repo

    # Test de validaciones
    result = service.create_producto({'descripcion': ''})
    assert not result.success
    assert 'descripcion' in str(result.validation_errors)
```

### Flexibilidad
```python
# Cambiar infraestructura es fácil
# Solo necesitas crear un nuevo Repository

class MongoProductoRepository(BaseRepository):
    def find_by_id(self, id):
        return mongo_client.productos.find_one({'_id': id})

# El Service no cambia
service = ProductoService(
    db_connection=None,
    sql_manager=None
)
service.repository = MongoProductoRepository()  # Inyección de dependencia
```

### Mantenibilidad
- **Código organizado**: Cada capa tiene su responsabilidad
- **Fácil encontrar bugs**: Separación clara de responsabilidades
- **Reutilización**: Métodos de repository reutilizables en múltiples services

---

## 🚀 Próximos Pasos

### Estado Actual
- ✅ BaseRepository implementado
- ✅ BaseService implementado
- ✅ Ejemplo: ProductoRepository + ProductoService

### Pendiente
- [ ] Migrar módulos restantes a Repository Pattern
- [ ] Crear Repositories para: Obras, Herrajes, Compras, etc.
- [ ] Crear Services para todos los módulos
- [ ] Actualizar Controllers para usar Services
- [ ] Migrar tests a usar mocks de repositories/services

### Prioridad de Migración
1. **Alta**: Inventario (ejemplo creado)
2. **Media**: Herrajes, Obras, Compras
3. **Baja**: Módulos con bajo tráfico

---

**Fecha**: 2025-02-07
**Arquitectura implementada por**: Claude Sonnet (AI Assistant)
**Patrones aplicados**: Repository Pattern, Service Layer, Dependency Injection
**Archivos creados**: 6 (bases + ejemplo inventario)
