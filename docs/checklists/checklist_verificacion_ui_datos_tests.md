# Checklist de Verificación de UI, Datos y Tests

Este checklist guía la revisión detallada de la interfaz de usuario, flujo de datos y tests por cada módulo del sistema.

## Objetivo

- Verificar que los datos se cargan correctamente en la interfaz de usuario
- Asegurar que el usuario recibe feedback visual adecuado durante todas las operaciones
- Comprobar que los datos se guardan correctamente en la base de datos
- Analizar la cobertura de tests y añadir casos de prueba para edge cases

## Procedimiento de Revisión por Módulo

Para cada módulo del sistema, seguir este procedimiento de verificación:

1. **Revisión de UI y carga de datos**
2. **Validación del feedback visual**
3. **Verificación del guardado en base de datos**
4. **Análisis de tests existentes**
5. **Documentación de edge cases**
6. **Recomendaciones de mejora**

---

## Módulo: Usuarios

### 1. Revisión de UI y Carga de Datos

- [ ] **Login**
  - [ ] Verificar que el formulario de login se carga correctamente
  - [ ] Comprobar que los errores de credenciales se muestran adecuadamente
  - [ ] Validar comportamiento con campos vacíos

- [ ] **Registro de Usuario**
  - [ ] Verificar que todos los campos del formulario se muestran correctamente
  - [ ] Comprobar carga de roles/perfiles disponibles
  - [ ] Validar que las validaciones en tiempo real funcionan

- [ ] **Perfil de Usuario**
  - [ ] Verificar que los datos del usuario se cargan correctamente
  - [ ] Comprobar que las imágenes/avatares se muestran correctamente
  - [ ] Validar que los permisos se reflejan adecuadamente en la UI

- [ ] **Listado de Usuarios**
  - [ ] Verificar que la paginación funciona correctamente
  - [ ] Comprobar que los filtros cargan datos adecuados
  - [ ] Validar que la ordenación por columnas funciona

### 2. Feedback Visual

- [ ] **Indicadores de Carga**
  - [ ] Verificar que hay spinners/loaders durante operaciones asíncronas
  - [ ] Comprobar que el sistema muestra el estado de progreso en operaciones largas
  - [ ] Validar que no hay "UI freeze" durante la carga de datos

- [ ] **Mensajes de Éxito/Error**
  - [ ] Verificar que los mensajes de éxito son claros y visibles
  - [ ] Comprobar que los mensajes de error son descriptivos
  - [ ] Validar que los mensajes desaparecen tras tiempo razonable o acción del usuario

- [ ] **Validación en Tiempo Real**
  - [ ] Verificar validación visual de campos (colores, iconos)
  - [ ] Comprobar que las sugerencias de corrección son útiles
  - [ ] Validar que los errores se muestran cerca del campo problemático

### 3. Guardado en Base de Datos

- [ ] **Creación de Usuario**
  - [ ] Verificar que todos los campos se guardan correctamente
  - [ ] Comprobar que el hash de contraseña se almacena (no texto plano)
  - [ ] Validar que los registros de auditoría se crean adecuadamente

- [ ] **Actualización de Usuario**
  - [ ] Verificar que solo se actualizan los campos modificados
  - [ ] Comprobar que se registra quién y cuándo realizó cambios
  - [ ] Validar que no se sobrescriben datos críticos innecesariamente

- [ ] **Eliminación/Desactivación**
  - [ ] Verificar que los usuarios se marcan como inactivos (no eliminar)
  - [ ] Comprobar que se mantiene integridad referencial
  - [ ] Validar que los registros históricos permanecen intactos

### 4. Análisis de Tests Existentes

- [ ] **Tests Unitarios**
  - [ ] Listar tests existentes para el modelo de usuarios
  - [ ] Identificar cobertura actual (métodos/funciones cubiertas)
  - [ ] Encontrar áreas sin cobertura de tests

