# REPORTE DE CONSULTAS PROBLEMÁTICAS - REXUS.APP
**Fecha:** 26 de agosto de 2025  
**Estado:** ✅ PROGRESO: 81 consultas inválidas (reducido desde 109)

## RESUMEN EJECUTIVO
- ✅ **Consultas válidas:** ~270 (aumentó desde ~242)
- ❌ **Consultas inválidas:** 81 (reducido desde 109)  
- 📊 **Total consultas analizadas:** 351
- 🎯 **Progreso:** 28 consultas corregidas exitosamente

## ✅ CORRECCIONES APLICADAS

### ✅ CORRECCIÓN 1: sessions_manager.py - COMPLETADA
**Problema:** Columna `is_active` no existe en tabla `sesiones`  
**Solución:** Cambiar `is_active` por `activa`  
**Estado:** ✅ Corregida - Todas las referencias actualizadas

### ✅ CORRECCIÓN 2: detalle_model.py - COMPLETADA
**Problema:** Tabla `ordenes_compra` no existe  
**Solución:** Cambiar por `pedidos_compra`  
**Estado:** ✅ Corregida

### ✅ CORRECCIÓN 3: inventory_integration.py - COMPLETADA
**Problema:** Tabla `ordenes_compra` no existe  
**Solución:** Cambiar por `pedidos_compra`  
**Estado:** ✅ Corregida - 3 referencias actualizadas

### ✅ CORRECCIÓN 4: vidrios/model.py - COMPLETADA
**Problema:** Tabla `vidrios_obra` no existe  
**Solución:** Cambiar por `vidrios_por_obra`  
**Estado:** ✅ Corregida - Tabla y referencias actualizadas

### ✅ CORRECCIÓN 5: productos_model.py - COMPLETADA
**Problema:** Tabla `productos_movimientos` no existe  
**Solución:** Cambiar por `movimientos_inventario`  
**Estado:** ✅ Corregida

### ✅ CORRECCIÓN 6: inventario/model.py - COMPLETADA
**Problema:** Tabla `historial_precios` no existe  
**Solución:** Cambiar por `historial`  
**Estado:** ✅ Corregida

---

## CATEGORIZACIÓN DE PROBLEMAS

### 1. TABLAS FALTANTES O INCORRECTAS

#### 1.1 Tablas de Sistema/Auditoría
| Tabla Incorrecta | Tabla Correcta | Archivos Afectados |
|------------------|----------------|-------------------|
| `AUDITORIA_SISTEMA` | `auditoria` | rexus/core/audit_system.py |
| `AUDIT_TRAIL` | `auditoria_cambios` | rexus/core/audit_trail.py |
| `AUTH_SESSIONS` | `sesiones` | rexus/core/auth_manager.py |
| `AUTH_USERS` | `usuarios` | rexus/core/auth_manager.py |

#### 1.2 Tablas de Metadatos (Compatibilidad SGBD)
| Tabla Incorrecta | Problema | Archivos Afectados |
|------------------|----------|-------------------|
| `SYSOBJECTS` | SQL Server específico | rexus/models/productos_model.py, rexus/modules/compras/pedidos/model.py, rexus/modules/mantenimiento/model.py, rexus/modules/vidrios/model.py |
| `INFORMATION_SCHEMA` | No disponible en contexto | rexus/modules/compras/model.py, rexus/modules/vidrios/model.py, rexus/modules/inventario/submodules/categorias_manager.py |
| `SQLITE_MASTER` | SQLite específico | rexus/utils/database_optimizer.py, tools/deploy_production.py |

#### 1.3 Tablas de Negocio Faltantes
| Tabla Incorrecta | Tabla Correcta Sugerida | Archivos Afectados |
|------------------|-------------------------|-------------------|
| `ORDENES_COMPRA` | `pedidos_compra` | rexus/modules/compras/detalle_model.py, rexus/modules/compras/inventory_integration.py |
| `VIDRIOS_OBRA` | `vidrios_por_obra` | rexus/modules/vidrios/model.py |
| `HERRAJES_INVENTARIO` | `herrajes` (usar stock) | rexus/modules/herrajes/inventario_integration.py |
| `PRODUCTOS_MOVIMIENTOS` | `movimientos_inventario` | rexus/models/productos_model.py |
| `HISTORIAL_PRECIOS` | `libro_contable` | rexus/modules/inventario/model.py |
| `USUARIOS_NOTIFICACIONES` | Crear nueva tabla | rexus/modules/notificaciones/model.py |
| `PERMISOS_USUARIOS` | `usuarios_permisos` | rexus/modules/usuarios/submodules/permissions_manager.py |
| `PRODUCTOS_COMPRAS` | `productos` | rexus/modules/compras/inventory_integration.py |

