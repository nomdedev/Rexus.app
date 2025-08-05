# Checklist de Mejoras y Problemas Detectados en Rexus.app

## 🎉 MEJORAS CRÍTICAS COMPLETADAS RECIENTEMENTE

### ✅ SEGURIDAD SQL Y SANITIZACIÓN DE DATOS (COMPLETADO)
- **Fecha**: Enero 2025
- **Impacto**: CRÍTICO - Protección completa contra SQL Injection y XSS
- **Detalles**:
  - ✅ Creado sistema completo de seguridad SQL en `src/utils/sql_security.py`
  - ✅ Implementado sanitizador de datos robusto en `src/utils/data_sanitizer.py`
  - ✅ 26 tests de seguridad pasando (100% cobertura de utilidades)
  - ✅ Validación de 76+ tablas permitidas del sistema
  - ✅ Protección XSS con filtrado de HTML malicioso
  - ✅ Constructores SQL seguros para todas las operaciones CRUD

### ✅ CORRECCIÓN MASIVA DE IMPORTS (COMPLETADO)
- **Fecha**: Enero 2025  
- **Impacto**: CRÍTICO - Sistema de tests funcional
- **Detalles**:
  - ✅ Corregidos imports en 122+ archivos de test
  - ✅ Migración: `modules.` → `rexus.modules.`
  - ✅ Infraestructura de testing restaurada

### ✅ AUDITORÍA COMPLETA DE SEGURIDAD Y CALIDAD DE CÓDIGO (COMPLETADO)
- **Impacto**: CRÍTICO - Identificación y reparación de vulnerabilidades críticas
- **Detalles**:
  - ✅ **AUDITORÍA COMPLETA**: Análisis de 12 módulos principales con 21 problemas identificados
    - ✅ ConfiguracionModel: Validación completa con `_validate_table_name()`
    - ✅ VidriosModel: 12+ consultas vulnerables reparadas con listas blancas
    - ✅ InventarioModel: Validación de tablas con fallback seguro
    - 🟡 AdministracionModel: Parcialmente reparado (método validación agregado)
    - ❌ **CRÍTICO PENDIENTE**: MantenimientoModel (concatenación directa)
    - ❌ **CRÍTICO PENDIENTE**: LogisticaModel (concatenación directa)
    - ✅ SecurityManager: Sistema seguro con fallback
    - ✅ AuthManager: Migración completa con compatibilidad
    - ✅ PasswordValidator: Reglas de fortaleza implementadas
    - ✅ 25+ tablas en lista blanca, detección patrones peligrosos
    - ✅ SQLTableValidator, SQLQueryBuilder, SQLInputSanitizer
  - 🟡 **MIT LICENSE HEADERS**: 1/12 módulos principales con headers
  - [ ] Pendiente: Tests de integración, concurrencia, subida de archivos, mocks

### USO DE UTILIDADES SQL SEGURAS
  - [ ] Parametrizar todas las consultas de autenticación, búsqueda y filtros.
  - [ ] Sanitizar parámetros de filtros y datos de perfil.
    - ✅ InventarioView: Header completo agregado
    - ❌ 11 módulos restantes sin headers MIT
  - ✅ **EVALUACIÓN DE RIESGO**: Proyecto mejorado de 🔴 CRÍTICO → 🟡 MODERADO-ALTO

---

# CHECKLIST DE MEJORAS Y PROBLEMAS PENDIENTES EN REXUS.APP (REORGANIZADO POR PRIORIDAD)

