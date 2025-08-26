# Migración Sistemática de Queries Embebidas a Archivos SQL - Progreso

## Estado de la Migración (26/08/2025)

### ✅ MÓDULOS COMPLETADOS:

#### 🔹 rexus/core/database.py
- ✅ Migrado completamente a pyodbc/SQL Server
- ✅ Eliminadas todas las referencias a SQLite

#### 🔹 logistica/model.py
- **logistica**: Queries migradas a `sql/logistica/`
  - `insert_servicio_transporte.sql`
  - `select_servicios_transporte_activos.sql`
  - `select_servicios_transporte_all.sql`
  - `insert_proveedor_transporte.sql`
- ✅ Código actualizado para cargar queries desde archivos
- ✅ SQLite eliminado completamente

#### 🔹 compras/proveedores_model.py
- ✅ Completamente restructurado y migrado  
- ✅ Queries externalizadas a sql/compras/
- ✅ Usuario realizó correcciones manuales verificadas
- ✅ Código limpio y funcional

#### 🔹 inventario/model.py
- ✅ Queries principales migradas a sql/inventario/
- ✅ select_lotes_inventario.sql, actualizar_stock_lote.sql creados
- ✅ Código actualizado para cargar queries externas

#### 🔹 obras/submodules/recursos_manager.py
- ✅ Queries migradas a sql/obras/
- ✅ select_vidrio_stock.sql, update_vidrio_stock.sql, etc. creados
- ✅ Código actualizado para usar consultas externas
- ✅ Imports corregidos (pyodbc, typing)

#### 🔹 mantenimiento/model.py
- ✅ Queries principales migradas a sql/mantenimiento/
- ✅ 8 archivos SQL creados específicos para migración
- ✅ 6 métodos migrados: obtener_estado_equipos, obtener_todos_equipos, crear_equipo, programar_mantenimiento, ejecutar_mantenimiento, obtener_historial_mantenimiento
- ✅ sql_manager inicializado correctamente
- ✅ Import datetime.datetime no usado eliminado
- ✅ Total de 29 archivos SQL en el directorio

#### 🔹 notificaciones/model.py
- ✅ Queries principales migradas a sql/notificaciones/
- ✅ 7 archivos SQL creados para operaciones CRUD completas
- ✅ 5 métodos migrados: eliminar_notificacion, crear_notificacion, marcar_como_leida, obtener_notificaciones, obtener_notificaciones_no_leidas, contar_no_leidas
- ✅ sql_manager inicializado correctamente
- ✅ Import json no usado eliminado

#### 🔹 herrajes/model.py
- ✅ Queries principales migradas a sql/herrajes/
- ✅ 5 métodos migrados completamente
- ✅ Archivos SQL: select_herraje_by_codigo.sql, insert_herraje_simple.sql, update_stock_herraje.sql, etc.
- ✅ Import pyodbc eliminado, constructor limpio
- ✅ sql_manager inicializado correctamente

#### 🔹 vidrios/model.py
- ✅ Queries principales migradas a sql/vidrios/
- ✅ 10+ archivos SQL creados para operaciones CRUD completas
- ✅ Métodos críticos migrados: eliminar, crear, actualizar, obtener
- ✅ Import pyodbc eliminado completamente
- ✅ sql_manager inicializado correctamente
- ⚠️ Fallback mantenido para filtros complejos

### 🔄 MÓDULOS EN PROGRESO:

#### 🔸 usuarios/model.py (75% completado)
- ✅ Queries migradas a sql/usuarios/: 
  - select_usuario_autenticacion.sql
  - update_incrementar_intentos_fallidos.sql  
  - update_ultimo_acceso.sql
  - verificar_tabla_permisos_usuario.sql
  - select_permisos_usuario.sql
  - select_rol_usuario.sql
- ✅ sql_manager inicializado correctamente
- ⚠️ Pendiente: revisar método ejecutar_consulta_archivo

- **compras**: Queries migradas a `sql/compras/`
  - `insert_proveedor.sql`
  - `select_proveedor_by_id.sql`
  - `select_proveedores_activos.sql`
  - `select_proveedores_all.sql`