- [ ] **Tests de Integración**
  - [ ] Verificar tests que comprueban el flujo usuario-controlador-modelo
  - [ ] Identificar escenarios de integración no cubiertos
  - [ ] Analizar tests de interacción entre módulos

- [ ] **Tests de UI**
  - [ ] Revisar tests de interfaz existentes
  - [ ] Identificar flujos de usuario no probados
  - [ ] Evaluar cobertura de componentes de UI

### 5. Edge Cases a Probar

- [ ] **Valores Extremos**
  - [ ] Nombres de usuario muy largos o con caracteres especiales
  - [ ] Contraseñas en el límite de longitud permitida
  - [ ] Direcciones de email en formatos poco comunes pero válidos

- [ ] **Concurrencia**
  - [ ] Múltiples actualizaciones simultáneas del mismo usuario
  - [ ] Registro simultáneo de usuarios con mismo username/email
  - [ ] Navegación rápida entre vistas con datos cacheados

- [ ] **Seguridad**
  - [ ] Intentos de inyección SQL en campos de formularios
  - [ ] XSS en campos de perfil que se muestran a otros usuarios
  - [ ] Manipulación de cookies/tokens de sesión

- [ ] **Rendimiento**
  - [ ] Comportamiento con miles de usuarios en la lista
  - [ ] Carga de perfiles con muchas relaciones/permisos
  - [ ] Búsquedas con resultados muy grandes

### 6. Recomendaciones de Mejora

- [ ] **UI/UX**
  - [ ] _Completar durante la revisión_

- [ ] **Manejo de Datos**
  - [ ] _Completar durante la revisión_

- [ ] **Seguridad**
  - [ ] _Completar durante la revisión_

- [ ] **Tests**
  - [ ] _Completar durante la revisión_

---

## Módulo: Obras

### 1. Revisión de UI y Carga de Datos

- [ ] **Creación de Obra**
  - [ ] Verificar que el formulario carga correctamente todos los campos
  - [ ] Comprobar que los selectores (clientes, tipos) cargan datos completos
  - [ ] Validar que el mapa de ubicación funciona correctamente

- [ ] **Listado de Obras**
  - [ ] Verificar que todas las columnas muestran datos correctos
  - [ ] Comprobar funcionamiento de filtros (estado, cliente, fecha)
  - [ ] Validar que los indicadores de estado son claros y precisos

- [ ] **Detalle de Obra**
  - [ ] Verificar carga de datos generales, materiales y cronograma
  - [ ] Comprobar visualización de documentos adjuntos
  - [ ] Validar que los permisos limitan acciones adecuadamente

- [ ] **Cronograma/Kanban**
  - [ ] Verificar que las etapas se muestran correctamente
  - [ ] Comprobar funcionalidad drag & drop para cambiar etapas
  - [ ] Validar que las fechas estimadas vs. reales son claras

### 2. Feedback Visual

- [ ] **Indicadores de Carga**
  - [ ] Verificar indicadores durante carga de obras con muchos materiales
  - [ ] Comprobar estado de procesos de cambio de etapa
  - [ ] Validar feedback durante carga/descarga de archivos

- [ ] **Alertas y Notificaciones**
  - [ ] Verificar alertas para obras próximas a vencer
  - [ ] Comprobar notificaciones de cambios de estado
  - [ ] Validar notificaciones de asignación/reasignación

- [ ] **Códigos de Color**
  - [ ] Verificar consistencia en códigos de color para estados
  - [ ] Comprobar accesibilidad de combinaciones de colores
  - [ ] Validar que estados críticos destacan visualmente

### 3. Guardado en Base de Datos

- [ ] **Creación de Obra**
  - [ ] Verificar que todos los campos básicos se guardan
  - [ ] Comprobar relaciones con clientes y responsables
  - [ ] Validar generación de códigos/referencias únicas

- [ ] **Actualización de Estado**
  - [ ] Verificar registro de cambios de estado con timestamp
  - [ ] Comprobar actualización de porcentaje de avance
  - [ ] Validar registro de usuario que realiza los cambios