## ALTA PRIORIDAD
- [ ] Eliminar vulnerabilidades SQL injection y migrar todas las consultas a scripts externos con parámetros (solo módulos pendientes: Mantenimiento, Logística, Administracion).
- [ ] Implementar y validar sanitización XSS en todos los formularios y entradas de usuario (revisar módulos con cobertura <100%).
- [ ] Refactorizar módulos para cumplir estrictamente el patrón MVC (separar lógica de negocio de las vistas).
- [ ] Estandarizar manejo de errores y logging en todos los módulos (try-catch, logs centralizados).
- [ ] Integrar tests de seguridad y funcionalidad en CI/CD (automatizar ejecución y validación).
- [ ] Validar y documentar la configuración de variables de entorno y credenciales (evitar hardcode).
- [ ] Auditar permisos de base de datos y aplicar principio de mínimo privilegio.
- [ ] Completar funcionalidades faltantes en módulos críticos: Compras, Herrajes, Mantenimiento.
- [ ] Optimizar consultas SQL, índices y paginación en módulos con grandes volúmenes de datos.
- [ ] Revisar y limpiar imports y dependencias no utilizadas.

## MEDIA PRIORIDAD
- [ ] Mejorar feedback visual en login, registro y formularios (tooltips, loaders, mensajes claros).
- [ ] Refactorizar funciones grandes (>50 líneas) y mejorar modularidad.
- [ ] Mejorar documentación técnica y de usuario (manuales, guías de API, onboarding).
- [ ] Implementar dashboard de administración avanzado y exportación de reportes.
- [ ] Mejorar cobertura de tests (edge cases, integración, UI, seguridad).
- [ ] Sincronizar e integrar módulos (inventario, obras, compras, etc.) para evitar duplicidad de datos.
- [ ] Validar encoding y manejo de caracteres especiales en toda la app.

## BAJA PRIORIDAD
- [ ] Documentar modelos y relaciones de inventario, herrajes, vidrios y usuarios.
- [ ] Mejorar tooltips y mensajes en controles secundarios.
- [ ] Optimizar rendimiento en módulos menos críticos.
- [ ] Implementar modo oscuro y accesibilidad avanzada.
- [ ] Auditar y mejorar scripts de mantenimiento y verificación.

## SEGURIDAD Y SQL SEGURO
- [ ] Validar y sanitizar todos los datos de entrada (revisar módulos con cobertura <100%).
- [ ] Auditar y testear todos los métodos de acceso a datos.
- [ ] Implementar validación de nombres de tablas y columnas en consultas dinámicas.
- [ ] Documentar y registrar cada método migrado a SQL seguro.
- [ ] Revisar todos los métodos que usan f-strings, + o .format para armar consultas.

## TESTING Y QA
- [ ] Crear y ejecutar pruebas de penetración (SQLi, XSS, fuerza bruta).
- [ ] Validar cobertura de tests automatizados y edge cases.
- [ ] Revisar y mejorar tests de integración y UI.
- [ ] Documentar resultados y hallazgos en cada ciclo de QA.

## DOCUMENTACIÓN Y DESPLIEGUE
- [ ] Actualizar manual técnico y de usuario.
- [ ] Documentar procedimientos de seguridad y recuperación.
- [ ] Validar checklist de despliegue y monitoreo post-producción.
- [ ] Implementar plan de contingencia y backups verificados.

---

# CHECKLIST DE MEJORAS Y PROBLEMAS PENDIENTES EN REXUS.APP (REORGANIZADO POR PRIORIDAD)

## 🚨 VULNERABILIDADES CRÍTICAS PENDIENTES (AUDITORÍA AGOSTO 2025)

### ❌ SQL INJECTION CRÍTICAS - ACCIÓN INMEDIATA REQUERIDA
**Impacto**: CRÍTICO - Riesgo de compromiso total de base de datos

#### MantenimientoModel (`rexus/modules/mantenimiento/model.py`)
- **Problema**: Concatenación SQL directa extremadamente peligrosa
- **Líneas problemáticas**:
  ```python
  # LÍNEA 547 - CRÍTICO
  cursor.execute("SELECT COUNT(*) FROM " + self.tabla_equipos + " WHERE activo = 1")
  
  # LÍNEA 637 - CRÍTICO  
  cursor.execute("SELECT equipo_id FROM " + self.tabla_mantenimientos + " WHERE id = ?", (mantenimiento_id,))
  ```
