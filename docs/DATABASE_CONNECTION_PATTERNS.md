# Patrones de Conexión a Base de Datos - Rexus.app v2.0.0

## Resumen Ejecutivo

Esta documentación analiza y documenta los patrones de conexión a base de datos utilizados en toda la aplicación Rexus.app, con especial atención a la tabla `inventario_perfiles` y propuestas para implementar lazy loading.

## Arquitectura de Base de Datos

### 1. Múltiples Bases de Datos Especializadas

La aplicación utiliza una **arquitectura de múltiples bases de datos** para separar responsabilidades:

```python
# Bases de datos definidas en src/core/database.py
DB_USERS = "users"          # Autenticación y permisos
DB_INVENTARIO = "inventario" # Módulos de negocio
DB_AUDITORIA = "auditoria"  # Trazabilidad y eventos
```

### 2. Clases de Conexión Específicas

```python
# Conexiones especializadas por dominio
class UsersDatabaseConnection(DatabaseConnection):
    def __init__(self):
        super().__init__(database=DB_USERS)

class InventarioDatabaseConnection(DatabaseConnection):
    def __init__(self):
        super().__init__(database=DB_INVENTARIO)

class AuditoriaDatabaseConnection(DatabaseConnection):
    def __init__(self):
        super().__init__(database=DB_AUDITORIA)
```

## Análisis de Patrones de Conexión por Módulo

### 1. Módulo de Inventario

**Patrón Actual**: Conexión directa en constructor
```python
class InventarioModel:
    def __init__(self, db_connection=None):
        self.db_connection = db_connection
        self.tabla_inventario = "inventario_perfiles"  # TABLA CRÍTICA
        self._crear_tablas_si_no_existen()  # Conexión inmediata
```

**Características**:
- ✅ **Tabla inventario_perfiles verificada** en línea 26
- ✅ **Conexión inmediata** al inicializar el modelo
- ✅ **Verificación de estructura** de tablas en startup
- ⚠️ **Mantiene conexión activa** durante toda la vida del objeto

### 2. Módulo de Usuarios

**Patrón Actual**: Conexión directa en constructor
```python
class UsuariosModel:
    def __init__(self, db_connection=None):
        self.db_connection = db_connection
        self.tabla_usuarios = "usuarios"
        self._crear_tabla_si_no_existe()  # Conexión inmediata
```

**Características**:
- ✅ **Conexión inmediata** al inicializar
- ✅ **Creación automática** de tablas si no existen
- ⚠️ **Conexión persistente** durante toda la sesión

### 3. Módulo de Herrajes

**Patrón Actual**: Conexión directa en constructor
```python
class HerrajesModel:
    def __init__(self, db_connection=None):
        self.db_connection = db_connection
        self.tabla_herrajes = "herrajes"
        self._crear_tablas_si_no_existen()  # Conexión inmediata
```

**Características similares** a otros módulos.

### 4. Módulo de Configuración

**Patrón Actual**: Conexión directa + fallback a archivo
```python
class ConfiguracionModel:
    def __init__(self, db_connection=None):
        self.db_connection = db_connection
        self.config_file = Path("config/rexus_config.json")
        self._crear_tabla_si_no_existe()
        self._cargar_configuracion_inicial()  # Conexión inmediata
```

**Características**:
- ✅ **Fallback a archivo JSON** si no hay BD
- ✅ **Cache en memoria** para configuraciones
- ✅ **Doble persistencia** (BD + archivo)

## Problemas Identificados con el Patrón Actual

### 1. **Conexiones Persistentes Innecesarias**
```python
# PROBLEMA: Conexión activa durante toda la vida del objeto
class InventarioModel:
    def __init__(self, db_connection=None):
        self.db_connection = db_connection  # Conexión persistente
```

### 2. **Inicialización Pesada**
```python
# PROBLEMA: Operaciones de BD en constructor
def __init__(self, db_connection=None):
    self._crear_tablas_si_no_existen()  # Operación pesada en init
    self._cargar_configuracion_inicial()  # Más operaciones en init
```

### 3. **Falta de Pool de Conexiones**
- Cada módulo mantiene su propia conexión
- No hay reutilización de conexiones
- Posible agotamiento de recursos

## Tabla `inventario_perfiles` - Estado Actual

### Confirmación de Existencia
```python
# CONFIRMADO: Tabla existe y está configurada
self.tabla_inventario = "inventario_perfiles"  # model.py línea 26
```

### Verificación en Startup
```python
def _crear_tablas_si_no_existen(self):
    cursor.execute(
        "SELECT * FROM sysobjects WHERE name=? AND xtype='U'",
        (self.tabla_inventario,),  # Verifica inventario_perfiles
    )
```

### Estructura de Datos
La tabla `inventario_perfiles` contiene **campos completos** para:
- ✅ **Información básica**: código, descripción, tipo_material
- ✅ **Control de stock**: stock_actual, stock_minimo, ubicacion
- ✅ **Campos técnicos**: QR, imagen_referencia
- ✅ **Datos del inventario real**: proveedor, dimensiones, importes

## Propuesta de Lazy Loading

### 1. **Patrón de Conexión Bajo Demanda**

