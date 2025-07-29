# Checklist de Mejoras y Problemas Detectados en Rexus.app

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
## 7. Errores de importación o inicialización silenciosos
- [ ] Errores en imports o constructores de vistas/modelos/controladores no se ven en la UI.
  - [ ] Revisar los logs y mostrar mensajes de error en pantalla.
    - *Justificación:* Si hay un error en el import, el usuario solo ve el fallback y no sabe por qué.
    - *Solución:* Capturar excepciones y mostrar el mensaje real en la UI.

## 8. Falta de datos de prueba o base de datos vacía
- [ ] Las tablas pueden estar vacías porque la base de datos no tiene datos de prueba.
- [ ] Agregar datos de ejemplo o scripts de carga rápida.
    - *Justificación:* Sin datos de prueba, es difícil validar la UI y la lógica.
    - *Solución:* Crear scripts de carga de datos y/o un modo demo.
## 9. Código duplicado y falta de reutilización
- [ ] Hay lógica repetida en la inicialización de vistas, carga de datos y manejo de errores.
- [ ] Extraer funciones utilitarias para carga de datos, manejo de errores y normalización de nombres.
    - *Justificación:* Facilita el mantenimiento y reduce bugs por cambios en un solo lugar.
    - *Solución:* Crear utilidades en `utils/` y usarlas en todos los módulos.

## 10. Falta de validación de formularios
- [x] ✅ **PARCIALMENTE RESUELTO** Los formularios permiten guardar datos incompletos o inválidos.
  - [x] ✅ **RESUELTO - Inventario y Obras** Agregar validaciones antes de guardar (campos obligatorios, formatos, etc.).
    - **Solución aplicada:** Sistema completo de validación implementado con `FormValidatorManager`
    - **Validaciones implementadas:** campos obligatorios, email, códigos de producto, fechas, números, rangos
    - **Feedback visual:** Colores y mensajes de error en tiempo real
    - **Impacto:** Formularios de Inventario y Obras ahora previenen datos inválidos

## 11. Falta de documentación y comentarios
## 12. Checklist detallado de mejoras y tests faltantes por módulo

### Inventario

### Obras

### Logística

### Herrajes

### Vidrios

### Mantenimiento

### Configuración

### Usuarios

### General

## 13. Problema crítico: sistema de seguridad no se inicializa correctamente
- [ ] El sistema de seguridad global (`SecurityManager`) no se inicializa correctamente al iniciar la app, por lo que el login y los permisos no funcionan aunque la base de datos conecte bien.
    - *Síntoma:* Login exitoso pero error "sistema de seguridad no disponible" y no se puede continuar.
    - *Causa:* Se llama a `get_security_manager()` en vez de `initialize_security_manager()` en el arranque, por lo que la instancia global queda en `None`.
    - *Solución:* Reemplazar la llamada por `initialize_security_manager()` para inicializar correctamente el sistema de seguridad y permitir login y permisos.

## 🔥 Mejoras y correcciones tras últimos cambios manuales (2025-07-28)

### Inventario (view.py)
- [ ] Verificar que la vista de Inventario inicialice correctamente la carga de datos y la conexión con el controlador tras los últimos cambios.
- [ ] Validar que los formularios y validadores de producto funcionen correctamente con los nuevos imports y estructura.

### Administración (view.py)
- [ ] Revisar la integración de señales y la conexión con el controlador para la gestión de empleados, departamentos y reportes.
- [ ] Asegurar que los diálogos y formularios de administración validen correctamente los datos antes de enviarlos al backend.

### Herrajes (model.py)
- [ ] Corregir la sintaxis de la creación de tablas: la instrucción `CREATE TABLE IF NOT EXISTS ... IDENTITY` no es válida en SQL Server, y puede causar errores de ejecución.
- [ ] Validar que todos los bloques `try` tengan su correspondiente `except` o `finally` para evitar errores de sintaxis Python.
- [ ] Revisar el uso de cursores y commits para asegurar que la conexión a la base de datos no sea `None` y que los índices se creen correctamente.

### Obras (view.py)
- [ ] Verificar que la vista de Obras conecte correctamente las señales de agregado/edición de obra y que los formularios funcionen tras los cambios recientes.
- [ ] Validar la carga inicial de datos y la integración con el cronograma de obras.

