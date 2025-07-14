# Estructura Unificada de Base de Datos - Documentación

## Estructura y Relaciones entre Tablas

Este documento describe la estructura unificada de la base de datos tras el proceso de optimización. Se eliminan tablas redundantes y se establece un esquema claro para la integración entre módulos.

## 1. Tablas Principales del Sistema

### Obras (`obras`)
- **Propósito**: Tabla central que almacena la información básica de todas las obras/proyectos.
- **Relaciones**: Es la tabla central a la que se relacionan todas las demás tablas específicas de módulos.
- **Campos clave**:
  - `id` (PK)
  - `nombre`
  - `cliente`
  - `direccion`
  - `fecha_inicio`
  - `fecha_entrega`
  - `estado` (en_curso, finalizada, etc.)

### Inventario (`inventario_perfiles`)
- **Propósito**: Catálogo maestro de perfiles y materiales disponibles.
- **Relaciones**: Se relaciona con `pedidos_compra`, `pedidos_material`, `reserva_materiales`.
- **Campos clave**:
  - `id` (PK)
  - `codigo`
  - `descripcion`
  - `tipo`
  - `stock`

### Usuarios (`users`)
- **Propósito**: Gestión de usuarios y permisos del sistema.
- **Campos clave**:
  - `id` (PK)
  - `nombre`
  - `apellido`
  - `usuario`
  - `password` (encriptado)
  - `rol` (admin, supervisor, usuario)

## 2. Tablas para la Integración Cruzada

### Pedidos de Material (`pedidos_material`)
- **Propósito**: Registra pedidos de materiales específicos para cada obra.
- **Relaciones**:
  - `obra_id` → `obras.id`
  - `material_id` → `inventario_perfiles.id`
- **Campos clave**:
  - `id` (PK)
  - `obra_id` (FK)
  - `material_id` (FK)
  - `cantidad`
  - `estado` (pendiente, pedido, recibido, completado)
  - `fecha_pedido`
  - `usuario_id`

### Vidrios por Obra (`vidrios_por_obra`)
- **Propósito**: Gestión unificada de vidrios asignados a cada obra.
- **Relaciones**:
  - `obra_id` → `obras.id`
- **Campos clave**:
  - `id` (PK)
  - `obra_id` (FK)
  - `tipo_vidrio`
  - `medidas`
  - `cantidad`
  - `estado`
  - `proveedor`
  - `fecha_pedido`
  - `fecha_entrega_estimada`

### Herrajes por Obra (`herrajes_por_obra`)
- **Propósito**: Herrajes asignados a cada obra con cantidades reservadas.
- **Relaciones**:
  - `id_obra` → `obras.id`
- **Campos clave**:
  - `id` (PK)
  - `id_obra` (FK)
  - `id_herraje`
  - `cantidad_reservada`
  - `estado`

### Pedidos de Herrajes (`pedidos_herrajes`)
- **Propósito**: Registro específico de pedidos de herrajes para cada obra.
- **Relaciones**:
  - `obra_id` → `obras.id`
- **Campos clave**:
  - `id` (PK)
  - `obra_id` (FK)
  - `tipo_herraje`
  - `cantidad`
  - `estado`
  - `fecha_pedido`
  - `proveedor`

### Pagos de Pedidos (`pagos_pedidos`)
- **Propósito**: Control unificado de pagos relacionados con pedidos de cualquier módulo.
- **Relaciones**:
  - `obra_id` → `obras.id`
- **Campos clave**:
  - `id` (PK)
  - `obra_id` (FK)
  - `modulo` (inventario, vidrios, herrajes)
  - `tipo_pedido`
  - `monto_total`
  - `monto_pagado`
  - `estado`
  - `fecha_pago`

## 3. Tablas para Auditoría y Seguridad

### Auditoría (`auditoria`)
- **Propósito**: Registro de todas las acciones del sistema para trazabilidad.
- **Campos clave**:
  - `id` (PK)
  - `usuario_id`
  - `modulo`
  - `accion`
  - `detalle`
  - `ip_address`
  - `fecha`

## 4. Flujo de Integración Entre Módulos

