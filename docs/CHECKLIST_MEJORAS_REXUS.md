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
- [ ] Documentación avanzada (manual de usuario, troubleshooting, diagramas)
- [ ] Mejoras de estilo (líneas largas, espacios en blanco, f-strings)
- [ ] Atajos de teclado y accesibilidad (shortcuts, tooltips)
- [ ] API REST y webhooks para integraciones externas
- [ ] Monitor de rendimiento y analizador de deuda técnica (scripts para complejidad y optimización)
