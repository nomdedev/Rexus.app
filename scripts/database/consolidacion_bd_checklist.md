# Checklist de Consolidación de Base de Datos - Rexus.app

## 📋 Resumen del Proyecto
**Objetivo**: Consolidar ~45 tablas fragmentadas en ~15 tablas principales para eliminar duplicación de datos y simplificar el mantenimiento.

**Beneficios esperados**:
- ✅ 67% reducción en número de tablas
- ✅ 40-50% reducción en tamaño de BD
- ✅ Eliminación de datos duplicados
- ✅ Mantenimiento simplificado

---

## 🚀 FASE 1: Consolidación del Core (Tablas Principales)

### 1.1 Crear Tabla `productos` (Inventario Consolidado)
- [ ] **Crear tabla `productos`** con estructura completa
  - Categorías: PERFIL, HERRAJE, VIDRIO, MATERIAL
  - Campos de stock unificados
  - Propiedades físicas y comerciales
  - Control de versiones y auditoría
- [ ] **Crear índices** para optimización de consultas
- [ ] **Crear triggers** para actualización automática de stock

### 1.2 Migración de Datos a `productos`
- [ ] **Migrar `inventario_perfiles`** → `productos` (categoría: PERFIL)
  - Mapear campos existentes
  - Convertir datos de stock
  - Preservar códigos y descripciones
- [ ] **Migrar `herrajes`** → `productos` (categoría: HERRAJE)
  - Consolidar información de herrajes
  - Migrar especificaciones técnicas
- [ ] **Migrar `vidrios`** → `productos` (categoría: VIDRIO)
  - Transferir tipos y características
  - Mantener relaciones con obras
- [ ] **Migrar `materiales`** → `productos` (categoría: MATERIAL)
  - Consolidar materiales adicionales
- [ ] **Verificar integridad** de datos migrados

### 1.3 Crear Tabla `auditoria` (Sistema Unificado)
- [ ] **Crear tabla `auditoria`** consolidada
  - Niveles: INFO, WARNING, ERROR, CRITICAL
  - Categorías: SISTEMA, USUARIO, NEGOCIO, SEGURIDAD
  - Campos JSON para cambios de datos
- [ ] **Migrar datos** de tablas existentes:
  - `auditoria_sistema` → `auditoria`
  - `logs_usuarios` → `auditoria`
  - `auditoria_log` → `auditoria`
- [ ] **Crear índices** para consultas por fecha/usuario/módulo

---

## 🔄 FASE 2: Consolidación de Operaciones

### 2.1 Sistema Unificado de Pedidos
- [ ] **Crear tabla `pedidos`** consolidada
  - Tipos: COMPRA, VENTA, INTERNO, OBRA
  - Estados unificados
  - Campos financieros completos
- [ ] **Crear tabla `pedidos_detalle`** 
  - Relación con `productos`
  - Cantidades y precios
  - Seguimiento de entregas
- [ ] **Migrar datos** de sistemas existentes:
  - `pedidos` + `pedidos_detalle` → nueva estructura
  - `pedidos_compra` + `detalle_pedido` → nueva estructura
  - `compras` + `detalle_compras` → nueva estructura

### 2.2 Relaciones Producto-Obra Unificadas
- [ ] **Crear tabla `productos_obra`**
  - Reemplaza: `materiales_por_obra`, `herrajes_obra`, `vidrios_obra`
  - Campos unificados para asignaciones
  - Control de estados y cantidades
- [ ] **Migrar asignaciones existentes**
  - Consolidar todas las relaciones producto-obra
  - Mantener historial de asignaciones

### 2.3 Movimientos de Inventario Unificados
- [ ] **Crear tabla `movimientos_inventario`**
  - Tipos: ENTRADA, SALIDA, AJUSTE, RESERVA, LIBERACION
  - Referencias a pedidos y obras
  - Trazabilidad completa
- [ ] **Migrar movimientos existentes**
  - Consolidar historial de `movimientos_stock`
  - Preservar trazabilidad

---

## 💻 FASE 3: Actualización de Código

### 3.1 Actualizar Modelos Python
- [ ] **InventarioModel** → usar tabla `productos`
  - Actualizar queries para categoría PERFIL
  - Modificar métodos de búsqueda y filtrado
  - Actualizar gestión de stock
- [ ] **HerrajesModel** → usar tabla `productos`
  - Filtrar por categoría HERRAJE
  - Mantener funcionalidad específica
- [ ] **VidriosModel** → usar tabla `productos`
  - Filtrar por categoría VIDRIO
  - Conservar lógica de negocio
- [ ] **PedidosModel** → usar tablas consolidadas
  - Actualizar queries de pedidos
  - Modificar lógica de detalles
- [ ] **ObrasModel** → usar `productos_obra`
  - Actualizar asignaciones de materiales
  - Modificar consultas de materiales por obra

