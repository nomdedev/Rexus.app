# Documentación del Módulo de Vidrios

## Descripción General

El módulo de Vidrios proporciona una interfaz completa para la gestión de vidrios y cristales utilizados en proyectos de construcción. Permite el control de inventario específico de vidrios, asignación por obras, gestión de pedidos y seguimiento de disponibilidad.

## Arquitectura del Módulo

### Componentes Principales

1. **VidriosView** (`rexus/modules/vidrios/view.py`)
   - Vista principal de gestión de vidrios
   - Sistema de búsqueda y filtrado avanzado
   - Formularios para operaciones CRUD
   - Panel de asignación por obras

2. **VidriosModel** (`rexus/modules/vidrios/model.py`)
   - Capa de acceso a datos optimizada
   - Consultas SQL seguras (reparadas con listas blancas)
   - Validación de integridad relacional
   - Control de stock y disponibilidad

3. **VidriosController** (`rexus/modules/vidrios/controller.py`)
   - Lógica de negocio centralizada
   - Coordinación entre vista y modelo
   - Manejo de eventos y señales

### Diálogos Especializados

1. **VidrioDialog** - Formulario de creación/edición de vidrios
2. **AsignarObraDialog** - Asignación de vidrios a obras específicas
3. **PedidoVidriosDialog** - Gestión de pedidos de vidrios

## Características de Seguridad

### Migración de Seguridad SQL
- **Consultas vulnerables reparadas**: Implementadas listas blancas
- **Prevención de inyección SQL**: Validación completa de parámetros
- **Sanitización de datos**: DataSanitizer implementado

### Control de Acceso y Validación
- **Sanitización completa**: Implementada en todos los campos de entrada
- **Logging sistemático**: Registro de operaciones críticas y errores
- **Validación de permisos**: Control de acceso por operación

## Funcionalidades Implementadas

### ✅ Completadas
- Sistema de sanitización de datos (DataSanitizer)
- Logging de operaciones críticas y errores
- Búsqueda y filtrado con sanitización
- Formularios con validación y sanitización
- Tooltips y mensajes explicativos
- Control de errores mejorado

### Gestión de Vidrios
- **CRUD completo**: Crear, leer, actualizar, eliminar vidrios
- **Búsqueda inteligente**: Por código, descripción, tipo, color
- **Filtrado avanzado**: Por tipo, proveedor, estado, espesor
- **Validación de datos**: Campos obligatorios y formatos específicos

### Características del Producto
- **Tipos de vidrio**: Templado, laminado, flotado, etc.
- **Especificaciones técnicas**: Espesor, dimensiones, color
- **Tratamientos**: Templado, laminado, serigrafiado
- **Control de calidad**: Estado y observaciones

### Sistema de Obras y Pedidos
- **Asignación por obra**: Vinculación específica por proyecto
- **Control de cantidades**: Gestión de metros cuadrados
- **Pedidos automatizados**: Solicitudes por obra
- **Seguimiento de uso**: Historial completo por proyecto

## Estructura de Datos

### Tabla Principal: vidrios
```sql
CREATE TABLE vidrios (
    id INTEGER PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    descripcion TEXT NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    espesor DECIMAL(4,2),
    proveedor VARCHAR(100),
    precio_m2 DECIMAL(10,2),
    color VARCHAR(50),
    tratamiento VARCHAR(100),
    dimensiones_disponibles TEXT,
    estado VARCHAR(20) DEFAULT 'ACTIVO',
    observaciones TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Relaciones Principales
- **vidrios_obras**: Asignación de vidrios por obra
- **pedidos_vidrios**: Pedidos de vidrios por proyecto
- **movimientos_vidrios**: Historial de cambios y uso

## Mejoras Implementadas

### Sanitización de Datos
```python
# Sanitización en búsqueda
if SANITIZER_AVAILABLE and data_sanitizer and termino:
    termino = data_sanitizer.sanitize_string(termino)

