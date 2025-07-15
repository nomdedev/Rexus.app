# Documentación Detallada de Tablas y Uso por Módulo

**Actualizado al 13/06/2025**

Este documento describe en detalle, módulo por módulo, todas las tablas utilizadas en el sistema, sus columnas, el propósito de cada campo y cómo se relacionan con la lógica de la aplicación. Es referencia obligatoria para desarrollo, QA, auditoría y sincronización con la base de datos.

---

## Índice
1. [Obras](#obras)
2. [Inventario](#inventario)
3. [Herrajes](#herrajes)
4. [Vidrios](#vidrios)
5. [Pedidos de Materiales](#pedidos-de-materiales)
6. [Producción](#producción)
7. [Logística](#logística)
8. [Contabilidad](#contabilidad)
9. [Usuarios y Auditoría](#usuarios-y-auditoría)
10. [Configuración](#configuración)

---

## Obras

**Tabla:** `obras`
- **Módulo:** Obras
- **Columnas:**
  - `id` (PK, int, autoincremental): Identificador único de la obra.
  - `nombre` (varchar): Nombre de la obra.
  - `cliente` (varchar): Cliente asociado.
  - `fecha_medicion` (date): Fecha de medición.
  - `fecha_entrega` (date): Fecha de entrega pactada.
  - `estado` (varchar): Estado general de la obra (Medición, Fabricación, Entrega, etc).
  - `direccion` (varchar): Dirección de la obra.
  - `observaciones` (text): Observaciones generales.
  - `usuario_creador` (int, FK a usuarios): Usuario que creó la obra.
  - `fecha_creacion` (datetime): Fecha de alta.
  - `fecha_modificacion` (datetime): Última modificación.
  - `estado_actual` (varchar): Estado actual de la obra.
  - `ultima_actualizacion` (datetime): Fecha de la última actualización del estado.
- **Uso:** Gestión central de obras, integración con pedidos, producción, logística y contabilidad.

**Tabla:** `historial_estados`
- **Módulo:** Obras
- **Columnas:**
  - `id` (PK, int, autoincremental): Identificador único del registro.
  - `id_obra` (FK a obras): Relación con la tabla `obras`.
  - `estado` (varchar): Estado de la obra en ese momento.
  - `fecha_cambio` (datetime): Fecha en que se cambió al estado.
  - `detalles` (varchar): Información adicional sobre el cambio.
- **Uso:** Registrar el historial de cambios de estado de las obras para trazabilidad.

---

## Inventario

**Tabla:** `inventario`
- **Módulo:** Inventario
- **Columnas:**
  - `id` (PK, int): Identificador del material.
  - `nombre` (varchar): Nombre del material.
  - `descripcion` (varchar): Descripción.
  - `stock` (int): Cantidad disponible.
  - `stock_minimo` (int): Stock mínimo recomendado.
  - `ubicacion` (varchar): Ubicación física.
  - `unidad` (varchar): Unidad de medida.
  - `activo` (bit): Si el material está activo.
- **Uso:** Control de stock, reservas, devoluciones, generación de pedidos.

**Tabla:** `movimientos_inventario`
- **Módulo:** Inventario
- **Columnas:**
  - `id` (PK, int)
  - `id_material` (FK a inventario)
  - `tipo_movimiento` (varchar): Entrada, salida, reserva, devolución.
  - `cantidad` (int)
  - `fecha` (datetime)
  - `usuario` (FK a usuarios)
  - `motivo` (varchar)
- **Uso:** Auditoría y trazabilidad de movimientos de stock.

**Tabla:** `vidrios_por_obra` (actualización)
- **Nuevas Columnas:**
  - `fecha_actualizacion` (datetime): Fecha de la última actualización del pedido de vidrios.
- **Uso:** Registrar cuándo se actualizó por última vez el estado del pedido de vidrios.

**Tabla:** `herrajes_por_obra` (actualización)
- **Nuevas Columnas:**
  - `fecha_actualizacion` (datetime): Fecha de la última actualización del pedido de herrajes.
- **Uso:** Registrar cuándo se actualizó por última vez el estado del pedido de herrajes.

---

## Herrajes

**Tabla:** `herrajes`
- **Módulo:** Herrajes
- **Columnas:**
  - `id` (PK, int)
  - `nombre` (varchar)
  - `tipo` (varchar)
  - `stock` (int)
  - `proveedor` (varchar)
  - `activo` (bit)
- **Uso:** Catálogo y stock de herrajes.

**Tabla:** `pedidos_herrajes`
- **Módulo:** Herrajes, Pedidos
- **Columnas:**
  - `id` (PK, int)
  - `id_obra` (FK a obras)
  - `fecha` (datetime)
  - `estado` (varchar)
  - `usuario` (FK a usuarios)
- **Uso:** Seguimiento de pedidos de herrajes por obra.

---

## Vidrios

**Tabla:** `vidrios`
- **Módulo:** Vidrios
- **Columnas:**
  - `id` (PK, int)
  - `tipo` (varchar)
  - `espesor` (float)
  - `medidas` (varchar)
  - `stock` (int)
  - `proveedor` (varchar)
  - `activo` (bit)
- **Uso:** Catálogo y stock de vidrios.

**Tabla:** `pedidos_vidrios`
- **Módulo:** Vidrios, Pedidos
- **Columnas:**
  - `id` (PK, int)
  - `id_obra` (FK a obras)
  - `fecha` (datetime)
  - `estado` (varchar)
  - `usuario` (FK a usuarios)
- **Uso:** Seguimiento de pedidos de vidrios por obra.

---

## Pedidos de Materiales

**Tabla:** `pedidos_materiales`
- **Módulo:** Pedidos, Inventario
- **Columnas:**
  - `id` (PK, int)
  - `id_obra` (FK a obras)
  - `fecha` (datetime)
  - `estado` (varchar)
  - `usuario` (FK a usuarios)
- **Uso:** Seguimiento de pedidos de materiales por obra.

**Tabla:** `pedidos_material`
- **Módulo:** Inventario
- **Columnas:**
  - `id` (PK, int): Identificador único del pedido.
  - `id_obra` (FK a obras): Obra asociada al pedido.
  - `id_perfil` (FK a inventario_perfiles): Material solicitado.
  - `cantidad` (int): Cantidad solicitada.
  - `estado` (varchar): Estado del pedido (pendiente, completado, etc.).
  - `fecha` (datetime): Fecha del pedido.
  - `usuario` (FK a usuarios): Usuario que realizó el pedido.
- **Uso:** Registro de pedidos de materiales asociados a obras.

**Tabla:** `reservas_stock`
- **Módulo:** Inventario
- **Columnas:**
  - `id` (PK, int): Identificador único de la reserva.
  - `id_item` (FK a inventario): Material reservado.
  - `id_obra` (FK a obras): Obra asociada a la reserva.
  - `cantidad_reservada` (int): Cantidad reservada.
  - `estado` (varchar): Estado de la reserva (activa, pendiente, etc.).
  - `fecha_reserva` (datetime): Fecha de la reserva.
- **Uso:** Gestión de reservas de stock para obras.

**Tabla:** `detalle_pedido`
- **Módulo:** Compras
- **Columnas:**
  - `id` (PK, int): Identificador único del detalle.
  - `id_pedido` (FK a pedidos): Pedido asociado.
  - `id_item` (FK a inventario): Ítem solicitado.
  - `cantidad` (int): Cantidad solicitada.
  - `precio_unitario` (decimal): Precio unitario del ítem.
  - `subtotal` (decimal): Subtotal del detalle.
- **Uso:** Almacenar detalles de pedidos realizados.

---

## Usuarios y Auditoría

**Tabla:** `usuarios`
- **Módulo:** Usuarios
- **Columnas:**
  - `id` (PK, int)
  - `nombre` (varchar)
  - `email` (varchar)
  - `rol` (varchar)
  - `activo` (bit)
- **Uso:** Gestión de usuarios y permisos.

**Tabla:** `auditoria`
- **Módulo:** Auditoría
- **Columnas:**
  - `id` (PK, int)
  - `usuario` (FK a usuarios)
  - `fecha` (datetime)
  - `accion` (varchar)
  - `modulo` (varchar)
  - `detalle` (text)
- **Uso:** Registro de acciones y eventos para trazabilidad.

**Tabla:** `notificaciones`
- **Módulo:** Notificaciones
- **Columnas:**
  - `id` (PK, int): Identificador único de la notificación.
  - `usuario_id` (FK a usuarios): Usuario destinatario de la notificación.
  - `mensaje` (varchar): Contenido de la notificación.
  - `fecha_envio` (datetime): Fecha de envío de la notificación.
  - `estado` (varchar): Estado de la notificación (pendiente, leída, etc.).
- **Uso:** Gestión de alertas y mensajes a los usuarios.

**Tabla:** `permisos_modulos`
- **Módulo:** Usuarios
- **Columnas:**
  - `id` (PK, int): Identificador único del permiso.
  - `id_usuario` (FK a usuarios): Usuario al que se le asigna el permiso.
  - `modulo` (varchar): Módulo al que aplica el permiso.
  - `puede_ver` (bit): Indica si el usuario puede ver el módulo.
  - `puede_modificar` (bit): Indica si el usuario puede modificar el módulo.
  - `puede_aprobar` (bit): Indica si el usuario puede aprobar acciones en el módulo.
- **Uso:** Gestión de permisos de acceso a módulos específicos.

**Tabla:** `logs_usuarios`
- **Módulo:** Auditoría
- **Columnas:**
  - `id` (PK, int): Identificador único del log.
  - `usuario_id` (FK a usuarios): Usuario que realizó la acción.
  - `accion` (varchar): Acción realizada.
  - `modulo` (varchar): Módulo donde se realizó la acción.
  - `fecha_hora` (datetime): Fecha y hora de la acción.
  - `detalle` (varchar): Detalles adicionales de la acción.
  - `ip_origen` (varchar): Dirección IP desde donde se realizó la acción.
- **Uso:** Registro de acciones de los usuarios para auditoría.

---

## Configuración

**Tabla:** `configuracion`
- **Módulo:** Configuración
- **Columnas:**
  - `id` (PK, int)
  - `clave` (varchar)
  - `valor` (varchar)
  - `descripcion` (varchar)
- **Uso:** Almacenamiento de parámetros críticos y configuración dinámica.

---

## Actualización: Base de Datos por Tabla

### Obras
**Base de Datos:** `obras`
- **Tabla:** `obras`
- **Tabla:** `historial_estados`

### Inventario
**Base de Datos:** `inventario`
- **Tabla:** `inventario`
- **Tabla:** `movimientos_inventario`
- **Tabla:** `vidrios_por_obra`
- **Tabla:** `herrajes_por_obra`

### Herrajes
**Base de Datos:** `herrajes`
- **Tabla:** `herrajes`
- **Tabla:** `pedidos_herrajes`

### Vidrios
**Base de Datos:** `vidrios`
- **Tabla:** `vidrios`
- **Tabla:** `pedidos_vidrios`

### Pedidos de Materiales
**Base de Datos:** `pedidos`
- **Tabla:** `pedidos_materiales`
- **Tabla:** `pedidos_material`
- **Tabla:** `reservas_stock`
- **Tabla:** `detalle_pedido`

### Usuarios y Auditoría
**Base de Datos:** `users`
- **Tabla:** `usuarios`
- **Tabla:** `permisos_modulos`
- **Tabla:** `notificaciones`

**Base de Datos:** `auditoria`
- **Tabla:** `auditoria`
- **Tabla:** `logs_usuarios`

### Configuración
**Base de Datos:** `configuracion`
- **Tabla:** `configuracion`

---

## Relaciones entre Tablas y Flujo de Datos

### Relaciones Clave entre Tablas

1. **Obras y su Historial de Estados**:
   - La tabla `obras` se relaciona con `historial_estados` mediante la columna `id` de `obras` y `id_obra` de `historial_estados`.
   - Uso: Permite rastrear los cambios de estado de una obra a lo largo del tiempo.

2. **Inventario y Movimientos de Inventario**:
   - La tabla `inventario` se relaciona con `movimientos_inventario` mediante la columna `id` de `inventario` y `id_material` de `movimientos_inventario`.
   - Uso: Proporciona trazabilidad de entradas, salidas y reservas de materiales.

3. **Usuarios y Auditoría**:
   - La tabla `usuarios` se relaciona con `auditoria` mediante la columna `id` de `usuarios` y `usuario` de `auditoria`.
   - Uso: Registro de acciones realizadas por los usuarios en el sistema.

4. **Pedidos y Detalles de Pedidos**:
   - La tabla `pedidos_materiales` se relaciona con `detalle_pedido` mediante la columna `id` de `pedidos_materiales` y `id_pedido` de `detalle_pedido`.
   - Uso: Almacenar los ítems solicitados en cada pedido.

### Flujo de Datos entre Módulos

1. **Gestión de Obras**:
   - Los datos de `obras` se integran con `pedidos_materiales`, `vidrios_por_obra` y `herrajes_por_obra` para gestionar los materiales requeridos.
   - El estado de las obras se actualiza en `historial_estados` para mantener trazabilidad.

2. **Control de Inventario**:
   - Los movimientos de inventario (`movimientos_inventario`) se generan a partir de pedidos (`pedidos_materiales`) y reservas (`reservas_stock`).

3. **Auditoría y Seguridad**:
   - Todas las acciones de los usuarios se registran en `auditoria` y `logs_usuarios` para garantizar trazabilidad y seguridad.

### Ejemplos de Consultas SQL

1. **Obtener el historial de estados de una obra específica**:
   ```sql
   SELECT h.estado, h.fecha_cambio, h.detalles
   FROM historial_estados h
   INNER JOIN obras o ON h.id_obra = o.id
   WHERE o.nombre = 'Obra Ejemplo';
   ```

2. **Consultar el stock disponible de un material específico**:
   ```sql
   SELECT nombre, stock, ubicacion
   FROM inventario
   WHERE nombre = 'Material Ejemplo';
   ```

3. **Listar las acciones realizadas por un usuario en un módulo específico**:
   ```sql
   SELECT a.fecha, a.accion, a.detalle
   FROM auditoria a
   INNER JOIN usuarios u ON a.usuario = u.id
   WHERE u.nombre = 'Usuario Ejemplo' AND a.modulo = 'Inventario';
   ```

### Diagramas de Relaciones

Se recomienda utilizar herramientas como [dbdiagram.io](https://dbdiagram.io) o similares para generar diagramas visuales de las relaciones entre tablas. Esto facilitará la comprensión de la estructura y el flujo de datos.

---

## Tablas presentes en la base de datos `inventario` no implementadas o con uso parcial

A continuación se listan las tablas que existen en la base de datos `inventario` pero no están implementadas en la lógica principal del sistema, o su uso es parcial/redundante. Se incluyen sugerencias de funcionalidad y migración:

- **inventario**: Tabla histórica, en desuso o absorbida por `inventario_perfiles`. Sugerencia: migrar datos relevantes y eliminar si no se usa.
- **inventario_items**: Usada para otros productos (herrajes, insumos) en tests y scripts, pero parece redundante con `inventario_perfiles`. Sugerencia: migrar lógica y datos a `inventario_perfiles` y eliminar si no hay dependencias.
- **movimientos_stock_items**: Registra movimientos de stock de items. Usada en tests, pero no en la lógica principal. Sugerencia: migrar a `movimientos_stock` si es posible.
- **pagos_por_obra / pagos_obra / pagos_pedidos**: Relacionadas con pagos, pero no se observa uso activo en inventario. Sugerencia: integrar con contabilidad y reportes financieros si se requiere trazabilidad de pagos.
- **obra_materiales / pedidos_obra / reserva_materiales**: Usadas en scripts y migraciones, pueden estar en transición o ser redundantes. Sugerencia: revisar dependencias y migrar a modelos actuales.
- **vidrios_por_obra / herrajes_por_obra / logistica_por_obra**: Relacionadas con otros módulos, su uso en inventario es indirecto. Sugerencia: documentar integración o migrar si corresponde.
- **estado_material / historial / auditorias_sistema**: Para trazabilidad y auditoría, pero no se observa uso directo en inventario. Sugerencia: implementar lógica de auditoría si se requiere mayor trazabilidad.
- **materiales**: Puede ser redundante con inventario_perfiles/items. Sugerencia: migrar datos y eliminar si no se usa.
- **users / auditoria**: Tablas de usuarios y auditoría, usadas en otros módulos pero no directamente en inventario.

**Notas de migración y mejora:**
- Revisar dependencias antes de eliminar cualquier tabla.
- Migrar datos históricos relevantes a las tablas actuales.
- Documentar cualquier integración entre módulos que dependa de estas tablas.
- Si se decide eliminar una tabla, actualizar este documento y los scripts de migración.

---

**Sugerencias de funcionalidades para mejor aprovechamiento de las tablas**

A continuación se proponen funcionalidades que pueden implementarse para aprovechar mejor la información de cada tabla:

- **inventario / inventario_perfiles / inventario_items**
  - Reportes históricos de stock y movimientos.
  - Alertas automáticas de stock bajo, vencimientos y productos críticos.
  - Auditoría de cambios y trazabilidad completa de cada producto.
  - Integración con compras/ventas para actualizar stock en tiempo real.
  - Dashboard visual de estado de inventario y tendencias.

- **movimientos_stock / movimientos_stock_items**
  - Dashboard de movimientos recientes y tendencias de consumo.
  - Estadísticas de entradas/salidas por período, usuario o tipo de producto.
  - Exportación de movimientos para análisis externo.
  - Filtros avanzados por tipo de movimiento, usuario, fecha, producto.

- **pagos_por_obra / pagos_obra / pagos_pedidos**
  - Reportes financieros por obra, proveedor o período.
  - Alertas de pagos pendientes o vencidos.
  - Integración con módulos de contabilidad y facturación.
  - Visualización de flujo de pagos y estado de cuentas.

- **obra_materiales / pedidos_obra / reserva_materiales**
  - Seguimiento detallado de consumo y reservas por obra.
  - Proyección de necesidades futuras según avance de obra.
  - Visualización de materiales asignados y pendientes.
  - Alertas de faltantes y vencimientos de reservas.

- **vidrios_por_obra / herrajes_por_obra / logistica_por_obra**
  - Seguimiento de entregas y pedidos específicos por obra.
  - Alertas de retrasos o faltantes en logística.
  - Integración con inventario para actualizar stock automáticamente.
  - Reportes de cumplimiento y eficiencia logística.

- **estado_material / historial / auditorias_sistema**
  - Trazabilidad completa de cambios y acciones sobre materiales.
  - Reportes de auditoría por usuario, fecha o tipo de acción.
  - Alertas de acciones críticas o sospechosas.
  - Visualización de historial de modificaciones y accesos.

- **materiales**
  - Unificación de catálogo de materiales para evitar duplicados.
  - Clasificación avanzada por tipo, proveedor, uso, etc.
  - Reportes de materiales por categoría y proveedor.

- **users / auditoria**
  - Reportes de actividad y permisos por usuario.
  - Alertas de accesos o acciones no autorizadas.
  - Integración con auditoría para trazabilidad completa.
  - Panel de administración de usuarios y roles.

**Planificación para implementación**

1. Priorizar funcionalidades según impacto y facilidad de desarrollo.
2. Definir requerimientos técnicos y de negocio para cada funcionalidad.
3. Crear historias de usuario y tareas en el gestor de proyectos.
4. Implementar módulos de reportes, alertas y dashboards visuales.
5. Integrar auditoría y trazabilidad en operaciones críticas.
6. Documentar cada nueva funcionalidad y actualizar este archivo.

---

**Sugerencia de módulo administrativo de Recursos Humanos**

Para complementar la parte contable y administrativa, se recomienda implementar un módulo de Recursos Humanos con las siguientes funcionalidades y tablas:

- **Tabla: operarios**
  - Datos personales: nombre, apellido, DNI, fecha de nacimiento, dirección, contacto.
  - Datos laborales: fecha de ingreso, puesto, área, estado (activo/inactivo).
  - Salario y condiciones contractuales.

- **Tabla: historial_academico**
  - Relación con operario.
  - Estudios realizados, cursos, certificaciones, fechas y entidades.

- **Tabla: desempeño_laboral**
  - Relación con operario.
  - Evaluaciones periódicas, observaciones, calificaciones, fechas.

- **Tabla: historial_salarios**
  - Relación con operario.
  - Registro de cambios de salario, bonificaciones, descuentos, fechas y motivos.

- **Funcionalidades recomendadas**
  - Carga y edición de datos de operarios.
  - Registro y consulta de historial académico y desempeño.
  - Seguimiento de evolución salarial y condiciones laborales.
  - Reportes de desempeño, historial y situación contractual.
  - Integración con contabilidad para cálculo de costos laborales y liquidaciones.
  - Alertas de vencimiento de contratos, capacitaciones pendientes, evaluaciones próximas.

**Planificación para implementación**

1. Definir el modelo de datos y las relaciones entre tablas.
2. Crear las tablas y migraciones necesarias en la base de datos.
3. Desarrollar formularios y vistas para carga y consulta de información.
4. Integrar reportes y alertas en el dashboard administrativo.
5. Documentar el módulo y actualizar este archivo.

---

**Nota sobre integración de módulos administrativos**

El módulo administrativo de usuarios y recursos humanos puede integrarse dentro del módulo "Contabilidad" o bien redefinirse como un módulo más amplio llamado "Administración", que incluya tanto la gestión contable como la gestión de personal, salarios y desempeño.

Esto permite centralizar la información administrativa y facilitar el acceso a reportes, auditoría y seguimiento de recursos humanos y aspectos económicos en un solo lugar.

Se recomienda:
- Unificar la documentación y los modelos bajo el nuevo módulo "Administración".
- Integrar formularios, reportes y dashboards para usuarios, operarios, salarios y contabilidad.
- Actualizar el índice y las secciones del documento para reflejar esta integración.

---

**Este archivo debe mantenerse actualizado tras cada cambio en los modelos o la base de datos.**