### Flujo de Obras -> Inventario
1. Se crea una obra en el módulo de Obras (`obras`)
2. Se registran los materiales necesarios mediante pedidos (`pedidos_material`)
3. Se reserva stock del inventario (`inventario_perfiles`)
4. Se registran los pagos correspondientes (`pagos_pedidos`)

### Flujo de Obras -> Vidrios
1. Se crea una obra en el módulo de Obras (`obras`)
2. Se registran los vidrios necesarios (`vidrios_por_obra`)
3. Se asignan a la obra con su estado de producción/entrega
4. Se registran los pagos correspondientes (`pagos_pedidos`)

### Flujo de Obras -> Herrajes
1. Se crea una obra en el módulo de Obras (`obras`)
2. Se registran los herrajes necesarios (`herrajes_por_obra` y `pedidos_herrajes`)
3. Se asignan a la obra con su estado
4. Se registran los pagos correspondientes (`pagos_pedidos`)

## 5. Ejemplos de Consultas de Integración

### Consulta del estado completo de una obra
```sql
SELECT
    o.id, o.nombre, o.cliente, o.estado as estado_obra,
    (SELECT COUNT(*) FROM pedidos_material WHERE obra_id = o.id) as total_materiales,
    (SELECT COUNT(*) FROM vidrios_por_obra WHERE obra_id = o.id) as total_vidrios,
    (SELECT COUNT(*) FROM herrajes_por_obra WHERE id_obra = o.id) as total_herrajes,
    (SELECT SUM(monto_pagado) FROM pagos_pedidos WHERE obra_id = o.id) as total_pagado
FROM obras o
WHERE o.id = ?
```

### Consulta de materiales pendientes por obra
```sql
SELECT
    m.codigo, m.descripcion, pm.cantidad, pm.estado, pm.fecha_pedido
FROM pedidos_material pm
JOIN inventario_perfiles m ON pm.material_id = m.id
WHERE pm.obra_id = ? AND pm.estado IN ('pendiente', 'pedido')
ORDER BY pm.fecha_pedido
```

### Consulta de pagos pendientes por módulo
```sql
SELECT
    o.nombre as obra, pp.modulo, pp.tipo_pedido,
    pp.monto_total, pp.monto_pagado,
    (pp.monto_total - pp.monto_pagado) as pendiente,
    pp.fecha_vencimiento, pp.estado
FROM pagos_pedidos pp
JOIN obras o ON pp.obra_id = o.id
WHERE pp.estado != 'completado'
ORDER BY pp.fecha_vencimiento
```

## 6. Recomendaciones para Desarrollo Futuro

1. **Mantener la estructura unificada**: Evitar crear nuevas tablas redundantes.
2. **Usar las tablas comunes**: Para nuevos módulos, relacionar con las tablas existentes.
3. **Mantener consistencia en nombres**: Seguir las convenciones establecidas.
4. **Documentar cambios**: Actualizar este documento al modificar la estructura.
5. **Validar integridad**: Ejecutar regularmente el análisis de tablas para verificar consistencia.

## 7. Tablas Obsoletas o Fusionadas

Las siguientes tablas han sido combinadas o reemplazadas en la estructura optimizada:

- `vidrios` → Reemplazada por `vidrios_por_obra`
- `pedidos` → Reemplazada por múltiples tablas específicas por módulo
- `pagos` → Reemplazada por `pagos_pedidos` (con campo `modulo`)

## 8. Auditoría y Trazabilidad

La tabla `auditoria` es crucial para la trazabilidad del sistema. Todas las operaciones críticas deben registrarse en esta tabla, incluyendo:

- Login/logout de usuarios
- Creación, modificación o eliminación de registros importantes
- Acciones críticas de negocio (aprobaciones, rechazos, etc.)
- Accesos o cambios en configuraciones sensitivas

## 9. Estado Actual de la Base de Datos

Según el análisis realizado, la base de datos cuenta con 20 tablas, incluyendo:

- Tablas principales: `obras`, `inventario_perfiles`, etc.
- Tablas de pedidos y pagos: `pedidos_compra`, `pagos_obra`, etc.
- Tablas de detalles: `vidrios_por_obra`, `herrajes_por_obra`, etc.

La estructura es ahora más coherente y facilita la integración entre módulos, eliminando redundancias y mejorando el rendimiento.
