# Checklist de Mejoras y Problemas Detectados en Rexus.app

# CHECKLIST DE MEJORAS Y PROBLEMAS PENDIENTES EN REXUS.APP (REORGANIZADO POR PRIORIDAD)

## PRIORIDAD ALTA
### USUARIOS
- [ ] Validar unicidad de nombre de usuario/email en registro
- [ ] Implementar validación en formularios de login y registro
- [ ] Sanitizar todos los datos de entrada (texto libre, email, contraseña)
- [ ] Limitar intentos de login fallidos
- [ ] Validar tokens y entradas en restablecimiento de contraseña
- [ ] Cobertura de tests automatizados (unitarios, edge cases, UI)
### INVENTARIO
- [ ] Migrar todas las consultas SQL a scripts externos en scripts/sql/
- [ ] Usar siempre parámetros en cursor.execute
- [ ] Validar y sanitizar todos los datos de entrada
- [ ] Auditar y testear todos los métodos de acceso a datos
- [ ] Validar que todos los scripts SQL externos usen solo parámetros nombrados y nunca interpolación directa
- [ ] Migrar métodos que construyen queries con strings a scripts externos y parametrizar
- [ ] Validar formato de códigos de producto, precios, cantidades, fechas
- [ ] Cobertura de tests automatizados (unitarios, edge cases, UI)
### HERRAJES
- [ ] Migrar métodos principales a scripts externos y validar parámetros
- [ ] Controladores incompletos o no robustos
- [ ] Cobertura de tests automatizados (unitarios, edge cases, UI)

## PRIORIDAD MEDIA
### USUARIOS
- [ ] Mejorar feedback visual en login y registro (mensajes claros, tooltips, loaders)
- [ ] Refactorizar funciones grandes en el controlador de usuarios
- [ ] Limpieza de imports y dependencias
### INVENTARIO
- [ ] Optimización de rendimiento (consultas SQL, índices, paginación, lazy loading)
- [ ] Refactorización de funciones grandes
- [ ] Limpieza de imports y dependencias
### HERRAJES
- [ ] Optimización de rendimiento y refactorización de funciones grandes
- [ ] Limpieza de imports y dependencias

## PRIORIDAD BAJA
### USUARIOS
- [ ] Documentar el flujo de autenticación y recuperación de contraseña
### INVENTARIO
- [ ] Documentar el modelo de inventario y sus relaciones
### HERRAJES
- [ ] Documentar el modelo de herrajes y sus relaciones

---

## VIDRIOS

### Alta Prioridad
- [ ] Mejorar validación de errores y feedback visual en la UI para operaciones fallidas (si no está implementado en todos los métodos).
- [ ] Revisar cobertura de tests automatizados (unitarios, edge cases, UI).
### Media Prioridad
- [ ] Mejorar tooltips y mensajes en controles y botones de acción.
- [ ] Optimización de rendimiento y refactorización de funciones grandes.
### Baja Prioridad
- [ ] Documentar el modelo de vidrios y sus relaciones.

---

## LOGÍSTICA
### Alta Prioridad
- [ ] Revisar que el método `create_mapa_tab` inicialice correctamente el widget de mapa y dependencias QtWebEngine.
- [ ] Validar que el panel de ubicaciones muestre tooltips explicativos en cada celda.
- [ ] Manejo de excepciones en inicialización y actualización del mapa interactivo.
- [ ] Mejorar feedback visual en la tabla de ubicaciones y controles del mapa.
### Media Prioridad
- [ ] Optimización de rendimiento y refactorización de funciones grandes.
### Baja Prioridad
- [ ] Documentar el modelo de logística y sus relaciones.

---

## CONFIGURACIÓN
### Alta Prioridad
- [ ] Revisar lectura y escritura de parámetros en widgets de configuración.
- [ ] Validar que la carga de configuraciones y parámetros no arroje excepciones.
- [ ] Manejo de errores robusto en lectura de archivos y actualización de parámetros.
- [ ] Cobertura de tests automatizados (unitarios, edge cases, UI).
### Media Prioridad
- [ ] Mejorar tooltips explicativos en widgets de configuración.
- [ ] Limpieza de imports y dependencias.
### Baja Prioridad
- [ ] Documentar el modelo de configuración y sus relaciones.

---

## COMPRAS
### Alta Prioridad
- [ ] Funcionalidades faltantes: proveedores, órdenes, seguimiento.
- [ ] Validar y sanitizar todos los datos de entrada.
- [ ] Cobertura de tests automatizados (unitarios, edge cases, UI).
### Media Prioridad
- [ ] Optimización de rendimiento y refactorización de funciones grandes.
### Baja Prioridad
- [ ] Documentar el modelo de compras y sus relaciones.

---

## MANTENIMIENTO
### Alta Prioridad
- [ ] Funcionalidades faltantes: programación, historial.
- [ ] Validar y sanitizar todos los datos de entrada.
- [ ] Cobertura de tests automatizados (unitarios, edge cases, UI).
### Media Prioridad
- [ ] Optimización de rendimiento y refactorización de funciones grandes.
### Baja Prioridad
- [ ] Documentar el modelo de mantenimiento y sus relaciones.

---

## OBRAS
### Alta Prioridad
- [ ] Validar y sanitizar todos los datos de entrada.
- [ ] Cobertura de tests automatizados (unitarios, edge cases, UI).
### Media Prioridad
- [ ] Optimización de rendimiento y refactorización de funciones grandes.
### Baja Prioridad
- [ ] Documentar el modelo de obras y sus relaciones.

---

## SECCIONES TRANSVERSALES

### SEGURIDAD Y SQL SEGURO
- [ ] Implementar validación de nombres de tablas y columnas en todas las consultas dinámicas.
- [ ] Actualizar TABLAS_PERMITIDAS y COLUMNAS_PERMITIDAS con todas las tablas y columnas del sistema.
- [ ] Reemplazar SELECT/INSERT/UPDATE/DELETE directos por constructores seguros.
- [ ] Verificar que siempre exista cláusula WHERE en DELETE/UPDATE.
- [ ] Validar y sanitizar todos los datos de entrada y salida.
- [ ] Prevenir XSS en todos los campos críticos.
- [ ] Auditar y monitorear accesos y actividad.
- [ ] Configurar análisis automático de seguridad en pipeline CI/CD.
- [ ] Actualizar checklist con cada mejora aplicada.

### VALIDACIÓN Y SANITIZACIÓN DE DATOS
- [ ] Implementar validación en todos los formularios (login, registro, edición, inventario, pedidos, configuración).
- [ ] Sanitizar todos los datos de entrada (texto libre, URLs, JSON, numéricos, fechas).
- [ ] Revisar todos los campos donde se muestra contenido ingresado por el usuario.
- [ ] Aplicar detección y sanitización de XSS en datos críticos.
- [ ] Validar formato de email, teléfono, NIF/CIF, códigos de producto, precios, cantidades, fechas.
- [ ] Validar relaciones (cliente, productos, pedidos).

### EDGE CASES Y TESTS
- [ ] Edge cases: datos límite, condiciones de error, concurrencia, datos corruptos, memoria/disco limitado, red lenta, usuario sin permisos, sesión expirada, múltiples logins, drag & drop, cookies/JS deshabilitado.
- [ ] Tests: unitarios, integración, edge cases, seguridad (inyección SQL, XSS, subida de archivos, concurrencia, errores, mocks).

