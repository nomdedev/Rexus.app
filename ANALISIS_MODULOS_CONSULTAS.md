# 🔍 ANÁLISIS COMPLETO DE CONSULTAS PROBLEMÁTICAS POR MÓDULO

**Fecha:** 26 de agosto de 2025  
**Estado:** ✅ ANÁLISIS DETALLADO COMPLETADO

## 📊 RESUMEN EJECUTIVO

### Estadísticas Generales
- ✅ **Consultas válidas:** 270 (77%)
- ❌ **Consultas inválidas:** 81 (23%)
- 📁 **Módulos con problemas:** 15
- 📊 **Total consultas analizadas:** 351
- 🎯 **Progreso:** Reducido de 109 a 81 errores (25.7% mejora)

## 🎯 PRIORIZACIÓN POR MÓDULO (TOP 10)

| # | Módulo | Errores | Prioridad | Descripción |
|---|--------|---------|-----------|-------------|
| 1 | `scripts` | 16 | 🔥 **CRÍTICA** | Tablas `ORDENES_COMPRA_*` inexistentes |
| 2 | `modules/compras` | 10 | 🔥 **CRÍTICA** | Consultas incompatibles con SQL Server |
| 3 | `utils/database_optimizer.py` | 9 | ⚠️ **ALTA** | Código SQLite en entorno SQL Server |
| 4 | `core/auth_manager.py` | 8 | ⚠️ **ALTA** | Tablas de autenticación incorrectas |
| 5 | `modules/vidrios` | 6 | 🟡 **MEDIA** | ✅ CORREGIDO |
| 6 | `core/audit_system.py` | 4 | 🟡 **MEDIA** | Tabla `AUDITORIA_SISTEMA` inexistente |
| 7 | `core/audit_trail.py` | 4 | 🟡 **MEDIA** | Tabla `AUDIT_TRAIL` inexistente |
| 8 | `modules/herrajes` | 4 | 🟡 **MEDIA** | Tabla `HERRAJES_INVENTARIO` inexistente |
| 9 | `modules/notificaciones` | 4 | 🟡 **MEDIA** | Tabla `USUARIOS_NOTIFICACIONES` inexistente |
| 10 | `modules/usuarios` | 4 | 🟡 **MEDIA** | Tabla `PERMISOS_USUARIOS` inexistente |

## 📁 ANÁLISIS DETALLADO POR MÓDULO

### 🔥 PRIORIDAD CRÍTICA (26 errores total)

#### 1. 📁 scripts (16 errores)
**Archivos afectados:**
- `scripts/fix_detalle_model.py`

**Problemas identificados:**
- ❌ `ORDENES_COMPRA_DETALLES` (14 errores) → ✅ Debe ser `detalle_compras`
- ❌ `ORDENES_COMPRA` (2 errores) → ✅ Debe ser `pedidos_compra`

**Impacto:** CRÍTICO - Scripts de migración y corrección
**Acción requerida:** Reemplazar TODAS las referencias de tablas

#### 2. 📁 modules/compras (10 errores)
**Archivos afectados:**
- `rexus/modules/compras/inventory_integration.py`
- `rexus/modules/compras/model.py`
- `rexus/modules/compras/model_clean.py`
- `rexus/modules/compras/pedidos/model.py`

**Problemas identificados:**
- ❌ `INFORMATION_SCHEMA` (4 errores) → ✅ Usar `sys.tables` SQL Server
- ❌ `SYSOBJECTS` (4 errores) → ✅ Usar `sys.objects` SQL Server
- ❌ `PRODUCTOS_COMPRAS` (2 errores) → ✅ Verificar tabla correcta

**Impacto:** CRÍTICO - Módulo completo de compras
**Acción requerida:** Migrar de consultas genéricas a SQL Server específico

### ⚠️ PRIORIDAD ALTA (17 errores total)