- [ ] **Materiales y Presupuestos**
  - [ ] Verificar guardado de líneas de materiales
  - [ ] Comprobar cálculos de totales y descuentos
  - [ ] Validar actualización de stock al asignar materiales

### 4. Análisis de Tests Existentes

- [ ] **Tests Unitarios**
  - [ ] Listar tests existentes para el modelo de obras
  - [ ] Identificar cobertura de cálculos de presupuestos
  - [ ] Encontrar áreas sin cobertura de tests

- [ ] **Tests de Integración**
  - [ ] Verificar tests del flujo completo de obra
  - [ ] Identificar escenarios de integración con materiales/inventario
  - [ ] Analizar tests de interacción con módulo de clientes

- [ ] **Tests de UI**
  - [ ] Revisar tests del Kanban/cronograma
  - [ ] Identificar pruebas de filtros y búsquedas
  - [ ] Evaluar cobertura de componentes visuales

### 5. Edge Cases a Probar

- [ ] **Valores Extremos**
  - [ ] Obras con cientos de líneas de materiales
  - [ ] Descripciones o direcciones extremadamente largas
  - [ ] Fechas en años muy distantes (pasado/futuro)

- [ ] **Concurrencia**
  - [ ] Edición simultánea de la misma obra
  - [ ] Asignación simultánea de materiales escasos
  - [ ] Cambios de estado simultáneos

- [ ] **Casos Especiales**
  - [ ] Obras canceladas y su impacto en materiales reservados
  - [ ] Clientes eliminados con obras activas
  - [ ] Cambios de responsable durante etapas críticas

- [ ] **Rendimiento**
  - [ ] Comportamiento con listados de cientos de obras
  - [ ] Carga de obras con muchos documentos adjuntos
  - [ ] Generación de reportes para muchas obras

### 6. Recomendaciones de Mejora

- [ ] **UI/UX**
  - [ ] _Completar durante la revisión_

- [ ] **Manejo de Datos**
  - [ ] _Completar durante la revisión_

- [ ] **Integración con otros Módulos**
  - [ ] _Completar durante la revisión_

- [ ] **Tests**
  - [ ] _Completar durante la revisión_

---

## Módulo: Inventario

### 1. Revisión de UI y Carga de Datos

- [ ] **Listado de Productos**
  - [ ] Verificar que la tabla muestra todos los campos relevantes
  - [ ] Comprobar que las imágenes de productos cargan correctamente
  - [ ] Validar filtros por categoría, ubicación y estado

- [ ] **Detalle de Producto**
  - [ ] Verificar carga completa de datos y especificaciones
  - [ ] Comprobar visualización de histórico de movimientos
  - [ ] Validar cálculo y visualización de niveles de stock

- [ ] **Gestión de Stock**
  - [ ] Verificar funcionalidad de entrada/salida de stock
  - [ ] Comprobar funcionamiento de escáner de códigos (si aplica)
  - [ ] Validar cálculo automático de cantidades en formularios

- [ ] **Reportes e Informes**
  - [ ] Verificar generación de informes de inventario
  - [ ] Comprobar gráficos de rotación y consumo
  - [ ] Validar exportación de datos en diferentes formatos

### 2. Feedback Visual

- [ ] **Alertas de Stock**
  - [ ] Verificar alertas visuales de stock bajo mínimos
  - [ ] Comprobar indicadores de productos sin movimiento
  - [ ] Validar notificaciones de caducidad próxima

- [ ] **Feedback de Operaciones**
  - [ ] Verificar confirmación visual tras entradas/salidas
  - [ ] Comprobar animaciones durante procesamiento de operaciones
  - [ ] Validar mensajes claros de éxito/error en transferencias

- [ ] **Códigos de Color**
  - [ ] Verificar uso de colores para niveles de stock
  - [ ] Comprobar consistencia de indicadores visuales
  - [ ] Validar accesibilidad para daltonismo

