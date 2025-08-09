revisa# Guía de uso de bases de datos y tablas en la aplicación

-------------------------------------------------------------
DOCUMENTACIÓN DE USO DE BASES DE DATOS EN LA APP
-------------------------------------------------------------

1. La base de datos 'users' SOLO debe usarse para:
   - Login de usuarios
   - Gestión de permisos y roles
   - Todo lo relacionado con autenticación y seguridad

2. TODOS los demás módulos (inventario, obras, pedidos, vidrios, herrajes, etc.)
   deben usar la base de datos 'inventario' para sus tablas y operaciones.

3. La base de datos 'auditoria' se usa exclusivamente para trazabilidad y registro de eventos críticos.

NO mezclar tablas de negocio en 'users'. NO usar 'inventario' para login o permisos.
-------------------------------------------------------------

## Bases de datos disponibles

- **users**
  - Uso exclusivo para login, autenticación y gestión de permisos/roles.
  - Tablas:
    - `usuarios`: gestión de usuarios y credenciales
    - `permisos_modulos`: permisos por usuario y módulo
    - `notificaciones`: notificaciones internas para usuarios

- **inventario**
  - Uso para todos los módulos de negocio (obras, inventario, pedidos, vidrios, herrajes, etc.)
  - Tablas:
    - `inventario`: catálogo y stock de materiales
    - `movimientos_inventario`: auditoría de movimientos de stock
    - `obras`: gestión de obras y proyectos
    - `historial_estados`: historial de estados de obras
    - `vidrios_por_obra`: pedidos y asignación de vidrios
    - `herrajes_por_obra`: pedidos y asignación de herrajes
    - `pedidos_materiales`, `pedidos_material`, `reservas_stock`, `detalle_pedido`: gestión de pedidos y reservas
    - `herrajes`, `pedidos_herrajes`: catálogo y pedidos de herrajes
    - `vidrios`, `pedidos_vidrios`: catálogo y pedidos de vidrios

- **auditoria**
  - Uso exclusivo para trazabilidad y registro de eventos críticos.
  - Tablas:
    - `auditoria`: registro de acciones y eventos
    - `logs_usuarios`: logs de actividad de usuarios

## Reglas de uso

- No mezclar tablas de negocio en la base `users`.
- No usar la base `inventario` para login o permisos.
- Cada módulo debe conectarse solo a la base de datos que le corresponde según su función.

## Ejemplo de conexión por módulo

- **Login y permisos:**
  ```python
  db = UsersDatabaseConnection()
  # Acceso a usuarios, permisos_modulos, notificaciones
  ```

- **Inventario, obras, pedidos, etc.:**
  ```python
  db = InventarioDatabaseConnection()
  # Acceso a inventario, obras, pedidos_materiales, etc.
  ```

- **Auditoría:**
  ```python
  db = AuditoriaDatabaseConnection()
  # Acceso a auditoria, logs_usuarios
  ```

---

Mantén este archivo actualizado si se agregan nuevas tablas o bases de datos.
