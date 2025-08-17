# 📋 CHECKLIST PENDIENTES - REXUS.APP

**Última actualización**: 2025-08-17  
**Estado**: Auditado y verificado

---

## ✅ COMPLETADO

### Módulo Usuarios - Archivos Principales
- ✅ **Prints migrados a logger**: controller.py, view.py, model.py, security_features.py (0 prints)
- ✅ **Sistema de logging centralizado**: app_logger.py implementado
- ✅ **Constantes de mensajes**: 20+ constantes creadas en constants.py
- ✅ **Migración de mensajes**: 6 mensajes migrados en security_dialog.py y view.py
- ✅ **Patrón except Exception**: Documentado en docs/patron_except_refactor.md

### Logística - Refactorización Arquitectural
- ✅ **Managers creados**: 696 líneas extraídas (table_manager.py, panel_manager.py, transport_manager.py)
- ✅ **Integración iniciada**: 2 métodos delegados a managers
- ✅ **Progreso**: 32% completado (2,196 → 2,178 líneas)

---

## ⚠️ ALTA PRIORIDAD - PENDIENTE

### 1. **Migrar Prints Restantes a Logger Central**
**Estado**: CRÍTICO - 400+ prints restantes

#### Usuarios/submodules (23 prints verificados)
- `consultas_manager.py`: 7 prints
- `usuarios_manager.py`: 9 prints  
- `autenticacion_manager.py`: 7 prints

#### Otros Módulos (estimado 400+ prints)
- **Vidrios**: ~55 prints (model.py, controller.py, submodules)
- **Logística**: ~44 prints (view.py, model.py, controller.py)
- **Pedidos, Obras, Inventario**: No auditados

**Acción**: Migrar usando patrón con `rexus.utils.app_logger`

### 2. **Reemplazar Except Exception Genérico**
**Estado**: MASIVO - 71 archivos afectados

#### Usuarios
- Controller: 17/19 casos pendientes
- Model: 30+ casos pendientes
- Submodules: 50+ casos pendientes

#### Otros Módulos
- **Total estimado**: 300+ casos en toda la aplicación

**Acción**: Aplicar patrón específico de excepciones (DatabaseError, ValueError, etc.)

### 3. **Consolidar Mensajes Hardcodeados**
**Estado**: EXTENSO - 90%+ pendiente

#### Progreso Actual
- ✅ 20+ constantes creadas en usuarios/constants.py
- ✅ 6/1000+ mensajes migrados

#### Pendiente
- Crear constants.py para cada módulo
- Migrar mensajes de error/warning hardcodeados
- Unificar títulos de ventanas y diálogos

**Acción**: Crear constantes por módulo y migrar sistemáticamente

---

## 🔵 PRIORIDAD MEDIA

### 4. **Completar Refactorización Logística View.py**
**Estado**: 32% completado - EN PROGRESO

#### Progreso
- ✅ Managers creados: 696 líneas extraídas
- ✅ Integración iniciada: 2 métodos delegados
- ⏳ 60+ métodos pendientes de delegación

**Meta**: Reducir de 2,178 líneas a <500 líneas

### 5. **Auditar Módulos Restantes**
**Estado**: Pendiente de auditoría completa

#### Módulos por auditar:
- **Pedidos**: TODOs, lógica de UI mezclada
- **Obras**: Prints, excepts genéricos, mensajes hardcodeados
- **Inventario**: Estado desconocido
- **Herrajes**: Estado desconocido
- **Compras**: Estado desconocido
- **Auditoria**: Estado desconocido
- **Configuracion**: Estado desconocido
- **Mantenimiento**: Estado desconocido

---

## 🔴 PRIORIDAD BAJA

### 6. **Migrar Tests Legacy**
**Estado**: No iniciado
- Eliminar dependencias en shims
- Reescribir tests para usar API real
- Ubicación: `legacy_root/scripts/test/`

### 7. **Implementar Lógica Real en Controladores**
**Estado**: No iniciado
- Reemplazar stubs/shims por implementación funcional
- Ejemplos: `HerrajesController.get_integration_service`

---

## 📈 MÉTRICAS Y ESTRUCTURA

### Estado General: ~10% completado
- **Prints**: 5% migrados (usuarios principales)
- **Except Exception**: 2% corregidos
- **Mensajes**: 1% consolidados
- **Refactorización**: 15% completado

### Scripts de Validación:
```bash
# Contar prints restantes
find rexus/modules -name "*.py" -exec grep -l "print(" {} \; | wc -l

# Contar except Exception
find rexus/modules -name "*.py" -exec grep -l "except Exception" {} \; | wc -l

# Buscar mensajes hardcodeados
grep -r '"Error' rexus/modules --include="*.py" | head -10
```

### Estructura de Archivos Organizada:
```
D:\martin\Rexus.app/
├── main.py                    # Punto de entrada principal
├── requirements.txt           # Dependencias
├── CLAUDE.md                  # Documentación principal del proyecto
├── Checklist pendientes.md    # Este archivo
├── rexus/                     # Código principal
├── docs/                      # 📝 Documentación organizada
│   ├── checklist/             # Checklists archivados
│   ├── patron_except_refactor.md
│   ├── consolidacion_mensajes_progreso.md
│   ├── plan_refactor_logistica_view.md
│   └── progreso_refactor_logistica.md
├── tools/                     # 🛠️ Scripts de desarrollo movidos
│   ├── expert_audit.py
│   ├── fix_code_quality.py
│   ├── migrate_prints_batch.py
│   └── verify_fixes.py
├── project_scripts/           # Scripts de CI/CD
├── legacy_root/               # Archivos históricos
└── logs/                      # Logs de aplicación
```

---

## 🎯 PLAN DE ACCIÓN

### Semana 1: Finalizar Módulo Usuarios
1. Migrar 23 prints de submódulos usuarios
2. Completar except Exception en usuarios (17 casos restantes)
3. Migrar mensajes hardcodeados usuarios (90% restante)

### Semana 2: Módulos Críticos  
1. **Vidrios**: 55 prints + except Exception + mensajes
2. **Logística**: 44 prints + completar refactorización view.py

### Semana 3-4: Auditoría y Correcciones
1. **Pedidos, Obras, Inventario**: Auditoría completa
2. Implementar correcciones identificadas
3. Tests de validación

**Estimación Total**: 4 semanas de trabajo sistemático