### 3. Guardado en Base de Datos

- [ ] **Creación de Productos**
  - [ ] Verificar almacenamiento de todos los campos
  - [ ] Comprobar generación correcta de códigos únicos
  - [ ] Validar relaciones con categorías y ubicaciones

- [ ] **Movimientos de Stock**
  - [ ] Verificar registro detallado de cada movimiento
  - [ ] Comprobar cálculo correcto del stock actual
  - [ ] Validar registro de usuario, fecha y motivo

- [ ] **Ajustes de Inventario**
  - [ ] Verificar registro de ajustes con justificación
  - [ ] Comprobar funcionamiento de inventarios físicos
  - [ ] Validar trazabilidad de cambios manuales

### 4. Análisis de Tests Existentes

- [ ] **Tests Unitarios**
  - [ ] Listar tests de cálculos de stock
  - [ ] Identificar cobertura de valoración de inventario
  - [ ] Encontrar áreas críticas sin cobertura

- [ ] **Tests de Integración**
  - [ ] Verificar tests de integración con compras/ventas
  - [ ] Identificar pruebas de consistencia de stock
  - [ ] Analizar tests de reserva de stock para obras

- [ ] **Tests de UI**
  - [ ] Revisar tests de formularios de entrada/salida
  - [ ] Identificar pruebas de reportes y filtros
  - [ ] Evaluar cobertura de comportamientos críticos

### 5. Edge Cases a Probar

- [ ] **Valores Extremos**
  - [ ] Productos con cantidades muy grandes
  - [ ] Ajustes negativos que lleven a stock cero
  - [ ] Múltiples movimientos simultáneos del mismo producto

- [ ] **Concurrencia**
  - [ ] Reserva simultánea del mismo stock desde diferentes módulos
  - [ ] Ajustes de inventario durante procesos de salida
  - [ ] Transferencias entre almacenes concurrentes

- [ ] **Casos Especiales**
  - [ ] Comportamiento con productos discontinuados
  - [ ] Manejo de devoluciones parciales
  - [ ] Productos compuestos o kits

- [ ] **Rendimiento**
  - [ ] Comportamiento con miles de productos
  - [ ] Consultas de histórico muy extenso
  - [ ] Generación de reportes completos

### 6. Recomendaciones de Mejora

- [ ] **UI/UX**
  - [ ] _Completar durante la revisión_

- [ ] **Manejo de Datos**
  - [ ] _Completar durante la revisión_

- [ ] **Integración con otros Módulos**
  - [ ] _Completar durante la revisión_

- [ ] **Tests**
  - [ ] _Completar durante la revisión_

---

## Módulo: Herrajes

### 1. Revisión de UI y Carga de Datos

- [ ] **Catálogo de Herrajes**
  - [ ] Verificar visualización de imágenes y especificaciones
  - [ ] Comprobar filtros por tipo, material y proveedor
  - [ ] Validar carga de precios actualizados

- [ ] **Asignación a Obras**
  - [ ] Verificar formulario de asignación
  - [ ] Comprobar cálculo de cantidades según dimensiones
  - [ ] Validar visualización de disponibilidad

- [ ] **Detalle de Herraje**
  - [ ] Verificar ficha técnica completa
  - [ ] Comprobar historial de precios
  - [ ] Validar información de proveedores alternativos

### 2. Feedback Visual

- [ ] **Selección de Herrajes**
  - [ ] Verificar previsualización al seleccionar
  - [ ] Comprobar calculadora de necesidades
  - [ ] Validar mensajes de compatibilidad

- [ ] **Advertencias**
  - [ ] Verificar alertas de incompatibilidad
  - [ ] Comprobar avisos de stock insuficiente
  - [ ] Validar notificaciones de cambios de precio

### 3. Guardado en Base de Datos

- [ ] **Información de Herrajes**
  - [ ] Verificar campos técnicos y comerciales
  - [ ] Comprobar relaciones con proveedores
  - [ ] Validar historial de actualizaciones