### USO DE UTILIDADES SQL SEGURAS
- [ ] Revisar documentación de utilidades de seguridad (`utils/sql_seguro.py`, `utils/sanitizador_sql.py`).
- [ ] Instalar dependencias necesarias y ejecutar pruebas unitarias.
- [ ] Reemplazar consultas directas por constructores seguros en todos los módulos.
- [ ] Implementar validación de nombres de tabla y columna en todas las consultas dinámicas.
- [ ] Parametrizar todas las consultas de autenticación, búsqueda y filtros.
- [ ] Sanitizar parámetros de filtros y datos de perfil.
- [ ] Validar y sanitizar correos electrónicos, descripciones, códigos, precios, cantidades.
- [ ] Asegurar que DELETE siempre tenga WHERE.
- [ ] Validar datos de inventario y obras con `FormValidator`.
- [ ] Implementar sanitización HTML en todos los campos de texto libre.

[// --- FIN CHECKLIST UNIFICADO ORDENADO POR MÓDULO Y PRIORIDAD ---]

## 1. Visualización de datos en tablas
- [ ] El método del controlador que debería cargar los datos no se llama al inicializar la vista.
  - *Solución:* Llamar explícitamente a los métodos de carga de datos (`cargar_datos_iniciales`, `cargar_X`) en el constructor o método `set_controller` de cada vista.
- [ ] El método de la vista que debe poblar la tabla no está implementado o no se llama.
  - *Solución:* Implementar siempre un método `cargar_en_tabla` y llamarlo desde el controlador tras obtener los datos.
- [ ] Faltan llamadas a `set_controller` o a métodos como `cargar_datos_iniciales` en la inicialización.
  - *Solución:* Asegurarse de que cada vista reciba y almacene su controlador y que este llame a la carga inicial.
- [ ] Errores silenciosos en los métodos de carga (try/except que oculta el error real).
  - *Solución:* Loggear todas las excepciones y mostrar mensajes de error en la UI.

## 2. Factory de módulos y fallback
- [ ] Varios módulos muestran solo “disponible y funcionando” (fallback).
  - [ ] El nombre del módulo en el botón no coincide exactamente con el esperado en el factory.
    - *Solución:* Unificar nombres y claves en el diccionario del factory y en los botones del sidebar. Usar una función de normalización.
  - [ ] El import de la vista/modelo/controlador falla (archivo faltante, error de sintaxis, etc.).
    - *Solución:* Revisar los imports y agregar tests de importación. Mostrar el error real en la UI.
  - [ ] El método de creación del módulo no está implementado en el factory.
    - *Solución:* Implementar todos los métodos de creación de módulos en el factory.

## 5. Nombres y tildes en los módulos
- [ ] Inconsistencias en nombres de módulos (tildes, mayúsculas/minúsculas) entre el sidebar y el factory.
  - [ ] Unificar nombres y claves en el diccionario del factory y en los botones.
    - *Justificación:* Si el nombre no coincide exactamente, se muestra el fallback.
    - *Solución:* Usar una función de normalización de nombres (sin tildes, minúsculas) tanto en el sidebar como en el factory.

## 6. Falta de feedback visual o mensajes de error
- [ ] No se muestran mensajes claros cuando hay errores de carga de datos o de inicialización.
  - [ ] Agregar mensajes de error visibles en la UI y logs detallados.

## Checklist Único de Mejoras y Problemas Pendientes en Rexus.app (Reorganizado)

### ALTA PRIORIDAD
- [ ] Problema crítico: sistema de seguridad no se inicializa correctamente (`SecurityManager`).
- [ ] Cobertura de tests automatizados (unitarios, integración, edge cases, UI)
- [ ] Sanitización de datos sensibles (contraseñas, logs, auditoría)
- [ ] Auditoría y logs de actividad (registro, limpieza automática, detección de patrones sospechosos)
- [ ] Gestión de errores y excepciones (evitar try/except/pass, logging específico)
- [ ] Controladores incompletos o no robustos (herrajes, vidrios, filtros avanzados)
- [ ] Funcionalidades faltantes en módulos: Compras (proveedores, órdenes, seguimiento), Herrajes (cálculos, validaciones), Mantenimiento (programación, historial)

#### Logística
- [ ] Revisar que el método `create_mapa_tab` inicialice correctamente el widget de mapa y que las dependencias de QtWebEngine estén presentes.
- [ ] Validar que el panel de información de ubicaciones muestre tooltips explicativos en cada celda.
- [ ] Agregar manejo de excepciones en la inicialización y actualización del mapa interactivo.
- [ ] Mejorar feedback visual en la tabla de ubicaciones y controles del mapa.

#### Vidrios
- [ ] Revisar que la tabla de vidrios (`tabla_vidrios`) se conecte correctamente al controlador y que los métodos de actualización manejen errores.
- [ ] Agregar try/except en el método `actualizar_tabla` y mostrar mensajes de error en la UI si ocurre una excepción.
- [ ] Validar que la carga de datos en la tabla no arroje excepciones y que el feedback visual sea claro.
- [ ] Mejorar tooltips y mensajes en los controles y botones de acción.

#### Configuración
- [ ] Revisar la lectura y escritura de parámetros de configuración en los widgets (`widgets_configuracion`).
- [ ] Validar que la carga de configuraciones y parámetros no arroje excepciones.
- [ ] Agregar manejo de errores robusto en la lectura de archivos de configuración y en la actualización de parámetros.
- [ ] Agregar tooltips explicativos en los widgets de configuración para cada parámetro.

### MEDIA PRIORIDAD
- [ ] Optimización de rendimiento (consultas SQL, índices, paginación, lazy loading)
- [ ] Integración y sincronización entre módulos (inventario, obras, compras, etc.)
- [ ] Refactorización de funciones grandes (>50 líneas, muchas variables locales)
- [ ] Limpieza de imports (eliminar no usados, agrupar por tipo)
- [ ] Revisión y optimización de dependencias (`requirements.txt`, versiones, vulnerabilidades)
- [ ] Mejoras de feedback visual (indicadores de carga, accesibilidad, modo oscuro)

### BAJA PRIORIDAD

---

## SEGURIDAD Y SQL SEGURO

### Checklist de problemas de SQL Injection detectados
- [ ] Migrar todas las consultas SQL a scripts externos en scripts/sql/.
- [ ] Usar siempre parámetros en cursor.execute.
- [ ] Validar y sanitizar todos los datos de entrada.
- [ ] Auditar y testear todos los métodos de acceso a datos.
- [ ] Validar que todos los scripts SQL externos usen solo parámetros nombrados y nunca interpolación directa.
- [ ] Revisar todos los métodos que usan f-strings, + o .format para armar consultas.
- [ ] Documentar en el checklist cada método que fue migrado y cada uno pendiente.
- [ ] Implementar validación de nombres de tablas y columnas en todas las consultas dinámicas.
- [ ] Actualizar TABLAS_PERMITIDAS y COLUMNAS_PERMITIDAS con todas las tablas y columnas del sistema.
- [ ] Reemplazar SELECT/INSERT/UPDATE/DELETE directos por constructores seguros.
- [ ] Verificar que siempre exista cláusula WHERE en DELETE/UPDATE.

#### Herrajes
- [ ] obtener_herrajes_por_obra: Usa f-string para nombre de tabla, migrar a script externo y validar tabla.
- [ ] crear_herraje: Inserta en inventario con concatenación de tabla, migrar a script externo.
- [ ] actualizar_herraje: Actualiza inventario con concatenación de tabla, migrar a script externo.
- [ ] obtener_herraje_por_id: LEFT JOIN con concatenación de tabla, migrar a script externo.
- [ ] actualizar_stock: UPDATE con concatenación de tabla, migrar a script externo.
- [ ] buscar_herrajes: Validar uso de LIKE y parámetros, migrar a script externo si es posible.
- [ ] obtener_estadisticas: Revisar todas las consultas agregadas, migrar a scripts externos.
- [ ] eliminar_herraje: Validar que la eliminación lógica use solo scripts externos y parámetros seguros.

#### Inventario
- [ ] Otros métodos detectados por el linter (B608):
    - Métodos que construyen queries con strings (líneas 1434, 1459, 1471, 1483, 1529, 1576, 1626, 1644, 1656, 1668, 1718, 1789, 1845, 1853, 1869, 1881, 2000, 2011, 2137, 2144).
    - Usar scripts externos y parámetros seguros en todos ellos.

#### Vidrios
- [ ] Refactorizar método obtener_todos_vidrios para usar script externo y parámetros seguros.
- [ ] Revisar todos los métodos que construyen queries dinámicamente o usan concatenación de strings.

---

## VALIDACIÓN Y SANITIZACIÓN DE DATOS

- [ ] Implementar validación en todos los formularios (login, registro, edición, inventario, pedidos, configuración).
- [ ] Sanitizar todos los datos de entrada (texto libre, URLs, JSON, numéricos, fechas).
- [ ] Revisar todos los campos donde se muestra contenido ingresado por el usuario.
- [ ] Aplicar detección y sanitización de XSS en datos críticos.
- [ ] Validar unicidad de nombre de usuario/email en registro.
- [ ] Validar tokens y entradas en restablecimiento de contraseña.
- [ ] Validar formato de email, teléfono, NIF/CIF, códigos de producto, precios, cantidades, fechas.
- [ ] Limitar intentos de login fallidos.
- [ ] Validar relaciones (cliente, productos, pedidos).

---

## VERIFICACIÓN POR MÓDULO (estructura, feedback, almacenamiento, tests)

- [ ] Modelo de datos definido correctamente (clases/tablas, relaciones, campos, tipos, restricciones).
- [ ] Conexión a base de datos estable y segura (pool, timeouts, reconexión, cierre adecuado).
- [ ] Operaciones CRUD: Create, Read, Update, Delete (validaciones, transacciones, rollback, soft delete, cascada, auditoría).
- [ ] Validación de entrada y negocio (tipos, rangos, formatos, unicidad, relaciones, estados, permisos, sanitización).
- [ ] Feedback visual: indicadores de carga, estados de interfaz, mensajes de éxito/error/informativos, tooltips, refresh automático/manual.
- [ ] Almacenamiento en BD: consistencia, codificación, precisión, transacciones, deadlocks, rendimiento, manejo de memoria, cache.
- [ ] Seguridad: prevención de inyección SQL, permisos mínimos, auditoría de accesos, encriptación, logs, acceso restringido.
- [ ] Tests: unitarios, integración, edge cases, seguridad (inyección SQL, XSS, subida de archivos, concurrencia, errores, mocks).
- [ ] Edge cases: datos límite, condiciones de error, concurrencia, datos corruptos, memoria/disco limitado, red lenta, usuario sin permisos, sesión expirada, múltiples logins, drag & drop, cookies/JS deshabilitado.
- [ ] Sugerencias y mejoras: rendimiento, UX, seguridad, calidad de código, edge cases adicionales.

---

## VERIFICACIÓN DE UI, DATOS Y TESTS (por módulo)

- [ ] Revisión de UI y carga de datos (login, registro, perfil, listado, paginación, filtros, ordenación).
- [ ] Feedback visual (spinners, loaders, mensajes de éxito/error, validación en tiempo real, tooltips).
- [ ] Guardado en base de datos (consistencia, rollback, validación, auditoría).
- [ ] Análisis de tests existentes y edge cases (strings vacíos, números extremos, fechas límite, arrays vacíos, caracteres especiales).
- [ ] Recomendaciones de mejora (rendimiento, UX, seguridad, calidad de código).

---

## USO DE UTILIDADES SQL SEGURAS

- [ ] Revisar documentación de utilidades de seguridad (`utils/sql_seguro.py`, `utils/sanitizador_sql.py`).
- [ ] Instalar dependencias necesarias y ejecutar pruebas unitarias.
- [ ] Reemplazar consultas directas por constructores seguros en todos los módulos (usuarios, obras, inventario, herrajes, vidrios, pedidos, configuración, auditoría).
- [ ] Implementar validación de nombres de tabla y columna en todas las consultas dinámicas.
- [ ] Parametrizar todas las consultas de autenticación, búsqueda y filtros.
- [ ] Sanitizar parámetros de filtros y datos de perfil.
- [ ] Validar y sanitizar correos electrónicos, descripciones, códigos, precios, cantidades.
- [ ] Asegurar que DELETE siempre tenga WHERE.
- [ ] Validar datos de inventario y obras con `FormValidator`.
- [ ] Implementar sanitización HTML en todos los campos de texto libre.

---

## IMPLEMENTACIÓN DE SEGURIDAD GENERAL

- [ ] Verificar conexiones a base de datos y reemplazar SQL manual por consultas parametrizadas.
- [ ] Implementar time-out en todas las conexiones.
- [ ] Configurar análisis automático de seguridad en pipeline CI/CD.
- [ ] Validar y sanitizar todos los datos de entrada y salida.
- [ ] Prevenir XSS en todos los campos críticos.
- [ ] Auditar y monitorear accesos y actividad.
- [ ] Actualizar checklist con cada mejora aplicada.

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

# Checklist de Verificación por Módulo

Este checklist debe completarse para cada módulo del sistema, verificando la carga de datos, feedback visual, almacenamiento y tests.

## Información del Módulo

- **Nombre del módulo:** _____________
- **Responsable:** _____________
- **Fecha de verificación:** _____________
- **Versión analizada:** _____________

---

## 1. Verificación de Carga de Datos

### 1.1 Estructura de Datos
- [ ] **Modelo de datos definido correctamente**
  - [ ] Clases/tablas principales identificadas
  - [ ] Relaciones entre entidades documentadas
  - [ ] Campos obligatorios y opcionales definidos
  - [ ] Tipos de datos apropiados
  - [ ] Restricciones de integridad implementadas

- [ ] **Conexión a base de datos**
  - [ ] Conexión se establece correctamente
  - [ ] Pool de conexiones configurado (si aplica)
  - [ ] Timeouts apropiados configurados
  - [ ] Reconexión automática implementada
  - [ ] Cierre adecuado de conexiones

### 1.2 Operaciones CRUD
- [ ] **Create (Crear)**
  - [ ] Datos se insertan correctamente
  - [ ] Validaciones aplicadas antes de insertar
  - [ ] Manejo de IDs autogenerados
  - [ ] Transacciones implementadas apropiadamente
  - [ ] Rollback en caso de error

- [ ] **Read (Leer)**
  - [ ] Consultas SELECT funcionan correctamente
  - [ ] Filtros y búsquedas implementados
  - [ ] Paginación funciona (si aplica)
  - [ ] Ordenamiento por columnas funciona
  - [ ] Joins y relaciones cargan correctamente

- [ ] **Update (Actualizar)**
  - [ ] Actualizaciones se aplican correctamente
  - [ ] Solo se actualizan campos modificados
  - [ ] Versionado/concurrencia manejada
  - [ ] Auditoría de cambios implementada
  - [ ] Validaciones aplicadas antes de actualizar

- [ ] **Delete (Eliminar)**
  - [ ] Eliminaciones funcionan correctamente
  - [ ] Soft delete implementado (si aplica)
  - [ ] Eliminación en cascada configurada apropiadamente
  - [ ] Verificación de dependencias antes de eliminar
  - [ ] Auditoría de eliminaciones

### 1.3 Validación de Datos
- [ ] **Validación de entrada**
  - [ ] Tipos de datos validados
  - [ ] Rangos y límites verificados
  - [ ] Formatos específicos validados (email, teléfono, etc.)
  - [ ] Campos requeridos verificados
  - [ ] Sanitización de datos implementada

- [ ] **Validación de negocio**
  - [ ] Reglas de negocio aplicadas
  - [ ] Unicidad verificada donde corresponde
  - [ ] Relaciones válidas verificadas
  - [ ] Estados válidos verificados
  - [ ] Permisos verificados

---

## 2. Verificación de Feedback Visual

### 2.1 Indicadores de Estado
- [ ] **Indicadores de carga**
  - [ ] Spinner/loading mostrado durante operaciones lentas
  - [ ] Cursor cambia a "wait" durante procesamientos
  - [ ] Barras de progreso para operaciones largas
  - [ ] Textos informativos durante esperas
  - [ ] Deshabilitación de controles durante procesamiento

- [ ] **Estados de la interfaz**
  - [ ] Botones reflejan el estado actual
  - [ ] Campos se habilitan/deshabilitan apropiadamente
  - [ ] Pestañas/secciones muestran estado correcto
  - [ ] Contadores se actualizan en tiempo real
  - [ ] Badges/etiquetas reflejan datos actuales

### 2.2 Mensajes al Usuario
- [ ] **Mensajes de éxito**
  - [ ] Confirmación de operaciones exitosas
  - [ ] Detalles relevantes incluidos
  - [ ] Duración apropiada de visualización
  - [ ] Estilo consistente con la aplicación
  - [ ] Posicionamiento apropiado en la UI

- [ ] **Mensajes de error**
  - [ ] Errores mostrados de forma clara
  - [ ] Mensajes específicos y útiles
  - [ ] Sugerencias de corrección incluidas
  - [ ] No se expone información sensible
  - [ ] Logging de errores implementado

- [ ] **Mensajes informativos**
  - [ ] Avisos apropiados para acciones importantes
  - [ ] Confirmaciones antes de operaciones destructivas
  - [ ] Help/tooltips disponibles donde es útil
  - [ ] Mensajes de validación en tiempo real
  - [ ] Información contextual relevante

### 2.3 Actualización de Datos
- [ ] **Refresh automático**
  - [ ] Tablas se actualizan tras modificaciones
  - [ ] Contadores se recalculan automáticamente
  - [ ] Relaciones se refrescan apropiadamente
  - [ ] Cache se invalida cuando es necesario
  - [ ] UI se sincroniza con base de datos

- [ ] **Refresh manual**
  - [ ] Botón de actualizar disponible
  - [ ] F5/Ctrl+R funcionan apropiadamente
  - [ ] Refresh preserva filtros y ordenamiento
  - [ ] Posición actual se mantiene tras refresh
  - [ ] Selecciones se mantienen si es apropiado

---

## 3. Verificación de Almacenamiento en BD

### 3.1 Integridad de Datos
- [ ] **Consistencia**
  - [ ] Datos se almacenan en formato correcto
  - [ ] Codificación de caracteres apropiada (UTF-8)
  - [ ] Decimales con precisión correcta
  - [ ] Fechas en formato estándar
  - [ ] Referencias foráneas válidas

- [ ] **Transacciones**
  - [ ] Operaciones complejas usan transacciones
  - [ ] Rollback funciona correctamente en errores
  - [ ] Aislamiento apropiado configurado
  - [ ] Deadlocks manejados apropiadamente
  - [ ] Timeouts de transacción configurados

### 3.2 Rendimiento
- [ ] **Consultas optimizadas**
  - [ ] Índices apropiados definidos
  - [ ] Consultas N+1 evitadas
  - [ ] JOINs optimizados
  - [ ] LIMIT/TOP usados para grandes datasets
  - [ ] Consultas lentas identificadas y optimizadas

- [ ] **Manejo de memoria**
  - [ ] Resultados grandes paginados
  - [ ] Conexiones cerradas apropiadamente
  - [ ] Cursores liberados tras uso
  - [ ] Memoria liberada tras operaciones grandes
  - [ ] Cache implementado donde es beneficioso

### 3.3 Seguridad
- [ ] **Prevención de inyección SQL**
  - [ ] Consultas parametrizadas usadas
  - [ ] Input sanitizado antes de uso
  - [ ] Validación de nombres de tabla/columna
  - [ ] Escapado apropiado de caracteres especiales
  - [ ] No concatenación directa de SQL

- [ ] **Permisos y acceso**
  - [ ] Usuario de BD tiene permisos mínimos necesarios
  - [ ] Auditoría de accesos implementada
  - [ ] Encriptación de datos sensibles
  - [ ] Logs de seguridad configurados
  - [ ] Acceso a BD desde aplicación únicamente

---

## 4. Verificación de Tests

### 4.1 Cobertura de Tests
- [ ] **Tests unitarios**
  - [ ] Métodos principales probados
  - [ ] Validaciones probadas
  - [ ] Manejo de errores probado
  - [ ] Edge cases cubiertos
  - [ ] Mocks usados apropiadamente

- [ ] **Tests de integración**
  - [ ] Operaciones de BD probadas
  - [ ] Flujos completos probados
  - [ ] Interacción entre módulos probada
  - [ ] APIs externas mockeadas
  - [ ] Configuraciones diferentes probadas

### 4.2 Edge Cases Identificados
- [ ] **Datos límite**
  - [ ] Strings vacíos/null
  - [ ] Números muy grandes/pequeños
  - [ ] Fechas límite (1900, 2100, etc.)
  - [ ] Arrays/listas vacías
  - [ ] Caracteres especiales/unicode

- [ ] **Condiciones de error**
  - [ ] BD no disponible
  - [ ] Timeout de operaciones
  - [ ] Memoria insuficiente
  - [ ] Permisos insuficientes
  - [ ] Datos corruptos

- [ ] **Concurrencia**
  - [ ] Múltiples usuarios simultáneos
  - [ ] Modificaciones concurrentes
  - [ ] Deadlocks
  - [ ] Race conditions
  - [ ] Estados inconsistentes

### 4.3 Tests de Seguridad
- [ ] **Inyección SQL**
  - [ ] Intentos de inyección probados
  - [ ] Validación de input probada
  - [ ] Escapado de caracteres probado
  - [ ] Consultas parametrizadas verificadas
  - [ ] Logs de intentos maliciosos

- [ ] **XSS y otros ataques**
  - [ ] Input malicioso probado
  - [ ] Sanitización verificada
  - [ ] Output encoding verificado
  - [ ] Validación de URLs probada
  - [ ] Subida de archivos segura probada

---

## 5. Sugerencias y Mejoras Identificadas

### 5.1 Mejoras de Rendimiento
- [ ] **Identificadas:**
  - [ ] _________________________________
  - [ ] _________________________________
  - [ ] _________________________________

### 5.2 Mejoras de UX
- [ ] **Identificadas:**
  - [ ] _________________________________
  - [ ] _________________________________
  - [ ] _________________________________

### 5.3 Mejoras de Seguridad
- [ ] **Identificadas:**
  - [ ] _________________________________
  - [ ] _________________________________
  - [ ] _________________________________

### 5.4 Mejoras de Calidad de Código
- [ ] **Identificadas:**
  - [ ] _________________________________
  - [ ] _________________________________
  - [ ] _________________________________

---

## 6. Edge Cases Adicionales Sugeridos

### 6.1 Edge Cases de Datos
- [ ] Probar con base de datos vacía
- [ ] Probar con millones de registros
- [ ] Probar con caracteres especiales (émojis, acentos, símbolos)
- [ ] Probar con nombres muy largos (>255 caracteres)
- [ ] Probar con números negativos donde no se esperan
- [ ] Probar con fechas futuras/pasadas extremas
- [ ] Probar con decimales con muchos dígitos
- [ ] Probar con arrays/listas muy grandes
- [ ] Probar con JSON malformado
- [ ] Probar con archivos muy grandes

### 6.2 Edge Cases de Red/Sistema
- [ ] Probar con conexión de red lenta
- [ ] Probar con pérdida intermitente de conexión
- [ ] Probar con BD en mantenimiento
- [ ] Probar con memoria RAM limitada
- [ ] Probar con espacio en disco limitado
- [ ] Probar con múltiples ventanas/pestañas abiertas
- [ ] Probar con cambio de zona horaria
- [ ] Probar con diferentes resoluciones de pantalla
- [ ] Probar con diferentes navegadores/versiones
- [ ] Probar con antivirus bloqueando archivos

### 6.3 Edge Cases de Usuario
- [ ] Probar navegación muy rápida (clicks múltiples)
- [ ] Probar con usuario sin permisos
- [ ] Probar con sesión expirada
- [ ] Probar con múltiples logins simultáneos
- [ ] Probar con usuario inactivo por mucho tiempo
- [ ] Probar con datos inconsistentes de sesión previa
- [ ] Probar copiar/pegar en campos no esperados
- [ ] Probar drag & drop donde no está permitido
- [ ] Probar con JavaScript deshabilitado
- [ ] Probar con cookies deshabilitadas

---

## Resumen de Verificación

### Estadísticas
- **Total de checks:** _______ / _______
- **Porcentaje completado:** _______ %
- **Críticos faltantes:** _______
- **Mejoras identificadas:** _______

### Estado General
- [ ] ✅ Módulo cumple todos los estándares
- [ ] ⚠️ Módulo necesita mejoras menores
- [ ] ❌ Módulo necesita mejoras críticas

### Próximos Pasos
1. _________________________________
2. _________________________________
3. _________________________________

### Notas Adicionales
_________________________________________________
_________________________________________________
_________________________________________________

---

**Verificador:** _________________ **Fecha:** _________ **Firma:** _________


# Checklist de Validación y Sanitización de Datos de Entrada

Este checklist guía la implementación de validaciones de datos de entrada para prevenir XSS, inyección y otros ataques.

## Requisitos Previos

- [ ] Revisar la documentación de `utils/validador_http.py`
- [ ] Conocer los tipos de datos esperados en cada campo
- [ ] Identificar campos de alto riesgo (campos libres, URLs, código)
- [ ] Ejecutar pruebas unitarias para verificar utilidades de validación

## Implementación por Tipo de Formulario

### Formularios de Autenticación

- [ ] Formulario de Login
  - [ ] Validar longitud de nombre de usuario/email
  - [ ] Detectar patrones XSS en campos
  - [ ] Proteger contra inyección SQL
  - [ ] Limitar intentos de login fallidos

- [ ] Formulario de Registro de Usuario
  - [ ] Validar formato de email
  - [ ] Validar complejidad de contraseña
  - [ ] Sanitizar nombre y apellido
  - [ ] Validar unicidad de nombre de usuario/email

- [ ] Restablecimiento de Contraseña
  - [ ] Validar tokens de restablecimiento
  - [ ] Sanitizar entradas
  - [ ] Validar complejidad de nueva contraseña

### Formularios de Datos Maestros

- [ ] Clientes
  - [ ] Validar formato de email
  - [ ] Validar formato de teléfono
  - [ ] Sanitizar nombre y dirección
  - [ ] Validar código postal

- [ ] Proveedores
  - [ ] Validar formato de email
  - [ ] Validar formato de teléfono
  - [ ] Sanitizar nombres y descripciones
  - [ ] Validar formato de NIF/CIF

- [ ] Productos/Inventario
  - [ ] Validar códigos de producto
  - [ ] Sanitizar descripciones
  - [ ] Validar precios (rango, formato)
  - [ ] Validar existencias y cantidades mínimas

### Formularios de Transacciones

- [ ] Pedidos
  - [ ] Validar cantidades y precios
  - [ ] Sanitizar notas y comentarios
  - [ ] Validar fechas (entrega, producción)
  - [ ] Validar relaciones (cliente, productos)

- [ ] Obras
  - [ ] Validar información de contacto
  - [ ] Sanitizar direcciones y notas
  - [ ] Validar fechas de inicio/fin
  - [ ] Validar presupuestos y costos

- [ ] Pagos
  - [ ] Validar importes
  - [ ] Sanitizar conceptos y referencias
  - [ ] Validar fechas
  - [ ] Validar métodos de pago

### Formularios de Configuración

- [ ] Configuración de Sistema
  - [ ] Validar estrictamente todos los campos
  - [ ] Detectar patrones XSS en valores
  - [ ] Sanitizar todos los textos
  - [ ] Validar URLs y rutas

- [ ] Perfiles de Usuario
  - [ ] Sanitizar campos de perfil
  - [ ] Validar imágenes (tamaño, tipo)
  - [ ] Detectar patrones XSS en biografías
  - [ ] Validar preferencias y configuraciones

## Implementación de Validaciones por Tipo de Dato

### Texto

- [ ] Campos de texto corto
  - [ ] Validar longitud mínima y máxima
  - [ ] Sanitizar HTML si se muestra en UI
  - [ ] Validar patrones específicos si aplica

- [ ] Campos de texto largo
  - [ ] Detectar patrones XSS
  - [ ] Sanitizar HTML completamente
  - [ ] Limitar longitud máxima
  - [ ] Validar formato si aplica (Markdown, etc.)

### Números

- [ ] Enteros
  - [ ] Validar rango permitido
  - [ ] Validar tipo (entero vs decimal)
  - [ ] Sanitizar entrada antes de conversión

- [ ] Decimales
  - [ ] Validar precisión y escala
  - [ ] Validar rango permitido
  - [ ] Sanitizar formato según localización
  - [ ] Validar tipo de dato

### Fechas y Horas

- [ ] Fechas
  - [ ] Validar formato (YYYY-MM-DD)
  - [ ] Validar rango permitido
  - [ ] Validar lógica de negocio (ej: fecha futura/pasada)

- [ ] Horas
  - [ ] Validar formato (HH:MM:SS)
  - [ ] Validar rango permitido
  - [ ] Validar lógica horaria específica

- [ ] Rangos de Fechas
  - [ ] Validar que fecha inicial < fecha final
  - [ ] Validar límites máximos de rango
  - [ ] Sanitizar formatos antes de uso

### Datos Especiales

- [ ] Correos electrónicos
  - [ ] Validar formato según RFC
  - [ ] Validar dominio (opcional)
  - [ ] Sanitizar antes de almacenar

- [ ] URLs
  - [ ] Validar formato
  - [ ] Sanitizar para prevenir ataques de redirección
  - [ ] Validar esquema (http, https)
  - [ ] Validar dominios permitidos si aplica

- [ ] Teléfonos
  - [ ] Validar formato según país
  - [ ] Sanitizar caracteres no numéricos
  - [ ] Validar longitud según formato

- [ ] Documentos de identidad
  - [ ] Validar formato (DNI, NIF, otros)
  - [ ] Validar dígito de control si aplica
  - [ ] Sanitizar formato (espacios, guiones)

## Implementación Técnica

- [ ] Implementar `FormValidator` en todos los controladores
  - [ ] Crear reglas de validación para cada formulario
  - [ ] Definir campos requeridos adecuadamente
  - [ ] Utilizar funciones de validación existentes
  - [ ] Crear funciones de validación personalizadas si es necesario

- [ ] Sanitización
  - [ ] Sanitizar HTML en datos de texto libre
  - [ ] Sanitizar URLs en enlaces
  - [ ] Sanitizar datos JSON en APIs

- [ ] Manejo de Errores
  - [ ] Mostrar errores específicos por campo
  - [ ] Mantener valores válidos al reportar errores
  - [ ] Registrar intentos sospechosos (posibles ataques)
  - [ ] Implementar throttling en APIs y formularios

## Pruebas de Validación

- [ ] Crear casos de prueba con datos válidos
- [ ] Crear casos de prueba con datos inválidos
- [ ] Probar ataques XSS comunes
- [ ] Probar inyección SQL a través de formularios
- [ ] Probar valores límite y casos borde
- [ ] Probar caracteres especiales y codificaciones

## Revisión y Mantenimiento

- [ ] Revisar validaciones después de cambios en modelos de datos
- [ ] Actualizar patrones de validación cuando sea necesario
- [ ] Documentar reglas de validación específicas del negocio
- [ ] Revisar regularmente logs de errores de validación

---

## Registro de Implementación

| Fecha | Formulario | Validaciones Implementadas | Responsable | Observaciones |
|-------|------------|---------------------------|------------|---------------|
|       |            |                           |            |               |
|       |            |                           |            |               |

## Versión del Checklist: 1.0.0
Fecha de creación: 25 de junio de 2025


# Checklist de Uso de Utilidades SQL Seguras

Este checklist guía la implementación y uso de las utilidades SQL seguras en diferentes partes de la aplicación.

## Requisitos Previos

- [ ] Revisar la documentación de utilidades de seguridad
- [ ] Instalar todas las dependencias necesarias
- [ ] Verificar que `utils/sql_seguro.py` y `utils/sanitizador_sql.py` estén disponibles
- [ ] Ejecutar las pruebas unitarias para verificar funcionamiento correcto

## Implementación por Módulo

### Módulo de Usuarios (modules/usuarios)

- [ ] Archivo: `model.py`
  - [ ] Reemplazar consultas directas por `construir_select_seguro`
  - [ ] Implementar `validar_nombre_tabla` para 'users'
  - [ ] Parametrizar consultas de autenticación
  - [ ] Sanitizar entrada de usuario en búsquedas

- [ ] Archivo: `controller.py`
  - [ ] Implementar `FormValidator` para validación
  - [ ] Sanitizar datos de perfil con `sanitizar_html`
  - [ ] Validar y sanitizar correos electrónicos

### Módulo de Obras (modules/obras)

- [ ] Archivo: `model.py`
  - [ ] Reemplazar consultas directas por constructores seguros
  - [ ] Validar nombres de columnas en ordenamientos
  - [ ] Parametrizar búsquedas y filtros
  - [ ] Implementar `validar_nombre_tabla` para 'obras'

- [ ] Archivo: `controller.py`
  - [ ] Validar datos de obras con `FormValidator`
  - [ ] Sanitizar campos de descripción
  - [ ] Validar códigos y datos numéricos

### Módulo de Inventario (modules/inventario)

- [ ] Archivo: `model.py`
  - [ ] Reemplazar consultas directas por constructores seguros
  - [ ] Parametrizar consultas de búsqueda
  - [ ] Implementar `validar_nombre_tabla` para 'Inventario'
  - [ ] Asegurar que DELETE siempre tenga WHERE

- [ ] Archivo: `controller.py`
  - [ ] Validar datos de inventario con `FormValidator`
  - [ ] Sanitizar campos de descripción
  - [ ] Validar códigos de producto

### Módulo de Herrajes (modules/herrajes)

- [ ] Archivo: `model.py`
  - [ ] Reemplazar consultas directas por constructores seguros
  - [ ] Parametrizar consultas de búsqueda
  - [ ] Implementar validación de columnas para ordenamiento
  - [ ] Sanitizar parámetros de filtros

- [ ] Archivo: `controller.py`
  - [ ] Validar datos de entrada con `FormValidator`
  - [ ] Sanitizar descripciones con `sanitizar_html`
  - [ ] Validar precios y cantidades

### Módulo de Vidrios (modules/vidrios)

- [ ] Archivo: `model.py`
  - [ ] Reemplazar consultas directas por constructores seguros
  - [ ] Validar nombres de tablas y columnas
  - [ ] Parametrizar búsquedas por especificaciones
  - [ ] Sanitizar parámetros de dimensiones

- [ ] Archivo: `controller.py`
  - [ ] Validar datos de vidrios con `FormValidator`
  - [ ] Sanitizar descripciones de producto
  - [ ] Validar medidas y cantidades

### Módulo de Pedidos (modules/pedidos)

- [ ] Archivo: `model.py`
  - [ ] Reemplazar consultas directas por constructores seguros
  - [ ] Parametrizar consultas de búsqueda por fechas
  - [ ] Validar nombres de tablas relacionadas
  - [ ] Asegurar que UPDATE siempre tenga WHERE

- [ ] Archivo: `controller.py`
  - [ ] Validar datos de pedidos con `FormValidator`
  - [ ] Sanitizar notas y comentarios
  - [ ] Validar fechas y datos numéricos

## Configuraciones y Actualizaciones

- [ ] Actualizar `TABLAS_PERMITIDAS` con nuevas tablas cuando se creen
- [ ] Actualizar `COLUMNAS_PERMITIDAS` cuando se modifique el esquema
- [ ] Documentar excepciones a la validación estricta (si aplica)
- [ ] Revisar y actualizar pruebas unitarias tras cambios

## Pruebas de Seguridad

- [ ] Ejecutar `analizar_seguridad_sql_codigo.py` después de cambios importantes
- [ ] Verificar que no haya construcción dinámica de SQL
- [ ] Probar casos límite con datos especiales (comillas, caracteres UTF-8, etc.)
- [ ] Verificar que los errores de seguridad se registren correctamente

## Revisión de Código

- [ ] Confirmar que no hay consultas SQL construidas con concatenación
- [ ] Verificar uso correcto de parámetros en consultas
- [ ] Asegurar que no hay SQL en línea hardcodeado
- [ ] Revisar el manejo de errores de seguridad

## Consideraciones Especiales

- [ ] Consultas complejas (JOIN múltiples)
  - [ ] Documentar por qué no se usan los constructores si aplica
  - [ ] Asegurar que los parámetros se pasan correctamente

- [ ] Reportes y consultas analíticas
  - [ ] Validar nombres de columnas en cláusulas ORDER BY y GROUP BY
  - [ ] Parametrizar filtros en consultas de reporte

- [ ] Procedimientos almacenados
  - [ ] Validar parámetros antes de llamar a SP
  - [ ] Sanitizar resultados si es necesario

---

## Registro de Implementación

| Fecha | Módulo | Archivos Modificados | Responsable | Observaciones |
|-------|--------|----------------------|------------|---------------|
|       |        |                      |            |               |
|       |        |                      |            |               |

## Versión del Checklist: 1.0.0
Fecha de creación: 25 de junio de 2025

# Checklist de problemas de SQL Injection detectados

## Herrajes
- [x] obtener_todos_herrajes: Refactorizado para usar script externo y parámetros seguros.
- [ ] obtener_herrajes_por_obra: Usa f-string para nombre de tabla, migrar a script externo y validar tabla.
- [ ] crear_herraje: Inserta en inventario con concatenación de tabla, migrar a script externo.
- [ ] actualizar_herraje: Actualiza inventario con concatenación de tabla, migrar a script externo.
- [ ] obtener_herraje_por_id: LEFT JOIN con concatenación de tabla, migrar a script externo.
- [ ] actualizar_stock: UPDATE con concatenación de tabla, migrar a script externo.
- [ ] buscar_herrajes: Validar uso de LIKE y parámetros, migrar a script externo si es posible.
- [ ] obtener_estadisticas: Revisar todas las consultas agregadas, migrar a scripts externos.
- [ ] eliminar_herraje: Validar que la eliminación lógica use solo scripts externos y parámetros seguros.
- [ ] Validar que todos los scripts SQL externos usen solo parámetros nombrados y nunca interpolación directa.
- [ ] Revisar todos los métodos que usan f-strings, + o .format para armar consultas.
- [ ] Auditar los scripts en scripts/sql/ para asegurar que no haya riesgos de inyección por variables no controladas.
- [ ] Documentar en el checklist cada método que fue migrado y cada uno pendiente.

## Inventario
- [x] obtener_todos_productos: Refactorizado para usar script externo y parámetros seguros.
- [ ] Otros métodos detectados por el linter (B608):
    - Métodos que construyen queries con strings (líneas 1434, 1459, 1471, 1483, 1529, 1576, 1626, 1644, 1656, 1668, 1718, 1789, 1845, 1853, 1869, 1881, 2000, 2011, 2137, 2144).
    - Usar scripts externos y parámetros seguros en todos ellos.

## Vidrios
- [ ] Refactorizar método obtener_todos_vidrios para usar script externo y parámetros seguros.
- [ ] Revisar todos los métodos que construyen queries dinámicamente o usan concatenación de strings.

## Acciones generales
- [ ] Migrar todas las consultas SQL a scripts externos en scripts/sql/.
- [ ] Usar siempre parámetros en cursor.execute.
- [ ] Validar y sanitizar todos los datos de entrada.
- [ ] Auditar y testear todos los métodos de acceso a datos.

# Checklist de Implementación de Seguridad

Este checklist presenta todas las acciones que deben implementarse para mejorar la seguridad de la aplicación. Marca cada elemento a medida que se completa.

## Protección contra Inyección SQL

- [ ] **Verificar conexiones a base de datos**
  - [ ] Revisar todos los módulos que realizan conexiones directas a la base de datos
  - [ ] Reemplazar cualquier construcción manual de SQL por consultas parametrizadas
  - [ ] Implementar time-out en todas las conexiones

- [ ] **Implementar consultas parametrizadas en todas las operaciones**
  - [ ] Módulo de usuarios
  - [ ] Módulo de obras
  - [ ] Módulo de inventario
  - [ ] Módulo de herrajes
  - [ ] Módulo de vidrios
  - [ ] Módulo de pedidos
  - [ ] Módulo de configuración
  - [ ] Módulo de auditoría

- [ ] **Usar los constructores de SQL seguro**
  - [ ] Reemplazar SELECT directos por `construir_select_seguro`
  - [ ] Reemplazar INSERT directos por `construir_insert_seguro`
  - [ ] Reemplazar UPDATE directos por `construir_update_seguro`
  - [ ] Reemplazar DELETE directos por `construir_delete_seguro`
  - [ ] Verificar que siempre exista cláusula WHERE en DELETE/UPDATE

- [ ] **Validar nombres de tablas y columnas**
  - [ ] Actualizar `TABLAS_PERMITIDAS` con todas las tablas del sistema
  - [ ] Actualizar `COLUMNAS_PERMITIDAS` con todas las columnas por tabla
  - [ ] Implementar validación de nombres en todas las consultas dinámicas

## Validación y Sanitización de Datos de Entrada

- [ ] **Implementar validación en todos los formularios**
  - [ ] Formularios de login y registro
  - [ ] Formularios de edición de perfil
  - [ ] Formularios de creación/edición de obras
  - [ ] Formularios de inventario
  - [ ] Formularios de pedidos
  - [ ] Formularios de configuración

- [ ] **Sanitizar todos los datos de entrada**
  - [ ] Campos de texto libre (usar `sanitizar_html`)
  - [ ] URLs y enlaces (usar `sanitizar_url`)
  - [ ] Datos JSON (usar `sanitizar_json`)
  - [ ] Valores numéricos (usar `sanitizar_numerico`)
  - [ ] Fechas (usar `sanitizar_fecha_sql`)

- [ ] **Prevención de XSS**
  - [ ] Revisar todos los campos donde se muestra contenido ingresado por el usuario
  - [ ] Aplicar `detectar_xss` en datos críticos
  - [ ] Implementar sanitización HTML en todos los campos de texto libre
  - [ ] Asegurar que el contenido HTML generado siempre esté escapado

## Análisis y Monitoreo de Seguridad

- [ ] **Implementar escaneo regular de código**
  - [ ] Configurar análisis automático en pipeline de CI/CD
  - [ ] Programar análisis semanal con `analizar_seguridad_sql_codigo.py`
  - [ ] Bloquear commits con vulnerabilidades críticas

- [ ] **Auditoría y monitoreo**
  - [ ] Implementar registro de intentos de inyección SQL
  - [ ] Implementar registro de intentos de XSS
  - [ ] Configurar alertas para patrones sospechosos
  - [ ] Revisar logs de seguridad semanalmente

- [ ] **Escaneo de vulnerabilidades completo**
  - [ ] Ejecutar `escanear_vulnerabilidades.py` mensualmente
  - [ ] Documentar y priorizar vulnerabilidades encontradas
  - [ ] Verificar la resolución de problemas reportados

## Integración de Módulos y Pruebas

- [ ] **Integrar validadores con módulos existentes**
  - [ ] Integrar `FormValidator` en todos los controladores
  - [ ] Reemplazar validación manual por las utilidades centralizadas
  - [ ] Estandarizar manejo de errores de validación en UI

- [ ] **Pruebas de seguridad**
  - [ ] Crear pruebas de penetración para inyección SQL
  - [ ] Crear pruebas de penetración para XSS
  - [ ] Crear pruebas para validadores de formulario
  - [ ] Verificar sanitización correcta en todos los módulos

- [ ] **Actualizar documentación**
  - [ ] Incorporar guías de seguridad en manuales de desarrollo
  - [ ] Capacitar al equipo sobre las nuevas utilidades
  - [ ] Documentar excepciones y casos especiales

## Configuración y Permisos

- [ ] **Revisar permisos de base de datos**
  - [ ] Auditar permisos de usuario de aplicación en BD
  - [ ] Aplicar principio de mínimo privilegio
  - [ ] Separar usuarios por ambiente (dev, test, prod)

- [ ] **Configuraciones de seguridad**
  - [ ] Revisión de contraseñas y claves en archivos de configuración
  - [ ] Implementar almacenamiento seguro de credenciales
  - [ ] Verificar exclusión de archivos sensibles en `.gitignore`

## Extensión a Otras Áreas

- [ ] **Seguridad en JSON/APIs**
  - [ ] Validar todas las entradas y salidas JSON
  - [ ] Aplicar limitación de tasa (rate limiting) en APIs sensibles
  - [ ] Implementar autenticación robusta en todas las APIs

- [ ] **Protección contra otras vulnerabilidades**
  - [ ] Implementar protección contra CSRF
  - [ ] Revisar gestión de sesiones
  - [ ] Revisar política de contraseñas
  - [ ] Implementar bloqueo de cuentas tras intentos fallidos

## Verificación Final

- [ ] **Test de penetración completo**
  - [ ] Pruebas de inyección SQL en todos los endpoints
  - [ ] Pruebas de XSS en todos los campos de entrada
  - [ ] Pruebas de fuerza bruta en autenticación
  - [ ] Verificar encriptación de datos sensibles

- [ ] **Documentación de seguridad actualizada**
  - [ ] Manual de respuesta a incidentes
  - [ ] Procedimientos de recuperación
  - [ ] Política de actualizaciones de seguridad

## Mantenimiento Continuo

- [ ] **Plan de actualización de seguridad**
  - [ ] Programación de revisiones mensuales
  - [ ] Responsables asignados por área
  - [ ] Procedimiento para implementar parches de seguridad

---

## Registro de Implementación

| Fecha | Elemento Implementado | Responsable | Observaciones |
|-------|------------------------|------------|---------------|
|       |                        |            |               |
|       |                        |            |               |
|       |                        |            |               |

## Versión del Checklist: 1.0.0
Fecha de creación: 25 de junio de 2025

# Marco de Verificación de Módulos

Este documento establece el marco metodológico y los criterios para la verificación exhaustiva de cada módulo del sistema. Sirve como guía general para todos los checklists específicos por módulo.

## Objetivos de la Verificación

1. **Asegurar la calidad de la interfaz de usuario**
   - Verificar carga correcta de elementos visuales
   - Comprobar feedback visual adecuado
   - Validar experiencia de usuario coherente

2. **Garantizar la integridad de datos**
   - Verificar validación completa de entradas
   - Comprobar persistencia correcta en base de datos
   - Validar manejo adecuado de transacciones

3. **Validar la seguridad**
   - Verificar protección contra inyección SQL
   - Comprobar validación y sanitización de entradas
   - Validar gestión de permisos y accesos

4. **Evaluar la cobertura de tests**
   - Verificar cobertura de funcionalidades principales
   - Comprobar inclusión de edge cases
   - Validar tests de integración con otros módulos

## Metodología de Verificación

### 1. Análisis Preliminar

- Revisar la estructura del módulo para identificar:
  - Componentes de UI
  - Operaciones con base de datos
  - Validaciones existentes
  - Tests implementados

### 2. Verificación de UI

- **Carga de datos**
  - Verificar que todos los elementos visuales se cargan correctamente
  - Comprobar que los datos se muestran en los formatos adecuados
  - Validar comportamiento con diferentes tipos de datos (incluyendo extremos)

- **Feedback visual**
  - Verificar indicadores de progreso para operaciones largas
  - Comprobar mensajes de error, advertencia y éxito
  - Validar cambios de estado visual (habilitado/deshabilitado, seleccionado, etc.)

- **Experiencia de usuario**
  - Verificar navegación intuitiva y coherente
  - Comprobar accesibilidad (tamaños, contrastes, etc.)
  - Validar comportamiento responsive

### 3. Verificación de Operaciones de Datos

- **Validación de entradas**
  - Verificar validación de tipos de datos
  - Comprobar validación de formatos específicos (fechas, emails, etc.)
  - Validar manejo de valores nulos, vacíos o extremos

- **Operaciones con base de datos**
  - Verificar uso de utilidades de SQL seguro
  - Comprobar manejo adecuado de transacciones
  - Validar respuesta ante fallos de BD

- **Integridad relacional**
  - Verificar manejo correcto de relaciones entre entidades
  - Comprobar gestión de restricciones de integridad
  - Validar cascadas y propagación de cambios

### 4. Verificación de Seguridad

- **Prevención de inyección**
  - Verificar uso de consultas parametrizadas
  - Comprobar escapado de caracteres peligrosos
  - Validar uso de listas blancas para nombres de tablas y columnas

- **Validación de permisos**
  - Verificar comprobación de permisos antes de operaciones críticas
  - Comprobar registro de accesos y operaciones sensibles
  - Validar separación de roles y privilegios

### 5. Verificación de Tests

- **Cobertura funcional**
  - Verificar que cada funcionalidad crítica tiene tests
  - Comprobar pruebas de todas las ramas de lógica condicional
  - Validar escenarios típicos de uso

- **Edge cases**
  - Verificar tests con datos límite o extremos
  - Comprobar manejo de errores y excepciones
  - Validar comportamiento ante condiciones inusuales

- **Integración**
  - Verificar tests de interacción con otros módulos
  - Comprobar pruebas de flujos completos
  - Validar comportamiento en escenarios reales

## Criterios de Aceptación

Un módulo se considera verificado y aceptado cuando:

1. Todos los elementos de UI se cargan correctamente y ofrecen feedback adecuado
2. Todas las operaciones con datos incluyen validaciones y usan utilidades de SQL seguro
3. Los permisos se verifican correctamente en todas las operaciones sensibles
4. Existe cobertura de tests para al menos el 80% de las funcionalidades
5. Se han documentado y probado los edge cases relevantes
6. Todos los hallazgos críticos han sido corregidos

## Documentación de Hallazgos

Para cada hallazgo, documentar:

1. **Descripción** - Qué se encontró y dónde
2. **Impacto** - Gravedad y posibles consecuencias
3. **Recomendación** - Cómo debería corregirse
4. **Prioridad** - Alta/Media/Baja

## Plantilla de Registro

| ID | Componente | Hallazgo | Impacto | Recomendación | Prioridad | Estado |
|----|------------|----------|---------|---------------|-----------|--------|
| 01 |            |          |         |               |           |        |
| 02 |            |          |         |               |           |        |
| 03 |            |          |         |               |           |        |

---

## Historial de Revisiones

| Fecha | Versión | Descripción | Autor |
|-------|---------|-------------|-------|
| 27/06/2025 | 1.0.0 | Versión inicial | Sistema |
