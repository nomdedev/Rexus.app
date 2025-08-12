# Análisis Completo de Base de Datos - Rexus.app

## Resumen Ejecutivo

La aplicación Rexus.app utiliza **3 bases de datos principales** con aproximadamente **45-50 tablas activas**. Se identificaron **4-6 tablas potencialmente redundantes** y **4-6 pares de columnas** que requieren estandarización.

---

## Bases de Datos Utilizadas

### 1. **`users`** - Gestión de Usuarios y Seguridad
- **Propósito**: Autenticación, permisos, auditoría de usuarios
- **Tablas principales**: usuarios, roles, permisos, sesiones, auditoría

### 2. **`inventario`** - Operaciones Comerciales
- **Propósito**: Inventario, materiales, obras, pedidos, logística
- **Tablas principales**: inventario_perfiles, obras, pedidos, herrajes, vidrios

### 3. **`auditoria`** - Auditoría del Sistema
- **Propósito**: Registros de eventos del sistema y errores
- **Tablas principales**: auditorias_sistema, errores_sistema

---

## Base de Datos `users`

### ✅ Tablas Activas (Confirmadas en Uso)

**Autenticación y Usuarios:**
- `usuarios` - Tabla principal de usuarios con controles de seguridad
- `roles` - Definición de roles del sistema
- `permisos_usuario` - Permisos específicos por usuario
- `sesiones_usuario` - Gestión de sesiones activas
- `rbac_roles` - Roles para control de acceso basado en roles
- `rbac_permissions` - Permisos granulares
- `rbac_role_permissions` - Asignación rol-permiso
- `rbac_user_roles` - Asignación usuario-rol

**Auditoría del Sistema:**
- `auditoria_sistema` - Eventos de seguridad y auditoría
- `notificaciones` - Notificaciones de usuario

### ⚠️ Tablas Potencialmente Redundantes

1. **`permisos_modulos`** - Posible duplicación de funcionalidad con `permisos_usuario`
2. **`logs_usuarios`** - Puede solaparse con `auditoria_sistema`

### 🔧 Problemas de Columnas Identificados

**Tabla `usuarios`:**
- `ultima_conexion` vs `ultimo_login` (script sugiere eliminar `ultima_conexion`)

**Tabla `permisos_modulos`:**
- `usuario_id` vs `id_usuario` (estandarizar en `id_usuario`)

**Tabla `logs_usuarios`:**
- `fecha` vs `fecha_hora` (estandarizar en `fecha_hora`)

---

## Base de Datos `inventario`

### ✅ Tablas Activas (Confirmadas por Modelos)

**Gestión de Inventario:**
- `inventario_perfiles` - Tabla principal de inventario (usada por InventarioModel)
- `movimientos_stock` - Seguimiento de movimientos de stock
- `reservas_materiales` - Reservas de materiales para obras
- `materiales` - Catálogo adicional de materiales
- `materiales_por_obra` - Materiales asignados a obras específicas

**Gestión de Obras:**
- `obras` - Tabla principal de proyectos/obras (usada por ObrasModel)
- `cronograma_obras` - Programación de obras
- `perfiles_por_obra` - Perfiles asignados a obras

**Compras y Pedidos:**
- `pedidos` - Órdenes de compra (usada por PedidosModel)
- `pedidos_compra` - Órdenes de compra (tabla alternativa)
- `pedidos_por_obra` - Pedidos por obra
- `detalle_pedido` - Líneas de detalle de pedidos
- `proveedores` - Proveedores/vendedores

**Inventario Especializado:**
- `herrajes` - Inventario de herrajes (usada por HerrajesModel)
- `herrajes_obra` - Herrajes asignados a obras
- `herrajes_inventario` - Seguimiento de inventario de herrajes
- `pedidos_herrajes` - Pedidos de herrajes
- `vidrios` - Inventario de vidrios (usada por VidriosModel)
- `vidrios_obra` - Vidrios asignados a obras
- `pedidos_vidrios` - Pedidos de vidrios