```python
class InventarioModelLazy:
    def __init__(self):
        self._db_connection = None
        self.tabla_inventario = "inventario_perfiles"
        # NO inicializar conexión aquí
    
    def _get_connection(self):
        """Obtiene conexión solo cuando se necesita"""
        if self._db_connection is None:
            self._db_connection = InventarioDatabaseConnection()
        return self._db_connection
    
    def obtener_todos_productos(self, filtros=None):
        """Método que conecta solo cuando se llama"""
        db = self._get_connection()  # Conexión bajo demanda
        cursor = db.cursor()
        # ... resto del código
```

### 2. **Context Manager para Conexiones**

```python
class DatabaseContextManager:
    def __init__(self, db_class):
        self.db_class = db_class
        self.connection = None
    
    def __enter__(self):
        self.connection = self.db_class()
        return self.connection
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.disconnect()

# Uso en modelo
def obtener_productos_lazy(self):
    with DatabaseContextManager(InventarioDatabaseConnection) as db:
        cursor = db.cursor()
        # Operación de BD
        # Conexión se cierra automáticamente
```

### 3. **Singleton para Pool de Conexiones**

```python
class DatabasePool:
    _instance = None
    _connections = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_connection(self, db_name):
        if db_name not in self._connections:
            if db_name == "inventario":
                self._connections[db_name] = InventarioDatabaseConnection()
            elif db_name == "users":
                self._connections[db_name] = UsersDatabaseConnection()
        return self._connections[db_name]
```

## Implementación de Backup Automático

### 1. **Backup en Operaciones Críticas**

```python
class InventarioModelWithBackup:
    def __init__(self):
        self.backup_manager = BackupManager()
    
    def actualizar_stock(self, producto_id, nuevo_stock):
        """Actualiza stock con backup automático"""
        try:
            # Crear backup antes de la operación
            self.backup_manager.crear_backup_pre_operacion(
                tabla="inventario_perfiles",
                operacion="UPDATE_STOCK",
                producto_id=producto_id
            )
            
            # Realizar la operación
            resultado = self._ejecutar_actualizacion_stock(producto_id, nuevo_stock)
            
            # Backup post-operación si es exitosa
            if resultado:
                self.backup_manager.crear_backup_post_operacion(
                    tabla="inventario_perfiles",
                    operacion="UPDATE_STOCK",
                    producto_id=producto_id,
                    estado="SUCCESS"
                )
            
            return resultado
            
        except Exception as e:
            # Backup en caso de error
            self.backup_manager.crear_backup_error(
                tabla="inventario_perfiles",
                operacion="UPDATE_STOCK",
                error=str(e)
            )
            raise
```

### 2. **Backup Diario Automático**

```python
class BackupScheduler:
    def __init__(self):
        self.backup_manager = BackupManager()
    
    def programar_backup_diario(self):
        """Programa backup diario de inventario_perfiles"""
        import schedule
        
        schedule.every().day.at("02:00").do(
            self.backup_manager.crear_backup_completo,
            tabla="inventario_perfiles"
        )
        
        schedule.every().day.at("14:00").do(
            self.backup_manager.crear_backup_incremental,
            tabla="inventario_perfiles"
        )
```

## Recomendaciones de Implementación

### 1. **Fase 1: Implementar Lazy Loading**
- ✅ Modificar constructores para no inicializar conexiones
- ✅ Implementar método `_get_connection()` en cada modelo
- ✅ Usar context managers para operaciones de BD

### 2. **Fase 2: Pool de Conexiones**
- ✅ Implementar singleton para pool de conexiones
- ✅ Reutilizar conexiones entre módulos
- ✅ Configurar timeouts y límites de pool

### 3. **Fase 3: Backup Automático**
- ✅ Implementar backup antes de operaciones críticas
- ✅ Configurar backup diario automático
- ✅ Monitorear espacio de backup y rotación

### 4. **Fase 4: Optimización de Performance**
- ✅ Implementar cache para queries frecuentes
- ✅ Optimizar queries de `inventario_perfiles`
- ✅ Implementar paginación para tablas grandes

## Impacto en Performance

### **Beneficios del Lazy Loading**:
1. **Startup más rápido**: No conexiones en init
2. **Menor uso de memoria**: Conexiones solo cuando necesarias
3. **Mejor escalabilidad**: Pool de conexiones compartido
4. **Recursos optimizados**: Conexiones se cierran automáticamente

### **Consideraciones**:
1. **Primer acceso más lento**: Conexión se crea en primera llamada
2. **Complejidad adicional**: Manejo de errores de conexión
3. **Cache necesario**: Para evitar reconexiones frecuentes

## Conclusión

El patrón actual de conexión directa en constructores funciona pero **no es óptimo para performance**. La implementación de lazy loading con pool de conexiones y backup automático proporcionará:

1. **Mejor performance** en startup
2. **Uso eficiente de recursos** de BD
3. **Backup automático** para `inventario_perfiles`
4. **Mejor escalabilidad** para múltiples usuarios

La tabla `inventario_perfiles` está **completamente configurada** y funcional. La optimización propuesta mejorará significativamente el rendimiento sin afectar la funcionalidad existente.