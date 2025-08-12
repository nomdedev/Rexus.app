# Documentación del Módulo de Inventario

## Descripción General

El módulo de Inventario es un sistema completo de gestión de productos, stock y reservas integrado en la aplicación Rexus.app. Proporciona funcionalidades avanzadas para el control de inventario, sistema de reservas por obra, y seguimiento de disponibilidad en tiempo real.

## Arquitectura del Módulo

### Componentes Principales

1. **InventarioView** (`rexus/modules/inventario/view.py`)
   - Vista principal con interfaz de pestañas
   - Sistema de reservas integrado
   - Controles de filtrado y búsqueda
   - Formularios de entrada con validación

2. **InventarioModel** (`rexus/modules/inventario/model.py`)
   - Capa de acceso a datos
   - Consultas SQL parametrizadas y seguras
   - Validación de stock negativo
   - Gestión de transacciones

3. **InventarioController** (`rexus/modules/inventario/controller.py`)
   - Lógica de negocio
   - Coordinación entre vista y modelo
   - Manejo de eventos

### Pestañas de la Interfaz

1. **Inventario General**
   - Lista completa de productos
   - Búsqueda y filtrado avanzado
   - Operaciones CRUD sobre productos

2. **Reservas por Obra**
   - Sistema de reservas vinculado a obras
   - Control de disponibilidad
   - Liberación automática de reservas

3. **Disponibilidad en Tiempo Real**
   - Monitor de stock actual
   - Alertas de stock bajo
   - Estadísticas de inventario

## Características de Seguridad

### Sanitización de Datos
- **DataSanitizer**: Implementado en todos los campos de entrada
- **Protección XSS**: Sanitización automática de texto
- **Validación SQL**: Prevención de inyección SQL

### Validación de Entrada
- **FormValidator**: Sistema de validación integrado
- **Campos obligatorios**: Verificación automática
- **Tipos de datos**: Validación de formato y rango

### Control de Acceso
- **Autorización**: Verificación de permisos por operación
- **Logging**: Registro de todas las operaciones críticas
- **Auditoría**: Seguimiento de cambios

## Funcionalidades Implementadas

### ✅ Completadas
- Sistema de validación de stock negativo
- Sanitización de datos de entrada (DataSanitizer)
- Logging de operaciones críticas
- Migración parcial a scripts SQL externos
- Headers MIT de licencia
- Interfaz de reservas por obra
- Control de disponibilidad en tiempo real

### Gestión de Productos
- **Agregar productos**: Formulario completo con validación
- **Editar productos**: Actualización de datos existentes
- **Eliminar productos**: Con confirmación de seguridad
- **Búsqueda avanzada**: Por código, descripción, categoría

### Sistema de Reservas
- **Reservar por obra**: Asignación temporal de productos
- **Liberar reservas**: Manual o automática
- **Control de disponibilidad**: Cálculo en tiempo real
- **Reportes de reservas**: Generación automática

### Monitoreo de Stock
- **Alertas de stock bajo**: Configurables por producto
- **Estadísticas generales**: Valor total, productos activos
- **Historial de movimientos**: Seguimiento completo

## Validaciones Implementadas

### Validación de Stock Negativo
```python
def validar_stock_negativo(self, producto_id, cantidad_solicitada):
    """
    Valida que la operación no genere stock negativo.
    
    Args:
        producto_id (int): ID del producto
        cantidad_solicitada (int): Cantidad a descontar
        
    Returns:
        tuple: (es_valido: bool, mensaje: str)
    """
```

### Sanitización de Entradas
```python
if SANITIZER_AVAILABLE and data_sanitizer:
    codigo_text = data_sanitizer.sanitize_string(self.codigo_input.text())
    descripcion_text = data_sanitizer.sanitize_string(self.descripcion_input.text())
```

## Logging y Auditoría

### Configuración de Logger
```python
self.logger = logging.getLogger(f"{__name__}.InventarioView")
```

### Eventos Registrados
- Inicialización del módulo
- Operaciones CRUD sobre productos
- Errores y excepciones
- Mensajes mostrados al usuario
- Validaciones exitosas y fallidas

## Casos de Uso Principales

### 1. Agregar Nuevo Producto
1. Usuario abre diálogo "Nuevo Producto"
2. Sistema valida campos obligatorios
3. Sanitización automática de entradas
4. Validación de stock y precios
5. Registro en base de datos
6. Logging de la operación

### 2. Reservar Productos para Obra
1. Usuario selecciona obra y productos
2. Sistema verifica disponibilidad
3. Validación de stock suficiente
4. Creación de reserva temporal
5. Actualización de disponibilidad
6. Notificación al usuario

### 3. Monitoreo de Stock Bajo
1. Sistema calcula stock actual
2. Comparación con límites configurados
3. Generación de alertas automáticas
4. Actualización de indicadores visuales
5. Registro de eventos

## Dependencias

### Internas
- `utils.data_sanitizer`: Sanitización de datos
- `rexus.utils.form_validators`: Validación de formularios
- `utils.sql_script_loader`: Carga de scripts SQL externos

### Externas
- `PyQt6`: Interfaz gráfica
- `logging`: Sistema de logs
- `sqlite3/pymysql`: Conexión a base de datos

## Testing

### Cobertura de Tests
- **Tests unitarios**: 40+ archivos de test
- **Tests de integración**: Pruebas completas del flujo
- **Tests de UI**: Verificación de interfaz
- **Edge cases**: Casos límite y errores

### Archivos de Test Principales
- `test_inventario_complete.py`: Tests completos
- `test_inventario_edge_cases.py`: Casos límite
- `test_inventario_view_complete.py`: Tests de vista
- `test_inventario_controller_complete.py`: Tests de controlador

## Mejoras Futuras

### En Desarrollo
- Migración completa a scripts SQL externos
- Implementación de feedback visual mejorado
- Documentación de API completa
- Optimización de rendimiento

### Propuestas
- Integración con códigos de barras
- Reportes avanzados con gráficos
- Sincronización con proveedores
- Alertas push en tiempo real

## Configuración

### Requisitos del Sistema
- Python 3.8+
- PyQt6
- Base de datos SQLite o MySQL
- Espacio en disco: 50MB mínimo

### Variables de Configuración
```json
{
  "inventario": {
    "stock_minimo_default": 10,
    "alertas_activas": true,
    "reservas_auto_liberacion": 24,
    "backup_automatico": true
  }
}
```

## Troubleshooting

### Problemas Comunes

1. **Error de Conexión a BD**
   - Verificar configuración de conexión
   - Comprobar permisos de acceso
   - Revisar logs de aplicación

2. **Validación Fallida**
   - Verificar formato de datos
   - Comprobar campos obligatorios
   - Revisar límites configurados

3. **Performance Lenta**
   - Optimizar consultas SQL
   - Implementar paginación
   - Reducir carga de datos inicial

## Contacto y Soporte

Para reportar bugs o solicitar mejoras, contactar al equipo de desarrollo a través del sistema de issues del proyecto.

---

**Versión**: 1.0.0
**Última actualización**: 5 de agosto de 2025
**Autor**: Sistema Rexus.app
