# Checklist Detallado de Estado y Pendientes del Proyecto

Actualizado: 15/07/2025

---

## 1. Arquitectura de Bases de Datos

- **Bases de datos disponibles:**
  - `users`: login, permisos, roles, notificaciones
  - `inventario`: obras, inventario, pedidos, vidrios, herrajes, movimientos, reservas
  - `auditoria`: logs, trazabilidad, acciones de usuarios

- **Reglas de uso:**
  - No mezclar tablas de negocio en `users`
  - No usar `inventario` para login o permisos
  - Cada módulo debe conectarse solo a la base que le corresponde

---

## 2. Estado por Módulo

### Usuarios (login, permisos)
- **DB:** `users`
- **Tablas:** `usuarios`, `permisos_modulos`, `notificaciones`
- **Info obtenida:** credenciales, roles, módulos asignados, notificaciones
- **Implementado:** Login básico, permisos y roles
- **Pendiente:** CRUD completo de usuarios, gestión avanzada de roles, interfaz de administración

### Inventario
- **DB:** `inventario`
- **Tablas:** `inventario`, `inventario_perfiles`, `inventario_reservas`, `inventario_movimientos`
- **Info obtenida:** stock, catálogo, reservas, movimientos
- **Implementado:** CRUD de materiales, reservas y movimientos, estadísticas de stock
- **Pendiente:** integración visual avanzada, edge cases de stock mínimo, pool de conexiones

### Obras
- **DB:** `inventario`
- **Tablas:** `obras`, `historial_estados`
- **Info obtenida:** datos generales de obra, estados, cronograma
- **Implementado:** CRUD de obras, estados y filtros
- **Pendiente:** cronograma visual, integración profunda con materiales y pedidos

### Herrajes
- **DB:** `inventario`
- **Tablas:** `herrajes`, `herrajes_por_obra`, `pedidos_herrajes`
- **Info obtenida:** catálogo, asignación a obras, pedidos
- **Implementado:** CRUD básico
- **Pendiente:** UI visual, integración con obras, gestión avanzada de proveedores

### Vidrios
- **DB:** `inventario`
- **Tablas:** `vidrios`, `vidrios_por_obra`, `pedidos_vidrios`
- **Info obtenida:** catálogo, asignación a obras, pedidos
- **Implementado:** Falta todo el módulo

### Pedidos de Materiales
- **DB:** `inventario`
- **Tablas:** `pedidos_materiales`, `pedidos_material`, `reservas_stock`, `detalle_pedido`
- **Info obtenida:** pedidos por obra, estado, reservas
- **Implementado:** CRUD básico
- **Pendiente:** validaciones avanzadas, integración con inventario y obras

### Auditoría
- **DB:** `auditoria`
- **Tablas:** `auditoria`, `logs_usuarios`
- **Info obtenida:** acciones de usuarios, logs, trazabilidad
- **Implementado:** sistema completo de logs, exportación y estadísticas
- **Pendiente:** validación de integridad, soft delete, versionado

### Configuración
- **DB:** `inventario` (o `configuracion` si existe)
- **Tablas:** `configuracion_sistema`
- **Info obtenida:** parámetros críticos, configuración dinámica
- **Implementado:** Falta todo el módulo

### Contabilidad
- **DB:** `inventario`
- **Tablas:** `contabilidad_asientos`, `contabilidad_recibos`, `contabilidad_departamentos`, `contabilidad_empleados`
- **Info obtenida:** asientos, recibos, empleados, reportes
- **Implementado:** sistema contable completo
- **Pendiente:** validaciones avanzadas, integración con otros módulos

### Mantenimiento
- **DB:** `inventario`
- **Tablas:** `mantenimiento_equipos`, `mantenimiento_ordenes`, `mantenimiento_historial`
- **Info obtenida:** equipos, órdenes, historial
- **Implementado:** Falta todo el módulo

---

## 3. Seguridad y Buenas Prácticas

- [ ] Consultas parametrizadas en todos los módulos
- [ ] Validación y sanitización de inputs
- [ ] Manejo de transacciones y rollback
- [ ] Pool de conexiones y timeouts
- [ ] Auditoría de accesos y cambios
- [ ] Permisos mínimos en usuarios de BD

---

## 4. Pendientes Generales

- [ ] Implementar módulos faltantes: Vidrios, Mantenimiento, Configuración
- [ ] Completar CRUD y UI en Usuarios, Obras, Herrajes
- [ ] Mejorar integración visual y feedback en todos los módulos
- [ ] Validar relaciones y claves foráneas en BD
- [ ] Tests unitarios y de edge cases para todos los módulos
- [ ] Documentar y actualizar diagramas de relaciones

---

Este archivo debe actualizarse en cada sprint y revisión técnica.