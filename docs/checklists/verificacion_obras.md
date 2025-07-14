# Checklist de Verificación: Módulo Obras

*Generado el 27/06/2025 basado en análisis preliminar*

## 1. Revisión de UI y Carga de Datos

### Formularios y vistas detectados

#### Vista principal (ObrasView)
- [ ] Verificar que la tabla principal de obras se carga correctamente con todos sus datos
- [ ] Comprobar que los filtros funcionan adecuadamente
- [ ] Validar que la paginación funciona correctamente si hay muchas obras
- [ ] Verificar que el ordenamiento de columnas funciona como se espera

#### Formulario de agregar obra
- [ ] Verificar que todos los campos obligatorios están marcados visualmente
- [ ] Comprobar que las fechas por defecto (+90 días) se calculan correctamente
- [ ] Validar restricciones de entrada (nombres duplicados, valores mínimos/máximos)
- [ ] Verificar que el cliente se puede seleccionar correctamente

#### Formulario de asignación de materiales
- [ ] Verificar que la lista de materiales disponibles se carga correctamente
- [ ] Comprobar que las cantidades se validan adecuadamente
- [ ] Validar que se puede asignar/desasignar materiales correctamente
- [ ] Verificar que se muestra el stock disponible y se actualiza al asignar

#### Vista de cronograma/Kanban
- [ ] Verificar que el Kanban muestra correctamente las obras según su estado
- [ ] Comprobar que se pueden arrastrar y soltar obras entre estados
- [ ] Validar que las fechas y barras de progreso se muestran correctamente
- [ ] Verificar que la exportación a Excel/PDF funciona correctamente

## 2. Feedback Visual

### Operaciones con feedback visual

- [ ] **Agregar obra**
  - [ ] Verificar mensaje de confirmación al agregar obra exitosamente
  - [ ] Comprobar mensaje de error si falla (nombre duplicado, etc.)
  - [ ] Validar que el formulario indica campos inválidos visualmente

- [ ] **Asignar materiales**
  - [ ] Verificar que se muestra feedback al asignar materiales
  - [ ] Comprobar mensaje de alerta si no hay stock suficiente
  - [ ] Validar indicación visual de cantidades inválidas

- [ ] **Cambio de estado**
  - [ ] Verificar que el cambio de estado en Kanban tiene confirmación visual
  - [ ] Comprobar indicadores de progreso al actualizar
  - [ ] Validar mensaje de error si hay bloqueo optimista (OptimisticLockError)

- [ ] **Exportación**
  - [ ] Verificar indicador de progreso durante la exportación
  - [ ] Comprobar mensaje de éxito al completar
  - [ ] Validar mensaje de error si falla la exportación

## 3. Verificación de Operaciones con Base de Datos

### Operaciones SQL detectadas

- [ ] **Alta de obra (agregar_obra)**
  - [ ] Verificar uso de parámetros preparados o funciones de escape
  - [ ] Comprobar validación de datos antes de insertar
  - [ ] Validar uso de utils.sql_seguro para construir queries
  - [ ] Verificar manejo de transacciones para operación atómica

- [ ] **Verificación de obra existente (verificar_obra_existente)**
  - [ ] Verificar sanitización de parámetros de búsqueda
  - [ ] Comprobar que usa listas blancas para columnas/tablas
  - [ ] Validar que no es vulnerable a inyección SQL

- [ ] **Asignación de materiales (asignar_material_a_obra)**
  - [ ] Verificar validación de stock antes de asignar
  - [ ] Comprobar uso de transacciones para mantener integridad
  - [ ] Validar actualización correcta del inventario al asignar

- [ ] **Actualización de estado (actualizar_estado_obra)**
  - [ ] Verificar uso de parámetros preparados
  - [ ] Comprobar manejo de bloqueo optimista
  - [ ] Validar actualización del registro de auditoría

## 4. Análisis de Tests

### Tests existentes

- [ ] **test_agregar_obra**
  - [ ] Verificar que prueba correctamente el caso exitoso
  - [ ] Comprobar test de nombre duplicado
  - [ ] Validar test de datos inválidos
  - [ ] Verificar test de permisos insuficientes

- [ ] **test_asignar_material**
  - [ ] Verificar test de asignación exitosa
  - [ ] Comprobar test de stock insuficiente
  - [ ] Validar test de asignación con datos inválidos

- [ ] **test_cronograma**
  - [ ] Verificar test de agregar etapa
  - [ ] Comprobar test de actualización de fechas
  - [ ] Validar test de exportación

### Edge cases a añadir

- [ ] Test de concurrencia (dos usuarios modificando la misma obra)
- [ ] Test de caracteres especiales en nombres de obra y descripción
- [ ] Test de fechas extremas (muy lejanas o muy cercanas)
- [ ] Test de rendimiento con muchas obras y materiales
- [ ] Test de conexión intermitente a base de datos

## 5. Recomendaciones Específicas

- [ ] Implementar validación más estricta para nombres de obra (evitar caracteres especiales)
- [ ] Mejorar feedback visual al reordenar en el Kanban
- [ ] Añadir indicadores de progreso para operaciones de carga de datos grandes
- [ ] Reforzar manejo de excepciones en operaciones críticas
- [ ] Implementar caché para datos frecuentemente consultados

## 6. Tabla de Registro de Revisión

| Funcionalidad | Revisado por | Fecha | Estado | Observaciones |
|--------------|--------------|-------|--------|---------------|
| Alta de obra | | | | |
| Asignación materiales | | | | |
| Cronograma Kanban | | | | |
| Exportación | | | | |

## 7. Hallazgos específicos

| ID | Componente | Hallazgo | Impacto | Recomendación | Prioridad | Estado |
|----|------------|----------|---------|---------------|-----------|--------|
| | | | | | | |
| | | | | | | |
| | | | | | | |

## 8. Siguientes Pasos

1. Revisar la implementación del decorador PermisoAuditoria
2. Verificar el manejo de OptimisticLockError en todas las operaciones concurrentes
3. Validar el cumplimiento de estándares visuales según docs/estandares_visuales.md
4. Comprobar la correcta implementación del patrón MVC entre model.py, view.py y controller.py
5. Revisar las llamadas a la auditoría para verificar que todas las acciones relevantes se registran