### General (app.py y módulos)
- [ ] Revisar la inicialización de variables de entorno y la carga de módulos tras los cambios en la arquitectura principal.
- [ ] Asegurar que todos los módulos gestionen correctamente los errores de conexión y muestren feedback visual adecuado.
---
---



## Checklist Único de Mejoras y Problemas Pendientes en Rexus.app

### ALTA PRIORIDAD
    - *Síntoma:* Login exitoso pero error "sistema de seguridad no disponible" y no se puede continuar.
    - *Causa:* Se llama a `get_security_manager()` en vez de `initialize_security_manager()` en el arranque, por lo que la instancia global queda en `None`.
    - *Solución:* Reemplazar la llamada por `initialize_security_manager()` para inicializar correctamente el sistema de seguridad y permitir login y permisos.
 - [ ] Cobertura de tests automatizados (unitarios, integración, edge cases, UI)
 - [ ] Sanitización de datos sensibles (contraseñas, logs, auditoría)
 - [ ] Auditoría y logs de actividad (registro, limpieza automática, detección de patrones sospechosos)
 - [ ] Gestión de errores y excepciones (evitar try/except/pass, logging específico)
 - [ ] Controladores incompletos o no robustos (herrajes, vidrios, filtros avanzados)
 - [ ] Funcionalidades faltantes en módulos: Compras (proveedores, órdenes, seguimiento), Herrajes (cálculos, validaciones), Mantenimiento (programación, historial)

### MEDIA PRIORIDAD
 - [ ] Optimización de rendimiento (consultas SQL, índices, paginación, lazy loading)
 - [ ] Integración y sincronización entre módulos (inventario, obras, compras, etc.)
 - [ ] Refactorización de funciones grandes (>50 líneas, muchas variables locales)
 - [ ] Limpieza de imports (eliminar no usados, agrupar por tipo)
 - [ ] Revisión y optimización de dependencias (`requirements.txt`, versiones, vulnerabilidades)
 - [ ] Mejoras de feedback visual (indicadores de carga, accesibilidad, modo oscuro)

### BAJA PRIORIDAD
 - [ ] Documentación avanzada (manual de usuario, troubleshooting, diagramas)
 - [ ] Mejoras de estilo (líneas largas, espacios en blanco, f-strings)
 - [ ] Atajos de teclado y accesibilidad (shortcuts, tooltips)
 - [ ] API REST y webhooks para integraciones externas
 - [ ] Monitor de rendimiento y analizador de deuda técnica (scripts para complejidad y optimización)
   - ✅ Verificados modelos restantes: Pedidos, Compras, Usuarios, Logística, Mantenimiento
   - ✅ Todos los modelos ya usan queries parametrizadas correctamente
   - **Impacto:** Sistema completamente protegido contra inyecciones SQL

### ✅ **COMPLETADO HOY (2025-01-28) - Sesión de finalización y mejoras UX**

9. **Conexión completa de botón Nuevo Producto en Inventario - COMPLETADO**
   - ✅ **Creado diálogo completo:** `DialogoNuevoProducto` con todos los campos necesarios
   - ✅ **Sistema de validación integrado:** Uso de `FormValidatorManager` con validaciones específicas
   - ✅ **Validaciones implementadas:** código de producto, campos obligatorios, formatos numéricos
   - ✅ **Conexión con controlador:** Método `agregar_producto()` con manejo de errores
   - ✅ **Feedback visual:** Mensajes de éxito/error y recarga automática de datos
   - **Archivos modificados:** `src/modules/inventario/view.py`, `src/modules/inventario/controller.py`
   - **Impacto:** Formulario de productos completamente funcional con validación robusta

10. **Conexión completa de botón Nueva Obra en Obras - COMPLETADO**
    - ✅ **Aprovechado diálogo existente:** `FormularioObraDialog` mejorado con validaciones
    - ✅ **Sistema de validación completo:** Validaciones para todos los campos críticos
    - ✅ **Validaciones personalizadas:** Fechas, presupuesto, email, campos obligatorios
    - ✅ **Validación de lógica de negocio:** Fecha fin posterior a fecha inicio
    - ✅ **Conexión controlador-vista:** Método `mostrar_dialogo_nueva_obra()` funcionando
    - ✅ **Alias de método:** `agregar_obra()` que llama a `crear_obra()` existente
    - **Archivos modificados:** `src/modules/obras/view.py`, `src/modules/obras/controller.py`
    - **Impacto:** Creación de obras con validación completa y feedback inmediato

