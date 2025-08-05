# Documentación del Módulo de Herrajes

## Descripción General

El módulo de Herrajes proporciona una interfaz completa para la gestión de herrajes y accesorios utilizados en obras de construcción. Permite el manejo de inventario específico de herrajes, asignación por obras, y control de pedidos.

## Arquitectura del Módulo

### Componentes Principales

1. **HerrajesView** (`rexus/modules/herrajes/view.py`)
   - Vista principal de gestión de herrajes
   - Interfaz de búsqueda y filtrado
   - Diálogos para operaciones CRUD
   - Sistema de asignación por obras

2. **HerrajesModel** (`rexus/modules/herrajes/model.py`)
   - Capa de acceso a datos
   - Consultas SQL optimizadas con sql_script_loader
   - Validación de integridad relacional
   - Gestión de stock y disponibilidad

3. **HerrajesController** (`rexus/modules/herrajes/controller.py`)
   - Lógica de negocio
   - Coordinación entre vista y modelo
   - Manejo de eventos y señales

### Diálogos Especializados

1. **HerrajeDialogManager** - Gestión centralizada de diálogos
2. **HerrajeObrasDialog** - Asignación de herrajes a obras
3. **HerrajePedidosDialog** - Gestión de pedidos de herrajes

## Características de Seguridad

### Migración a Scripts SQL Externos
- **sql_script_loader**: Implementado para separar lógica SQL
- **Consultas parametrizadas**: Prevención de inyección SQL
- **Validación de parámetros**: Entrada segura de datos

### Control de Acceso
- **AuthManager**: Verificación de permisos por operación
- **Logging**: Registro de operaciones críticas
- **SecurityUtils**: Utilidades de seguridad integradas

## Funcionalidades Implementadas

### ✅ Completadas
- Migración de métodos principales a scripts externos
- Limpieza de imports no utilizados
- Estandarización de manejo de excepciones
- Sistema de logging básico implementado
- Interfaces de gestión modularizadas

### Gestión de Herrajes
- **CRUD completo**: Crear, leer, actualizar, eliminar herrajes
- **Búsqueda avanzada**: Por código, descripción, proveedor
- **Filtrado inteligente**: Por categoría, estado, obra
- **Validación de datos**: Campos obligatorios y formatos

### Asignación por Obras
- **Vinculación obra-herraje**: Asignación específica por proyecto
- **Control de cantidades**: Gestión de stock disponible
- **Seguimiento de uso**: Historial por obra
- **Reportes de asignación**: Generación automática

### Gestión de Pedidos
- **Pedidos por obra**: Solicitudes específicas por proyecto
- **Control de estado**: Seguimiento de pedidos
- **Integración con proveedores**: Gestión de solicitudes
- **Alertas automáticas**: Notificaciones de stock bajo

## Estructura de Datos

### Tabla Principal: herrajes
```sql
CREATE TABLE herrajes (
    id INTEGER PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    descripcion TEXT NOT NULL,
    proveedor VARCHAR(100),
    precio DECIMAL(10,2),
    stock_actual INTEGER DEFAULT 0,
    stock_minimo INTEGER DEFAULT 5,
    categoria VARCHAR(50),
    estado VARCHAR(20) DEFAULT 'ACTIVO',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Relaciones Principales
- **herrajes_obras**: Asignación de herrajes por obra
- **pedidos_herrajes**: Pedidos de herrajes por obra
- **movimientos_herrajes**: Historial de movimientos de stock

## Mejoras Implementadas

### Scripts SQL Externos
- Separación de consultas complejas
- Mejora en mantenibilidad del código
- Reutilización de consultas
- Mejor control de versiones

### Gestión de Diálogos Mejorada
- **HerrajeDialogManager**: Gestión centralizada
- **Validación integrada**: FormValidator implementado
- **Interfaz consistente**: Diseño unificado
- **Manejo de errores**: Feedback claro al usuario

### Limpieza de Código
- Eliminación de imports no utilizados
- Organización de dependencias
- Estandarización de nomenclatura
- Optimización de performance

## Integración con Otros Módulos

### Módulo de Obras
- Vinculación directa herraje-obra
- Reportes consolidados
- Seguimiento por proyecto

### Módulo de Inventario General
- Sincronización de stock
- Alertas compartidas
- Reportes unificados

### Módulo de Compras
- Integración de pedidos
- Gestión de proveedores
- Control de costos

## Validaciones y Controles

### Validación de Integridad Relacional
```python
def validar_integridad_herraje_obra(self, herraje_id, obra_id):
    """
    Valida que la asignación herraje-obra sea válida.
    
    Args:
        herraje_id (int): ID del herraje
        obra_id (int): ID de la obra
        
    Returns:
        tuple: (es_valido: bool, mensaje: str)
    """
```

### Control de Stock
- Validación de stock disponible
- Alertas de stock mínimo
- Prevención de stock negativo
- Seguimiento de movimientos

## Logging y Auditoría

### Configuración de Logger
```python
self.logger = logging.getLogger(f"{__name__}.HerrajesView")
```

### Eventos Registrados
- Operaciones CRUD sobre herrajes
- Asignaciones por obra
- Pedidos creados y modificados
- Errores y excepciones
- Acceso a funcionalidades

## Casos de Uso Principales

### 1. Crear Nuevo Herraje
1. Usuario abre diálogo "Nuevo Herraje"
2. Validación de campos obligatorios
3. Verificación de código único
4. Registro en base de datos
5. Actualización de interfaz

### 2. Asignar Herraje a Obra
1. Selección de herraje y obra
2. Validación de stock disponible
3. Creación de asignación
4. Actualización de disponibilidad
5. Registro de movimiento

### 3. Generar Pedido de Herrajes
1. Selección de herrajes necesarios
2. Especificación de cantidades
3. Validación con proveedores
4. Creación de pedido
5. Seguimiento de estado

## Testing

### Cobertura de Tests
- Tests unitarios de funcionalidades básicas
- Tests de integración con otros módulos
- Tests de validación de datos
- Tests de interfaz de usuario

### Archivos de Test
- `test_herrajes_model.py`: Tests del modelo
- `test_herrajes_view.py`: Tests de la vista
- `test_herrajes_integration.py`: Tests de integración

## Configuración

### Parámetros del Módulo
```json
{
  "herrajes": {
    "stock_minimo_default": 5,
    "categorias_disponibles": [
      "Bisagras",
      "Cerraduras",
      "Manijas",
      "Tornillería",
      "Accesorios"
    ],
    "proveedores_preferidos": [
      "Proveedor A",
      "Proveedor B"
    ]
  }
}
```

## Mejoras Futuras

### Próximas Implementaciones
- Documentación detallada de relaciones
- Auditoría visual completa
- Tests de casos extremos
- Optimización de consultas

### Propuestas de Mejora
- Integración con catálogos de proveedores
- Sistema de alertas avanzadas
- Reportes gráficos
- Sincronización en tiempo real

## Troubleshooting

### Problemas Conocidos

1. **Diálogos duplicados**
   - Revisar definiciones de métodos
   - Eliminar duplicados
   - Consolidar funcionalidades

2. **Referencias indefinidas**
   - Verificar imports
   - Comprobar definiciones de clases
   - Revisar dependencias

3. **Performance lenta**
   - Optimizar consultas SQL
   - Implementar paginación
   - Cachear datos frecuentes

## Contacto y Soporte

Para reportar bugs o solicitar mejoras en el módulo de Herrajes, contactar al equipo de desarrollo.

---

**Versión**: 1.0.0
**Última actualización**: 5 de agosto de 2025
**Autor**: Sistema Rexus.app