#### 3. 📁 utils/database_optimizer.py (9 errores)
**Problemas identificados:**
- ❌ `SQLITE_MASTER` (5 errores) → ✅ Usar `sys.tables` SQL Server
- ❌ `QUERY_METRICS` (2 errores) → ✅ Crear tabla o usar alternativa
- ❌ `OPTIMIZATION_ACTIONS` (2 errores) → ✅ Crear tabla o usar alternativa

**Impacto:** ALTO - Optimización de rendimiento
**Acción requerida:** Reescribir completamente para SQL Server

#### 4. 📁 core/auth_manager.py (8 errores)
**Problemas identificados:**
- ❌ `AUTH_SESSIONS` (6 errores) → ✅ Usar `sesiones`
- ❌ `AUTH_USERS` (2 errores) → ✅ Usar `usuarios`

**Impacto:** ALTO - Sistema de autenticación
**Acción requerida:** Actualizar referencias de tablas

### 🟡 PRIORIDAD MEDIA (24 errores total)

#### 5. 📁 modules/vidrios (6 errores) ✅ **CORREGIDO**
- ✅ `VIDRIOS_OBRA` → Corregido a `vidrios_por_obra`
- ✅ Consultas de metadatos eliminadas

#### 6-10. Otros módulos (4 errores cada uno)
**Problemas comunes:**
- Tablas de tracking inexistentes
- Referencias a sistemas de auditoría no implementados
- Tablas de relación faltantes

## ✅ CORRECCIONES YA COMPLETADAS

### ✅ Fase 1: Problemas de Esquema (COMPLETADA)
1. **sessions_manager.py**: `is_active` → `activa`
2. **detalle_model.py**: `ordenes_compra_detalles` → `detalle_compras`
3. **inventory_integration.py**: Múltiples correcciones de tablas
4. **vidrios/model.py**: `VIDRIOS_OBRA` → `vidrios_por_obra`
5. **productos_model.py**: `PRODUCTOS_MOVIMIENTOS` → `movimientos_inventario`
6. **inventory/model.py**: `HISTORIAL_PRECIOS` → `historial`

**Resultado:** 28 consultas corregidas exitosamente

## 🚀 PLAN DE ACCIÓN INMEDIATO

### Siguiente Sesión: Atacar Prioridad Crítica
1. **scripts/fix_detalle_model.py** (16 errores)
   - Buscar y reemplazar: `ORDENES_COMPRA_DETALLES` → `detalle_compras`
   - Buscar y reemplazar: `ORDENES_COMPRA` → `pedidos_compra`
   
2. **modules/compras** (10 errores)
   - Eliminar todas las consultas `INFORMATION_SCHEMA`
   - Eliminar todas las consultas `SYSOBJECTS`
   - Reemplazar por equivalentes SQL Server

### Meta Inmediata
**Objetivo:** Reducir de 81 a menos de 55 errores (35% reducción adicional)

## 🛠️ HERRAMIENTAS DE VALIDACIÓN

### Tests Automatizados Disponibles
- ✅ `tests/test_database_schema_validation.py` - Validación completa
- ✅ `analyze_queries_by_module.py` - Análisis por módulo
- ✅ Conexión directa a SQL Server para validación real-time

### Comando de Verificación
```bash
# Análisis completo
python analyze_queries_by_module.py

# Validación específica
python -m pytest tests/test_database_schema_validation.py::TestDatabaseSchema::test_embedded_queries_validation -v
```

## 📈 MÉTRICAS DE ÉXITO

- **Estado inicial:** 109 consultas inválidas ❌
- **Estado actual:** 81 consultas inválidas ⚠️
- **Consultas corregidas:** 28 ✅
- **Progreso total:** 25.7% ✅
- **Meta final:** 0 consultas inválidas 🎯

---

**✨ Conclusión:** El análisis está completo y tenemos una hoja de ruta clara. Los módulos están priorizados por impacto y cantidad de errores. ¡Listos para continuar con las correcciones sistemáticas!