- **Solución requerida**:
  1. Agregar `from rexus.utils.sql_security import validate_table_name, SQLSecurityError`
  2. Crear método `_validate_table_name()` (copiar de otros módulos reparados)
  3. Reemplazar concatenación por: `f"SELECT COUNT(*) FROM [{self._validate_table_name(self.tabla_equipos)}] WHERE activo = 1"`
  4. Repetir para todas las consultas con concatenación

#### LogisticaModel (`rexus/modules/logistica/model.py`)
- **Problema**: Concatenación SQL directa extremadamente peligrosa
- **Líneas problemáticas**:
  ```python
  # LÍNEA 499 - CRÍTICO
  query = "DELETE FROM " + self.tabla_detalle_entregas + " WHERE id = ?"
  
  # LÍNEA 529 - CRÍTICO
  cursor.execute("SELECT COUNT(*) FROM " + self.tabla_transportes + " WHERE activo = 1")
  
  # LÍNEA 533 - CRÍTICO
  cursor.execute("SELECT COUNT(*) FROM " + self.tabla_transportes + " WHERE activo = 1 AND disponible = 1")
  ```
- **Solución requerida**:
  1. Mismo patrón de reparación que MantenimientoModel
  2. Agregar validación de tablas: `transportes`, `detalle_entregas`, `entregas`
  3. Reemplazar todas las concatenaciones con validación segura

#### AdministracionModel (`rexus/modules/administracion/model.py`)
- **Problema**: Concatenación de cláusulas WHERE dinámicas
- **Líneas problemáticas**:
  ```python
  # Múltiples líneas con: query += " WHERE " + " AND ".join(conditions)
  ```
- **Estado**: Parcialmente reparado (método `_validate_table_name()` agregado)
- **Pendiente**: Aplicar validación a todas las consultas dinámicas

### ❌ MIT LICENSE HEADERS FALTANTES - CUMPLIMIENTO LEGAL
**Impacto**: ALTO - Problemas de cumplimiento de licencia open source

#### Archivos principales sin headers MIT:
- `rexus/modules/obras/view.py`
- `rexus/modules/usuarios/view.py`  
- `rexus/modules/administracion/view.py`
- `rexus/modules/herrajes/view.py`
- `rexus/modules/logistica/view.py`
- `rexus/modules/pedidos/view.py`
- `rexus/modules/compras/view.py`
- `rexus/modules/mantenimiento/view.py`
- `rexus/modules/auditoria/view.py`
- `rexus/modules/configuracion/view.py`
- `rexus/modules/vidrios/view.py`

**Solución**: Agregar header MIT completo al inicio de cada archivo:
```python
"""
MIT License

Copyright (c) 2024 Rexus.app

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

[Descripción original del módulo]
"""
```

---

## PRIORIDAD ALTA
### USUARIOS
- [ ] Validar unicidad de nombre de usuario/email en registro
  - [ ] Pendiente: Aplicar en formularios de usuarios
  - [ ] Pendiente: Aplicar en módulo usuarios
- [ ] Limitar intentos de login fallidos
- [ ] Validar tokens y entradas en restablecimiento de contraseña
  - [ ] Pendiente: Tests específicos del módulo usuarios
### INVENTARIO
  - [ ] Migrar todas las consultas SQL a scripts externos en scripts/sql/
  - [ ] Usar siempre parámetros en cursor.execute
  - [ ] Auditar y testear todos los métodos de acceso a datos
  - [ ] Validar que todos los scripts SQL externos usen solo parámetros nombrados y nunca interpolación directa
  - [ ] Migrar métodos que construyen queries con strings a scripts externos y parametrizar
  - [ ] Validar y sanitizar todos los datos de entrada en formularios de inventario (códigos, cantidades, precios, fechas)
  - [ ] Implementar validación de stock negativo y límites máximos por producto
  - [ ] Revisar y mejorar feedback visual en la UI para operaciones de stock (alta, baja, edición, errores)
  - [ ] Auditar manejo de errores y logs en operaciones de inventario
  - [ ] Validar integridad relacional entre inventario y otros módulos (obras, compras, herrajes)
  - [ ] Cobertura de tests automatizados: unitarios, edge cases, integración, UI
  - [ ] Documentar el modelo de inventario y sus relaciones