#### herrajes/model.py (100% completado) ✅ MIGRADO
- ✅ sql_manager inicializado correctamente
- ✅ Todos los métodos migrados a consultas externas
- ✅ Archivos SQL: select_herraje_by_codigo.sql, delete_herraje_by_codigo.sql, insert_herraje_simple.sql, update_stock_herraje.sql, etc.
- ✅ Import pyodbc eliminado
- ✅ Constructor limpio y sin duplicaciones
- ✅ Métodos: obtener_herraje_por_codigo, eliminar_herraje, obtener_todos_herrajes, crear_herraje, actualizar_stock

#### vidrios/model.py (95% completado) ✅ MIGRADO
- ✅ sql_manager inicializado correctamente
- ✅ Todas las queries principales migradas a consultas externas
- ✅ 10+ archivos SQL creados: select_vidrio_activo_by_id.sql, insert_vidrio_completo.sql, etc.
- ✅ Métodos migrados: eliminar_vidrio, crear_vidrio, actualizar_vidrio, obtener_vidrio_por_id, obtener_vidrios
- ✅ Import pyodbc eliminado
- ✅ Total de 38+ archivos SQL en directorio vidrios/
- ⚠️ Fallback mantenido para filtros complejos en obtener_vidrios

#### rexus/utils/ (CRÍTICO - Descubierto) ⭐ NUEVO
- ⚠️ **data_integrity_validator.py**: Consultas de integridad críticas
- ⚠️ **database_optimizer.py**: Consultas de optimización y métricas
- ⚠️ **intelligent_cache_manager.py**: Gestión de caché embebida
- 📁 3 queries creadas en sql/utils/: select_usuario_by_username.sql, etc.

### ❌ PENDIENTES CRÍTICOS:

#### usuarios/model.py (85% completado)
- ✅ 6 queries migradas a sql/usuarios/
- ✅ sql_manager inicializado 
- ⚠️ Método execute_query pendiente de verificación

#### usuarios/submodules/profiles_manager.py (60% completado)  
- ✅ 5 queries creadas: update_soft_delete_usuario.sql, count_usuarios_*.sql
- ⚠️ Archivo incompleto - falta estructura completa

### ❌ PENDIENTES CRÍTICOS:

#### administracion/model.py
- ⚠️ **ISSUES GRAVES**: Sintaxis e indentación rotas
- ✅ Algunos métodos ya usan sql_manager.get_query
- 🔧 Requiere refactor completo antes de migración

#### rexus/utils/ (DESCUBIERTO)
- ⚠️ **NUEVO**: data_integrity_validator.py, database_optimizer.py
- 📊 Consultas embebidas en utilidades críticas del sistema

### ❌ PENDIENTES REGULARES:
- **obras**: controller.py, view.py (submodules completados ✅)
- **pedidos**: Sin analizar
- **herrajes**: Sin analizar  
- **vidrios**: Sin analizar
- **auditoria**: Sin analizar
- **configuracion**: Sin analizar
- **mantenimiento**: Sin analizar
- **notificaciones**: Sin analizar

### 📋 ARCHIVOS CORREGIDOS:
- `rexus/core/database.py`: Migrado de SQLite a SQL Server (pyodbc)
- `rexus/modules/compras/proveedores_model.py`: Reestructurado completamente
- `rexus/modules/logistica/model.py`: Queries migradas a archivos externos
- `rexus/modules/inventario/model.py`: Parcialmente migrado

### 🗂️ ESTRUCTURA SQL CREADA:
```
sql/
├── logistica/
├── compras/  
├── inventario/
├── obras/
├── vidrios/ (✅ 38+ archivos)
├── herrajes/ (✅ 29+ archivos)
├── notificaciones/ (✅ 7 archivos nuevos)
├── mantenimiento/ (✅ 29 archivos)
├── utils/
└── usuarios/ (ya existía con muchos archivos)
```

### 📝 PRÓXIMOS PASOS:
1. Continuar migración de módulos restantes
2. Eliminar todas las referencias a SQLite
3. Validar funcionamiento con SQL Server
4. Documentar cambios realizados

---
**Progreso estimado:** 50% completado
