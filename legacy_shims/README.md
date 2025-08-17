# 🗂️ Legacy Shims Directory

**Fecha:** 2025-08-17  
**Estado:** Archivos temporales marcados para eliminación

## 📋 Propósito

Este directorio contiene archivos temporales (shims, stubs, placeholders) que fueron creados durante el desarrollo y migración del sistema. Están organizados aquí para facilitar su eventual eliminación.

## 📁 Organización

### `original_stubs/`
Contiene archivos stub originales del directorio `legacy_root/original_root/stubs/`:
- `aplicar_estilos_premium.py` - Script de aplicación de estilos (completado)
- `cleanup_duplicates.py` - Script de limpieza de duplicados (completado)
- `expert_audit.py` - Script de auditoría experta (completado)
- `fix_code_quality.py` - Script de mejora de calidad (completado)
- `fix_syntax_errors.py` - Script de corrección de sintaxis (completado)

## ⚠️ Plan de Eliminación

### Fase 1: Identificación (Completada ✅)
- [x] Identificar todos los archivos shim/stub en el proyecto
- [x] Mover archivos a `legacy_shims/`
- [x] Documentar dependencias y referencias

### Fase 2: Reemplazo (En Progreso 🔄)
- [x] Reemplazar funciones shim por implementaciones reales
- [x] Migrar tests legacy que dependían de shims
- [x] Validar que no hay referencias activas a estos archivos

### Fase 3: Eliminación (Próxima 📅)
**Fecha objetivo:** 2025-09-01

Antes de eliminar, verificar:
1. No hay imports a estos archivos en código productivo
2. Tests pasan sin estos archivos
3. No hay referencias en configuración o scripts

### Fase 4: Limpieza Final (Próxima 🧹)
**Fecha objetivo:** 2025-09-15

- Eliminar directorio `legacy_shims/` completo
- Limpiar referencias en documentación
- Actualizar .gitignore si es necesario

## 🔍 Verificación de Dependencias

Para verificar que es seguro eliminar estos archivos:

```bash
# Buscar imports a archivos shim
find . -name "*.py" -exec grep -l "from.*legacy_shims\|import.*legacy_shims" {} \;

# Buscar referencias en tests
find tests/ -name "*.py" -exec grep -l "aplicar_estilos_premium\|cleanup_duplicates\|expert_audit" {} \;

# Verificar que tests pasan sin estos archivos
python -m pytest tests/ -v
```

## 📊 Estado de Reemplazo

| Archivo | Estado | Reemplazado Por | Fecha Completado |
|---------|--------|----------------|------------------|
| `aplicar_estilos_premium.py` | ✅ Completado | `rexus.ui.style_manager` | 2025-08-17 |
| `cleanup_duplicates.py` | ✅ Completado | Limpieza manual | 2025-08-17 |
| `expert_audit.py` | ✅ Completado | `tools/comprehensive_audit.py` | 2025-08-17 |
| `fix_code_quality.py` | ✅ Completado | Refactoring manual | 2025-08-17 |
| `fix_syntax_errors.py` | ✅ Completado | Correcciones aplicadas | 2025-08-17 |

## 🚨 Precauciones

**IMPORTANTE:** No eliminar estos archivos hasta que:

1. Se confirme que ningún script en `project_scripts/` los referencia
2. Se confirme que ningún CI/CD pipeline los usa
3. Se ejecuten todos los tests y pasen sin errores
4. Se revisen manualmente los logs en busca de errores relacionados

## 📞 Contacto

Si tienes dudas sobre si es seguro eliminar algún archivo específico, consulta:
- El log de cambios en `CLAUDE.md`
- Los commits recientes relacionados con refactoring
- La documentación en `legacy_root/docs/`

---

**Recordatorio:** Este directorio es temporal. El objetivo es mantener el código limpio y eliminar dependencias legacy.