#### 1.4 Tablas de Cache/Performance
| Tabla Incorrecta | Acción Requerida | Archivos Afectados |
|------------------|------------------|-------------------|
| `CACHE_ENTRIES` | Crear tabla cache | rexus/utils/intelligent_cache_manager.py |
| `QUERY_METRICS` | Crear tabla métricas | rexus/utils/database_optimizer.py |
| `OPTIMIZATION_ACTIONS` | Crear tabla optimización | rexus/utils/database_optimizer.py |

### 2. COLUMNAS FALTANTES O INCORRECTAS

#### 2.1 Columnas de Estado/Activación
| Columna Incorrecta | Columna Correcta | Tabla | Archivos Afectados |
|--------------------|------------------|-------|-------------------|
| `is_active` | `activo` | `sesiones` | rexus/modules/usuarios/submodules/sessions_manager.py |

---

## PLAN DE CORRECCIÓN

### FASE 1: CORRECCIONES INMEDIATAS (Tablas Existentes)
1. **Corregir nombres de tablas principales**
   - `ORDENES_COMPRA` → `pedidos_compra`
   - `VIDRIOS_OBRA` → `vidrios_por_obra`
   - `PRODUCTOS_MOVIMIENTOS` → `movimientos_inventario`

2. **Corregir nombres de columnas**
   - `is_active` → `activo` en tabla `sesiones`

### FASE 2: ELIMINACIÓN DE DEPENDENCIAS INCOMPATIBLES
1. **Eliminar consultas de metadatos específicas de SGBD**
   - Remover `SYSOBJECTS`, `INFORMATION_SCHEMA`, `SQLITE_MASTER`
   - Implementar verificaciones alternativas

### FASE 3: CREACIÓN DE TABLAS FALTANTES
1. **Tablas de auditoría y logs**
   - Crear `auditoria_sistema` o mapear a `auditoria`
   - Crear `audit_trail` o mapear a `auditoria_cambios`

2. **Tablas de funcionalidades extendidas**
   - `usuarios_notificaciones`
   - Tablas de cache y métricas

### FASE 4: VERIFICACIÓN Y TESTING
1. Re-ejecutar test de validación
2. Verificar funcionalidad de módulos corregidos

---

## LISTADO DETALLADO DE CORRECCIONES

### CORRECCIÓN 1: rexus/modules/usuarios/submodules/sessions_manager.py
**Problema:** Columna `is_active` no existe  
**Corrección:** Cambiar `is_active` por `activo`  
**Líneas afectadas:** Múltiples consultas WHERE con `is_active = 1`

### CORRECCIÓN 2: rexus/modules/compras/detalle_model.py
**Problema:** Tabla `ORDENES_COMPRA` no existe  
**Corrección:** Cambiar por `pedidos_compra`  
**Líneas afectadas:** UPDATE queries

### CORRECCIÓN 3: rexus/modules/vidrios/model.py
**Problema:** Tabla `VIDRIOS_OBRA` no existe  
**Corrección:** Cambiar por `vidrios_por_obra`  
**Líneas afectadas:** JOIN y UPDATE queries

### CORRECCIÓN 4: rexus/models/productos_model.py
**Problema:** Tabla `PRODUCTOS_MOVIMIENTOS` no existe  
**Corrección:** Cambiar por `movimientos_inventario`  
**Líneas afectadas:** INSERT queries

### CORRECCIÓN 5: rexus/core/auth_manager.py
**Problema:** Tabla `AUTH_USERS` no existe  
**Corrección:** Ya corregido a `usuarios`, verificar pendientes

---

## PRIORIDADES DE CORRECCIÓN

### 🔴 ALTA PRIORIDAD (Funcionalidad Crítica)
1. Sesiones de usuario (`is_active` → `activo`)
2. Compras (`ORDENES_COMPRA` → `pedidos_compra`)
3. Autenticación (`AUTH_*` → tablas reales)

### 🟡 MEDIA PRIORIDAD (Funcionalidad Extendida)
1. Vidrios (`VIDRIOS_OBRA` → `vidrios_por_obra`)
2. Inventario (`PRODUCTOS_MOVIMIENTOS` → `movimientos_inventario`)
3. Notificaciones (crear `usuarios_notificaciones`)

### 🟢 BAJA PRIORIDAD (Optimización)
1. Métricas y cache (crear tablas faltantes)
2. Consultas de metadatos (eliminar dependencias específicas)

---

**Siguiente paso:** Comenzar con correcciones de alta prioridad, archivo por archivo.