- [ ] **Asignación a Obras**
  - [ ] Verificar registro completo de especificaciones
  - [ ] Comprobar actualización de disponibilidad
  - [ ] Validar registro de usuario responsable

### 4. Análisis de Tests Existentes y Edge Cases

- [ ] **Tests**
  - [ ] Analizar cobertura actual
  - [ ] Identificar casos críticos sin pruebas

- [ ] **Edge Cases**
  - [ ] Herrajes descontinuados asignados a obras
  - [ ] Cambios de especificaciones durante obra
  - [ ] Reemplazo de herrajes no disponibles

### 5. Recomendaciones de Mejora
  - [ ] _Completar durante la revisión_

---

## Módulo: Vidrios

### 1. Revisión de UI y Carga de Datos

- [ ] **Catálogo de Vidrios**
  - [ ] Verificar visualización de tipos y características
  - [ ] Comprobar filtros por propiedades (térmicas, acústicas)
  - [ ] Validar carga de precios por m²

- [ ] **Cálculo de Vidrios**
  - [ ] Verificar calculadora de dimensiones y tipos
  - [ ] Comprobar especificaciones de corte y tolerancias
  - [ ] Validar optimización de desperdicios

- [ ] **Asignación a Obras**
  - [ ] Verificar interfaces de selección con dimensiones
  - [ ] Comprobar cálculo de cantidades y desperdicios
  - [ ] Validar restricciones de tamaños máximos/mínimos

### 2. Feedback Visual

- [ ] **Visualización de Cortes**
  - [ ] Verificar diagramas de corte propuestos
  - [ ] Comprobar indicadores de optimización
  - [ ] Validar alertas de limitaciones técnicas

- [ ] **Alertas Técnicas**
  - [ ] Verificar advertencias de espesores inadecuados
  - [ ] Comprobar notificaciones de tratamientos necesarios
  - [ ] Validar información de compatibilidades

### 3. Guardado en Base de Datos

- [ ] **Especificaciones de Vidrios**
  - [ ] Verificar registro de composiciones y tratamientos
  - [ ] Comprobar almacenamiento de propiedades técnicas
  - [ ] Validar historial de precios

- [ ] **Vidrios en Obras**
  - [ ] Verificar registro detallado de medidas y tipos
  - [ ] Comprobar cálculos de superficie y coste
  - [ ] Validar registro de modificaciones

### 4. Análisis de Tests Existentes y Edge Cases

- [ ] **Tests**
  - [ ] Analizar pruebas de cálculo de superficie
  - [ ] Identificar tests de optimización de corte
  - [ ] Evaluar cobertura de validaciones técnicas

- [ ] **Edge Cases**
  - [ ] Vidrios de dimensiones extremas
  - [ ] Combinaciones de tratamientos especiales
  - [ ] Modificaciones post-fabricación

### 5. Recomendaciones de Mejora
  - [ ] _Completar durante la revisión_

---

## Módulo: Pedidos

### 1. Revisión de UI y Carga de Datos

- [ ] **Creación de Pedidos**
  - [ ] Verificar formulario con selección de proveedores
  - [ ] Comprobar búsqueda y selección de productos
  - [ ] Validar cálculos de subtotales y totales

- [ ] **Seguimiento de Pedidos**
  - [ ] Verificar visualización de estado y timeline
  - [ ] Comprobar gestión de recepción parcial
  - [ ] Validar notificaciones de cambios de estado

- [ ] **Historial de Pedidos**
  - [ ] Verificar filtros por proveedor, estado y fechas
  - [ ] Comprobar visualización de documentos asociados
  - [ ] Validar exportación de informes

### 2. Feedback Visual

- [ ] **Estado de Pedidos**
  - [ ] Verificar indicadores claros de estado
  - [ ] Comprobar notificaciones de retrasos
  - [ ] Validar alertas de incidencias