# Sanitización en formularios
codigo = data_sanitizer.sanitize_string(codigo)
descripcion = data_sanitizer.sanitize_string(descripcion)
```

### Sistema de Logging
```python
self.logger = logging.getLogger(f"{__name__}.VidriosView")
self.logger.info("Inicializando vista de vidrios")
self.logger.error(f"Error mostrado al usuario: {mensaje}")
```

### Validación y Control de Errores
- **Validación de entrada**: Campos obligatorios y formatos
- **Control de tipos**: Validación de datos numéricos
- **Manejo de errores**: Feedback claro al usuario
- **Logging de eventos**: Registro completo de operaciones

## Interfaz de Usuario

### Panel de Filtros
- **Búsqueda en tiempo real**: Con sanitización automática
- **Filtros por categoría**: Tipo, proveedor, estado
- **Estadísticas rápidas**: Contadores y totales
- **Botones de acción**: Nuevo, editar, eliminar

### Tabla Principal
- **Vista detallada**: Código, descripción, especificaciones
- **Precios en tiempo real**: Formato de moneda
- **Estado visual**: Indicadores de color
- **Acciones rápidas**: Botones integrados

### Formularios de Entrada
- **Validación en tiempo real**: Campos obligatorios
- **Tooltips informativos**: Ayuda contextual
- **Combos predefinidos**: Valores estandarizados
- **Área de observaciones**: Texto libre sanitizado

## Integración con Otros Módulos

### Módulo de Obras
- Asignación directa vidrio-obra
- Cálculo de necesidades por proyecto
- Reportes consolidados de uso

### Módulo de Inventario General
- Sincronización de stock
- Alertas compartidas de disponibilidad
- Reportes unificados de materiales

### Módulo de Compras
- Integración de pedidos automáticos
- Gestión de proveedores especializados
- Control de costos por metro cuadrado

## Validaciones y Controles

### Validación de Integridad
- **Códigos únicos**: Verificación de duplicados
- **Formatos específicos**: Validación de datos técnicos
- **Rangos de valores**: Control de espesores y precios
- **Estados válidos**: Control de ciclo de vida

### Control de Stock y Disponibilidad
- **Metros cuadrados disponibles**: Cálculo en tiempo real
- **Reservas por obra**: Control de compromisos
- **Alertas de stock bajo**: Notificaciones automáticas
- **Histórico de movimientos**: Trazabilidad completa

## Logging y Auditoría

### Configuración de Logger
```python
self.logger = logging.getLogger(f"{__name__}.VidriosView")
```

### Eventos Registrados
- Inicialización del módulo
- Operaciones CRUD sobre vidrios
- Búsquedas y filtros aplicados
- Asignaciones por obra
- Errores y excepciones
- Mensajes mostrados al usuario

## Casos de Uso Principales

### 1. Agregar Nuevo Vidrio
1. Usuario abre formulario "Nuevo Vidrio"
2. Sanitización automática de campos de texto
3. Validación de código único
4. Verificación de especificaciones técnicas
5. Registro en base de datos con logging

### 2. Búsqueda y Filtrado
1. Usuario ingresa término de búsqueda
2. Sanitización automática del término
3. Aplicación de filtros adicionales
4. Actualización de resultados en tiempo real
5. Logging de operación de búsqueda

### 3. Asignación a Obra
1. Selección de vidrio y obra
2. Especificación de metros cuadrados
3. Validación de disponibilidad
4. Creación de asignación
5. Actualización de stock disponible

## Testing y Cobertura

### Tests Implementados
- Tests unitarios de funcionalidades básicas
- Tests de sanitización de datos
- Tests de validación de formularios
- Tests de integración con otros módulos

### Cobertura de Casos
- Casos normales de uso
- Casos límite y extremos
- Manejo de errores
- Validación de entrada

## Configuración del Módulo

### Parámetros Configurables
```json
{
  "vidrios": {
    "tipos_disponibles": [
      "Templado",
      "Laminado",
      "Flotado",
      "Doble acristalamiento",
      "Espejo"
    ],
    "espesores_estandar": [3, 4, 5, 6, 8, 10, 12, 15, 19, 25],
    "proveedores_preferidos": [
      "Proveedor A",
      "Proveedor B"
    ],
    "stock_minimo_m2": 50
  }
}
```

## Mejoras Futuras

### En Desarrollo
- Tests de casos extremos completos
- Optimización de consultas SQL
- Reportes gráficos avanzados
- Integración con catálogos

### Propuestas de Mejora
- Calculadora de vidrios automática
- Integración con proveedores online
- Sistema de alertas push
- Códigos QR para identificación
- Sincronización móvil

## Troubleshooting

### Problemas Conocidos

1. **Errores de casting en widgets**
   - Verificar tipos de widgets en tablas
   - Comprobar inicialización de controles
   - Validar referencias a objetos

2. **Performance en tablas grandes**
   - Implementar paginación
   - Optimizar filtros
   - Cachear consultas frecuentes

3. **Validación de entrada**
   - Verificar DataSanitizer disponible
   - Comprobar configuración de logging
   - Validar formatos de datos

## Métricas y Estadísticas

### Indicadores Clave
- Total de vidrios en inventario
- Metros cuadrados disponibles
- Número de proveedores activos
- Obras con vidrios asignados
- Valor total del inventario

### Reportes Disponibles
- Inventario por tipo de vidrio
- Consumo por obra
- Proveedores y precios
- Histórico de movimientos
- Alertas de stock bajo

## Contacto y Soporte

Para reportar bugs o solicitar mejoras en el módulo de Vidrios, contactar al equipo de desarrollo a través del sistema de issues del proyecto.

---

**Versión**: 1.0.0
**Última actualización**: 5 de agosto de 2025
**Autor**: Sistema Rexus.app