11. **Mejoras críticas de UI y experiencia de usuario - COMPLETADO**
    - ✅ **Contraste sidebar mejorado:** Ajustados colores para mejor visibilidad del texto
    - ✅ **Tamaño de cards optimizado:** Reducidos recuadros de administración para mejor uso del espacio
    - ✅ **Eliminación de errores CSS:** Removidas propiedades `transition` incompatibles con PyQt
    - ✅ **Hover mejorado:** Incrementadas diferencias de opacidad para mejor feedback visual
    - **Archivos modificados:** `src/main/app.py`, `src/modules/administracion/view.py`
    - **Impacto:** Interfaz más legible, sin errores CSS, mejor experiencia visual

12. **Corrección crítica de errores de sintaxis - COMPLETADO**
    - ✅ **Error en herrajes corregido:** Arreglada query SQL malformada que impedía carga del módulo
    - ✅ **Validación de BD más leniente:** Cambio de crash por warning cuando faltan variables de entorno
    - ✅ **Modo fallback mejorado:** Módulos ahora pueden funcionar con datos demo si falla BD
    - **Archivos modificados:** `src/modules/herrajes/model.py`, `src/core/database.py`
    - **Impacto:** Módulos que mostraban solo "disponible y funcionando" ahora cargan correctamente

### ⏳ **PENDIENTE - ALTA PRIORIDAD**
13. **Completar conexión de formularios restantes**
    - [ ] Aplicar sistema de validación a formularios de Usuarios y Compras
    - [ ] Conectar botones "Agregar" faltantes en otros módulos restantes
    - [ ] Verificar señales de actualización de tablas tras guardar en todos los módulos

### ⏳ **PENDIENTE - MEDIA PRIORIDAD**  
5. **Mejorar feedback visual y manejo de errores**
   - [ ] Agregar `QMessageBox` para errores críticos
   - [ ] Implementar banners de error en UI
   - [ ] Mejorar logging detallado en archivos

6. **Completar correcciones SQL injection**
   - [ ] Revisar y corregir modelos restantes: Pedidos, Compras, Usuarios, Logística, Mantenimiento
   - [ ] Verificar nombres de tablas correctos en BD
   - [ ] Estandarizar uso de queries parametrizadas

7. **Crear datos de prueba**
   - [ ] Scripts de carga de datos demo para módulos vacíos
   - [ ] Modo demo cuando no hay conexión BD
   - [ ] Datos de ejemplo realistas

### ⏳ **PENDIENTE - BAJA PRIORIDAD**
8. **Refactoring y optimización**
   - [ ] Extraer utilidades comunes a `src/utils/`
   - [ ] Reducir código duplicado en inicialización
   - [ ] Mejorar arquitectura MVC

9. **Validación de formularios**
   - [ ] Campos obligatorios
   - [ ] Validación de formatos (email, teléfono, etc.)
   - [ ] Feedback visual de validación

10. **Documentación**
    - [ ] Docstrings en todas las clases principales
    - [ ] Comentarios explicativos en código complejo
    - [ ] Documentación de arquitectura

---




### Logística (PRIORIDAD MEDIA)
- [ ] Revisar que el método `create_mapa_tab` inicialice correctamente el widget de mapa y que las dependencias de QtWebEngine estén presentes.
- [ ] Validar que el panel de información se muestre como tooltip y que los controles del mapa funcionen correctamente.
- [ ] Agregar manejo de excepciones en la inicialización y actualización del mapa interactivo.

### Vidrios (PRIORIDAD MEDIA)
- [ ] Revisar que la tabla de vidrios (`tabla_vidrios`) se conecte correctamente al controlador y que los métodos de actualización manejen errores.
- [ ] Validar que la carga de datos en la tabla no arroje excepciones y que el feedback visual sea claro.
- [ ] Agregar manejo de excepciones en los métodos de actualización de la tabla.

### Configuración (PRIORIDAD BAJA)
- [ ] Revisar la lectura y escritura de parámetros de configuración en los widgets (`widgets_configuracion`).
- [ ] Validar que la carga de configuraciones y parámetros no arroje excepciones.
- [ ] Agregar manejo de errores robusto en la lectura de archivos de configuración y en la actualización de parámetros.

---
> **Estos errores fueron detectados en la última ejecución y deben ser priorizados según el impacto en la funcionalidad principal.**
---
