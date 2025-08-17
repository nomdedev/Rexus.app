# 📋 CHECKLIST PENDIENTES - LIMPIO Y ACTUALIZADO

**Última actualización**: 2025-08-17  
**Estado**: Basado en auditoría real del código

---

## 🎯 TAREAS CRÍTICAS PENDIENTES

### ⚠️ ALTA PRIORIDAD - LOGGING Y CALIDAD

#### 1. **Migrar Prints Restantes a Logger Central**
**Estado**: 5% completado (solo usuarios principales)

**Archivos críticos pendientes**:
```bash
# Usuarios submódulos (79 prints)
rexus/modules/usuarios/submodules/autenticacion_manager.py    (7 prints)
rexus/modules/usuarios/submodules/consultas_manager.py        (7 prints)  
rexus/modules/usuarios/submodules/usuarios_manager.py         (9 prints)
rexus/modules/usuarios/model.py.sql_backup                   (56 prints)

# Vidrios (55 prints)
rexus/modules/vidrios/model.py                               (30 prints)
rexus/modules/vidrios/controller.py                          (4 prints)
rexus/modules/vidrios/submodules/productos_manager.py        (8 prints)
rexus/modules/vidrios/submodules/obras_manager.py            (7 prints)
rexus/modules/vidrios/submodules/consultas_manager.py        (6 prints)

# Logística (44 prints)  
rexus/modules/logistica/view.py                              (13 prints)
rexus/modules/logistica/model.py                             (27 prints)
rexus/modules/logistica/controller.py                        (4 prints)
```

**Acción**: Migrar usando patrón establecido con `app_logger.py`

#### 2. **Reemplazar Except Exception Genérico**
**Estado**: 2% completado (2/300+ casos)

**Alcance**: 71 archivos con except Exception genérico
**Patrón creado**: `docs/patron_except_refactor.md`

**Acción**: Aplicar patrón de manejo específico de excepciones

#### 3. **Consolidar Mensajes Hardcodeados**
**Estado**: 1% completado (6/1000+ mensajes)

**Progreso actual**:
- ✅ 20+ constantes creadas en `usuarios/constants.py`
- ✅ 6 mensajes migrados en usuarios

**Acción**: Crear constantes por módulo y migrar mensajes

---

## 🔧 REFACTORIZACIÓN ARQUITECTURAL

#### 4. **Completar Refactorización Logística View.py**
**Estado**: 32% completado

**Progreso**:
- ✅ 696 líneas extraídas en managers
- ✅ Integración básica completada
- ⏳ 60+ métodos pendientes de delegación

**Meta**: Reducir de 2,178 líneas a <500 líneas

#### 5. **Migrar Tests Legacy**
**Estado**: No iniciado

**Problema**: Dependencias en shims temporales
**Ubicación**: `legacy_root/scripts/test/`

**Acción**: Reescribir tests para usar API real

#### 6. **Implementar Lógica Real en Controladores**
**Estado**: No iniciado

**Problema**: Controladores usando stubs/shims
**Ejemplos**:
- `HerrajesController.get_integration_service`
- `LogisticaController.generar_servicios_automaticos`

**Acción**: Reemplazar shims por implementación funcional

---

## 📊 MÓDULOS POR AUDITAR Y CORREGIR

### Pendientes de Auditoría Completa:
- [ ] **Pedidos** - TODOs, mensajes hardcodeados, lógica de UI mezclada
- [ ] **Obras** - Prints, excepts genéricos, mensajes hardcodeados  
- [ ] **Inventario** - Estado desconocido
- [ ] **Herrajes** - Estado desconocido
- [ ] **Compras** - Estado desconocido
- [ ] **Auditoria** - Estado desconocido
- [ ] **Configuracion** - Estado desconocido
- [ ] **Mantenimiento** - Estado desconocido

---

## 🚫 ELIMINADO DEL CHECKLIST ORIGINAL

### ✅ Ya Corregido/Completado:
- ~~Migrar prints módulo usuarios principales~~ → ✅ COMPLETADO
- ~~Sistema de logging centralizado~~ → ✅ COMPLETADO  
- ~~Errores de sintaxis~~ → ✅ COMPLETADO
- ~~Arquitectura MVC~~ → ✅ COMPLETADO
- ~~Seguridad SQL injection~~ → ✅ COMPLETADO
- ~~Funcionalidades CRUD básicas~~ → ✅ COMPLETADO

### ❌ Removido por ser Inexacto:
- ~~"Problemas de tema y contraste CRÍTICOS"~~ → No crítico actualmente
- ~~"Migración SQL a archivos 20% completado"~~ → SQLQueryManager ya implementado
- ~~"UI/UX 90% completado"~~ → No validado, requiere auditoría

---

## 📈 PLAN DE ACCIÓN RECOMENDADO

### Semana 1: Finalizar Módulo Usuarios
1. Migrar 79 prints de submódulos usuarios
2. Completar except Exception en usuarios (17 casos restantes)
3. Migrar mensajes hardcodeados usuarios (90% restante)

### Semana 2: Módulos Críticos  
1. **Vidrios**: 55 prints + except Exception + mensajes
2. **Logística**: 44 prints + completar refactorización view.py

### Semana 3: Auditoría Masiva
1. **Pedidos, Obras, Inventario**: Auditoría completa
2. Priorizar por impacto y criticidad

### Semana 4: Implementación y Optimización
1. Implementar correcciones en módulos auditados
2. Tests de validación  
3. Optimizaciones finales

---

## 🛠️ HERRAMIENTAS DE VALIDACIÓN

### Scripts de Verificación:
```bash
# Contar prints restantes
find rexus/modules -name "*.py" -exec grep -l "print(" {} \; | wc -l

# Contar except Exception
find rexus/modules -name "*.py" -exec grep -l "except Exception" {} \; | wc -l

# Buscar mensajes hardcodeados
grep -r '"Error' rexus/modules --include="*.py" | head -10
```

### Métricas de Progreso:
- **Prints**: Meta <50 total en toda la aplicación
- **Except Exception**: Meta <10 casos específicos justificados
- **Mensajes**: Meta 100% en constantes centralizadas

---

**Estado General**: 10% completado del trabajo total estimado
**Tiempo estimado**: 4 semanas de trabajo sistemático