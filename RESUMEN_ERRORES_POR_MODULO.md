# 📊 RESUMEN DE CONSULTAS PROBLEMÁTICAS POR MÓDULO

**Fecha:** 26 de August de 2025

## 📈 Estadísticas Generales

- ✅ **Consultas válidas:** 274
- ❌ **Consultas inválidas:** 62
- 📁 **Módulos con problemas:** 13
- 📊 **Total consultas analizadas:** 336

## 🎯 Priorización por Módulo

| Posición | Módulo | Cantidad de Errores | Prioridad |
|----------|--------|--------------------|-----------|
| 1 | `utils/database_optimizer.py` | 16 | 🔥 ALTA |
| 2 | `core/auth_manager.py` | 8 | ⚠️ MEDIA |
| 3 | `modules/vidrios` | 6 | ⚠️ MEDIA |
| 4 | `core/audit_system.py` | 4 | 🟡 BAJA |
| 5 | `core/audit_trail.py` | 4 | 🟡 BAJA |
| 6 | `modules/herrajes` | 4 | 🟡 BAJA |
| 7 | `modules/notificaciones` | 4 | 🟡 BAJA |
| 8 | `modules/usuarios` | 4 | 🟡 BAJA |
| 9 | `utils/intelligent_cache_manager.py` | 4 | 🟡 BAJA |
| 10 | `models/productos_model.py` | 2 | 🟡 BAJA |

## 📁 Detalle por Módulo

### 📁 utils/database_optimizer.py
**Errores encontrados:** 16

**Tipos de errores:**
- Tabla inexistente: `SYS`: 10
- Tabla inexistente: `OPTIMIZATION_ACTIONS`: 4
- Tabla inexistente: `QUERY_METRICS`: 2

**Archivos afectados:**
- `rexus/utils/database_optimizer.py`

---

### 📁 core/auth_manager.py
**Errores encontrados:** 8

**Tipos de errores:**
- Tabla inexistente: `AUTH_SESSIONS`: 6
- Tabla inexistente: `AUTH_USERS`: 2

**Archivos afectados:**
- `rexus/core/auth_manager.py`

---

### 📁 modules/vidrios
**Errores encontrados:** 6

**Tipos de errores:**
- Tabla inexistente: `SYSOBJECTS`: 4
- Tabla inexistente: `INFORMATION_SCHEMA`: 2

**Archivos afectados:**
- `rexus/modules/vidrios/model.py`

---

### 📁 core/audit_system.py
**Errores encontrados:** 4

**Tipos de errores:**
- Tabla inexistente: `AUDITORIA_SISTEMA`: 4

**Archivos afectados:**
- `rexus/core/audit_system.py`

---

### 📁 core/audit_trail.py
**Errores encontrados:** 4

**Tipos de errores:**
- Tabla inexistente: `AUDIT_TRAIL`: 4

**Archivos afectados:**
- `rexus/core/audit_trail.py`

---

### 📁 modules/herrajes
**Errores encontrados:** 4

**Tipos de errores:**
- Tabla inexistente: `HERRAJES_INVENTARIO`: 4

**Archivos afectados:**
- `rexus/modules/herrajes/inventario_integration.py`

---

### 📁 modules/notificaciones
**Errores encontrados:** 4

**Tipos de errores:**
- Tabla inexistente: `USUARIOS_NOTIFICACIONES`: 4

**Archivos afectados:**
- `rexus/modules/notificaciones/model.py`

---

### 📁 modules/usuarios
**Errores encontrados:** 4

**Tipos de errores:**
- Tabla inexistente: `PERMISOS_USUARIOS`: 4

**Archivos afectados:**
- `rexus/modules/usuarios/submodules/permissions_manager.py`

---

### 📁 utils/intelligent_cache_manager.py
**Errores encontrados:** 4

**Tipos de errores:**
- Tabla inexistente: `CACHE_ENTRIES`: 4

**Archivos afectados:**
- `rexus/utils/intelligent_cache_manager.py`

---

### 📁 models/productos_model.py
**Errores encontrados:** 2

**Tipos de errores:**
- Tabla inexistente: `SYSOBJECTS`: 2

**Archivos afectados:**
- `rexus/models/productos_model.py`

---

### 📁 modules/inventario
**Errores encontrados:** 2

**Tipos de errores:**
- Tabla inexistente: `INFORMATION_SCHEMA`: 2

**Archivos afectados:**
- `rexus/modules/inventario/submodules/categorias_manager.py`

---

### 📁 modules/mantenimiento
**Errores encontrados:** 2

**Tipos de errores:**
- Tabla inexistente: `SYSOBJECTS`: 2

**Archivos afectados:**
- `rexus/modules/mantenimiento/model.py`

---

### 📁 tools
**Errores encontrados:** 2

**Tipos de errores:**
- Tabla inexistente: `SQLITE_MASTER`: 2

**Archivos afectados:**
- `tools/deploy_production.py`

---

## ⚡ Acciones Recomendadas

1. **Prioridad ALTA** (>= 10 errores): Atacar primero los módulos con más errores
2. **Estandarizar nombres de tablas** según el esquema real de SQL Server
3. **Eliminar consultas de metadatos** de otros SGBD (SQLite, MySQL, etc.)
4. **Verificar columnas** contra el esquema real
5. **Crear tablas faltantes** si son necesarias para la funcionalidad