### 3.2 Actualizar Vistas (UI)
- [ ] **InventarioView** - adaptar a nueva estructura
- [ ] **HerrajesView** - mantener funcionalidad con productos
- [ ] **VidriosView** - adaptar filtros por categoría
- [ ] **PedidosView** - usar sistema unificado
- [ ] **ObrasView** - actualizar asignación de materiales

### 3.3 Actualizar Controladores
- [ ] **InventarioController** - lógica de productos
- [ ] **HerrajesController** - filtros por categoría
- [ ] **VidriosController** - manejo unificado
- [ ] **PedidosController** - sistema consolidado
- [ ] **ObrasController** - nuevas asignaciones

---

## 🔧 FASE 4: Testing y Validación

### 4.1 Testing de Funcionalidad
- [ ] **Crear scripts de prueba** para cada módulo
- [ ] **Verificar CRUD operations** en todas las vistas
- [ ] **Probar búsquedas y filtros** con nueva estructura
- [ ] **Validar cálculos** de stock y movimientos
- [ ] **Verificar reportes** y estadísticas

### 4.2 Testing de Performance
- [ ] **Comparar tiempos** de consulta antes/después
- [ ] **Optimizar índices** según patrones de uso
- [ ] **Verificar memoria** y uso de recursos
- [ ] **Probar con datos masivos** (stress testing)

### 4.3 Actualizar Scripts SQL
- [ ] **Actualizar todos los scripts** en `/scripts/sql/`
- [ ] **Modificar queries** para usar nuevas tablas
- [ ] **Actualizar procedures** si existen
- [ ] **Revisar triggers** y constraints

---

## 🧹 FASE 5: Limpieza y Documentación

### 5.1 Eliminación de Tablas Redundantes
- [ ] **Crear backup** completo antes de eliminación
- [ ] **Eliminar tablas redundantes**:
  - `inventario_items`
  - `herrajes_inventario`
  - `materiales`
  - `reservas_stock`
  - `pedidos_compra`
  - `detalle_pedido`
  - `compras`
  - `detalle_compras`
  - `materiales_por_obra`
  - `herrajes_obra`
  - `vidrios_obra`
  - `auditoria_sistema`
  - `logs_usuarios`
  - `auditoria_log`
- [ ] **Verificar** que no hay dependencias activas

### 5.2 Optimización Final
- [ ] **Recrear estadísticas** de tablas
- [ ] **Optimizar índices** basado en uso real
- [ ] **Configurar mantenimiento** automático
- [ ] **Actualizar planes** de backup

### 5.3 Documentación
- [ ] **Actualizar diagrama** de base de datos
- [ ] **Documentar cambios** en API
- [ ] **Crear guía** de migración
- [ ] **Actualizar manuales** de usuario
- [ ] **Documentar nuevas** convenciones de naming

---

## 📊 Criterios de Éxito

### Técnicos
- [ ] Reducción de 67% en número de tablas
- [ ] Reducción de 40-50% en tamaño de BD
- [ ] Eliminación total de datos duplicados
- [ ] Tiempo de consulta mejorado en 30%+

### Funcionales
- [ ] Todas las funcionalidades existentes funcionan
- [ ] No hay pérdida de datos durante migración
- [ ] Interfaces de usuario mantienen funcionalidad
- [ ] Reportes generan datos correctos

### Operacionales
- [ ] Backups más rápidos (menor tamaño)
- [ ] Mantenimiento simplificado
- [ ] Monitoreo más efectivo
- [ ] Troubleshooting más fácil

---

## 🚨 Riesgos y Mitigaciones

### Riesgos Identificados
- **Pérdida de datos** → Backups múltiples antes de cada fase
- **Downtime prolongado** → Migración por fases con rollback
- **Incompatibilidad** → Testing exhaustivo en ambiente dev
- **Performance issues** → Benchmark antes/después

### Plan de Rollback
- [ ] **Backup completo** antes de iniciar
- [ ] **Scripts de rollback** para cada fase
- [ ] **Puntos de verificación** en cada etapa
- [ ] **Procedimiento de emergencia** documentado

---

## 📅 Cronograma Estimado

| Fase | Duración | Dependencias |
|------|----------|--------------|
| Fase 1 | 2-3 días | Análisis completado |
| Fase 2 | 3-4 días | Fase 1 terminada |
| Fase 3 | 4-5 días | Fase 2 validada |
| Fase 4 | 2-3 días | Código actualizado |
| Fase 5 | 1-2 días | Testing completado |

**Total estimado**: 12-17 días laborables

---

## ✅ Checklist de Finalización

- [ ] Todas las fases completadas exitosamente
- [ ] Testing completo realizado
- [ ] Documentación actualizada
- [ ] Equipo capacitado en nueva estructura
- [ ] Monitoreo post-migración configurado
- [ ] Plan de mantenimiento establecido

---

**🔄 Status**: Checklist creado - Listo para iniciar Fase 1

**📋 Próximo paso**: Ejecutar **FASE 1.1** - Crear tabla `productos`