- [ ] **Confirmaciones**
  - [ ] Verificar confirmaciones de envío de pedidos
  - [ ] Comprobar avisos de modificaciones
  - [ ] Validar notificaciones de recepciones

### 3. Guardado en Base de Datos

- [ ] **Pedidos**
  - [ ] Verificar registro completo de datos de contacto
  - [ ] Comprobar líneas de detalle con precios y cantidades
  - [ ] Validar historial de modificaciones

- [ ] **Recepción de Pedidos**
  - [ ] Verificar registro de recepciones parciales
  - [ ] Comprobar actualización automática de inventario
  - [ ] Validar registro de incidencias

### 4. Análisis de Tests Existentes y Edge Cases

- [ ] **Tests**
  - [ ] Analizar cobertura del flujo completo de pedidos
  - [ ] Identificar pruebas de modificaciones y cancelaciones
  - [ ] Evaluar tests de integración con inventario

- [ ] **Edge Cases**
  - [ ] Pedidos parcialmente recibidos y cancelados
  - [ ] Cambios de precios durante pedido en curso
  - [ ] Devoluciones y notas de crédito

### 5. Recomendaciones de Mejora
  - [ ] _Completar durante la revisión_

---

## Módulo: Contabilidad

### 1. Revisión de UI y Carga de Datos

- [ ] **Registro de Facturas**
- [ ] **Gestión de Pagos**
- [ ] **Informes Financieros**

### 2. Feedback Visual

- [ ] **Alertas de Vencimientos**
- [ ] **Indicadores Financieros**

### 3. Guardado en Base de Datos

- [ ] **Transacciones**
- [ ] **Asociación con Obras/Pedidos**

### 4. Análisis de Tests Existentes y Edge Cases

- [ ] **Tests de Cálculos Fiscales**
- [ ] **Edge Cases de Conciliaciones**

### 5. Recomendaciones de Mejora
  - [ ] _Completar durante la revisión_

---

## Módulo: Notificaciones

### 1. Revisión de UI y Carga de Datos

- [ ] **Centro de Notificaciones**
- [ ] **Configuración de Alertas**

### 2. Feedback Visual

- [ ] **Indicadores de Nuevas Notificaciones**
- [ ] **Prioridad Visual**

### 3. Guardado en Base de Datos

- [ ] **Registro de Notificaciones**
- [ ] **Preferencias de Usuario**

### 4. Análisis de Tests Existentes y Edge Cases

- [ ] **Tests de Entrega de Notificaciones**
- [ ] **Edge Cases de Múltiples Notificaciones**

### 5. Recomendaciones de Mejora
  - [ ] _Completar durante la revisión_

---

## Instrucciones de Uso del Checklist

1. **Para cada módulo**:
   - Revisar cada sección marcando los elementos verificados
   - Documentar problemas encontrados y soluciones propuestas
   - Especial atención a edge cases no considerados

2. **Proceso de revisión**:
   - Iniciar sesión con diferentes roles de usuario
   - Probar flujos completos de cada funcionalidad
   - Verificar comportamiento en dispositivos/resoluciones diferentes
   - Probar con conjuntos de datos pequeños y grandes

3. **Documentación**:
   - Documentar todos los problemas en formato detallado
   - Incluir capturas de pantalla de los problemas
   - Proponer soluciones específicas y viables

4. **Priorización**:
   - Alta: Problemas que afectan funcionalidad crítica o datos
   - Media: Problemas que afectan experiencia de usuario
   - Baja: Mejoras cosméticas o optimizaciones menores

## Registro de Hallazgos

| Fecha | Módulo | Elemento | Problema | Solución Propuesta | Prioridad |
|-------|--------|----------|----------|-------------------|-----------|
|       |        |          |          |                   |           |
|       |        |          |          |                   |           |

---

## Historial de Revisiones

| Fecha | Versión | Descripción | Autor |
|-------|---------|-------------|-------|
| 25/06/2025 | 1.0.0 | Versión inicial | Sistema |
|            |        |             |       |