### 📋 Tablas de Módulos Extendidos (24 tablas adicionales)

**Recursos Humanos:**
- `empleados`, `departamentos`, `asistencias`, `nomina`
- `bonos_descuentos`, `historial_laboral`

**Contabilidad:**
- `libro_contable`, `recibos`, `pagos_obra`, `pagos_materiales`

**Mantenimiento:**
- `equipos`, `herramientas`, `mantenimientos`
- `programacion_mantenimiento`, `tipos_mantenimiento`
- `estado_equipos`, `historial_mantenimiento`

**Logística:**
- `transportes`, `entregas`, `detalle_entregas`

**Configuración del Sistema:**
- `configuracion_sistema`, `parametros_modulos`
- `auditoria_cambios`, `logs_sistema`

### ⚠️ Tablas Potencialmente Redundantes

1. **`inventario_items`** - **MARCADA EXPLÍCITAMENTE COMO REDUNDANTE** en scripts de sincronización
2. **`reservas_stock`** - Puede solaparse con `reservas_materiales`

### 🔧 Problemas de Columnas

**Tabla `inventario_perfiles`:**
- `stock` vs `stock_actual` (potencial redundancia)

**Inconsistencias de Naming:**
- `id_item` vs `id_perfil` - Múltiples tablas usan ambas convenciones para el mismo concepto

---

## Base de Datos `auditoria`

### ✅ Tablas Activas
- `auditoria` - Log básico de auditoría
- `auditorias_sistema` - Auditoría mejorada del sistema
- `errores_sistema` - Registro de errores del sistema

---

## Recomendaciones de Limpieza

### 🚨 Alta Prioridad - Eliminar

1. **`inventario_items`** - **Explícitamente marcada como redundante** en scripts
2. **`reservas_stock`** - Se solapa con `reservas_materiales`

### ⚠️ Media Prioridad - Revisar

3. **`permisos_modulos`** - Posible duplicación con `permisos_usuario`
4. **`logs_usuarios`** - Posible solapamiento con `auditoria_sistema`

### 🔧 Limpieza de Columnas Recomendada

**Alta Prioridad:**
1. **users.usuarios**: Eliminar `ultima_conexion` si `ultimo_login` cumple la misma función
2. **inventario.inventario_perfiles**: Eliminar columna `stock` si `stock_actual` es la canónica
3. **users.permisos_modulos**: Estandarizar en `id_usuario`, eliminar `usuario_id`
4. **users.logs_usuarios**: Estandarizar en `fecha_hora`, eliminar `fecha`

### 📝 Estandarización de Naming

**Claves Foráneas Inconsistentes:**
- Estandarizar `id_perfil` vs `id_item` en todas las tablas relacionadas con inventario

---

## Notas de Seguridad

✅ **Prevención de SQL Injection**: Los modelos usan consultas parametrizadas y validación de nombres de tabla

✅ **Tablas Permitidas**: Cada modelo mantiene conjuntos `_allowed_tables` para seguridad

✅ **No Creación Dinámica**: La aplicación no crea tablas en tiempo de ejecución

---

## Estadísticas Finales

- **Total Bases de Datos**: 3
- **Tablas Activas Estimadas**: 45-50
- **Tablas Potencialmente Sin Uso**: 4-6
- **Tablas Marcadas para Revisión**: 2 (explícitamente redundantes)
- **Pares de Columnas a Limpiar**: 4-6

## Conclusión

La aplicación tiene un diseño de base de datos bien estructurado con separación adecuada de responsabilidades. Las principales oportunidades de limpieza son:

1. **Eliminar tablas explícitamente redundantes**
2. **Estandarizar convenciones de nombres de columnas** 
3. **Revisar tablas potencialmente duplicadas**

Esta limpieza mejorará el rendimiento, reducirá la complejidad y facilitará el mantenimiento futuro.