### HERRAJES
  - [ ] Migrar todos los métodos principales a scripts externos en scripts/sql/ y validar parámetros
  - [ ] Usar siempre parámetros en cursor.execute y evitar interpolación directa
  - [ ] Implementar validación de stock negativo y límites máximos por tipo de herraje
  - [ ] Validar integridad relacional entre herrajes y otros módulos (inventario, obras, compras)
- **Problema**: Diferentes módulos usan diferentes patrones para manejo de excepciones
- **Solución**: Estandarizar uso de try-catch y logging de errores
- **Impacto**: MEDIO - Debugging y estabilidad

#### Imports y Dependencias
- **Problema**: Algunos módulos tienen imports no utilizados
- **Estado**: Parcialmente resuelto con corrección masiva de imports reciente
- **Pendiente**: Limpieza de imports no utilizados
- **Impacto**: BAJO - Rendimiento y claridad de código

#### Documentación de Código
- **Problema**: Falta de documentación consistente en métodos y clases
- **Solución**: Agregar docstrings siguiendo estándar PEP 257
- **Impacto**: MEDIO - Mantenibilidad y onboarding de desarrolladores

---

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
  - [ ] Migrar todos los métodos principales a scripts externos en scripts/sql/ y validar parámetros
  - [ ] Usar siempre parámetros en cursor.execute y evitar interpolación directa
  - [ ] Auditar y testear todos los métodos de acceso a datos
  - [ ] Validar y sanitizar todos los datos de entrada en formularios de logística (ubicaciones, transportes, entregas, fechas)
  - [ ] Implementar validación de ubicaciones duplicadas y límites máximos por transporte
  - [ ] Revisar y mejorar feedback visual en la UI para operaciones de logística (alta, baja, edición, errores)
  - [ ] Auditar manejo de errores y logs en operaciones de logística
  - [ ] Validar integridad relacional entre logística y otros módulos (inventario, obras, compras)
  - [ ] Mejorar tooltips y mensajes en controles y botones de acción
  - [ ] Optimización de rendimiento y refactorización de funciones grandes
  - [ ] Cobertura de tests automatizados: unitarios, edge cases, integración, UI
  - [ ] Documentar el modelo de logística y sus relaciones

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
  - [ ] Auditar y monitorear accesos y actividad.
  - [ ] Configurar análisis automático de seguridad en pipeline CI/CD.

### VALIDACIÓN Y SANITIZACIÓN DE DATOS
  - [ ] Aplicar validación en todos los formularios (login, registro, edición, inventario, pedidos, configuración).
  - [ ] Revisar todos los campos donde se muestra contenido ingresado por el usuario.
  - [ ] Validar relaciones (cliente, productos, pedidos).

### EDGE CASES Y TESTS
  - [ ] Edge cases: datos límite, condiciones de error, concurrencia, datos corruptos, memoria/disco limitado, red lenta, usuario sin permisos, sesión expirada, múltiples logins, drag & drop, cookies/JS deshabilitado.
  - [ ] Pendiente: Tests de integración, concurrencia, subida de archivos, mocks

### USO DE UTILIDADES SQL SEGURAS
  - [ ] Parametrizar todas las consultas de autenticación, búsqueda y filtros.
  - [ ] Sanitizar parámetros de filtros y datos de perfil.
  - [ ] Validar datos de inventario y obras con `FormValidator`.

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
