# Checklist Detallado de Mejoras y Problemas en Rexus.app

## 1. Visualización de datos en tablas
  - [ ] El método del controlador que debería cargar los datos no se llama al inicializar la vista.
    - *Solución:* Llamar explícitamente a los métodos de carga de datos (`cargar_datos_iniciales`, `cargar_X`) en el constructor o método `set_controller` de cada vista.
  - [ ] El método del modelo retorna una lista vacía (por error de consulta, tabla vacía o error de conexión).
    - *Solución:* Agregar logs y manejo de errores en los métodos del modelo. Proveer datos de prueba si la base está vacía.
  - [ ] El método de la vista que debe poblar la tabla no está implementado o no se llama.
    - *Solución:* Implementar siempre un método `cargar_en_tabla` y llamarlo desde el controlador tras obtener los datos.
  - [ ] Faltan llamadas a `set_controller` o a métodos como `cargar_datos_iniciales` en la inicialización.
    - *Solución:* Asegurarse de que cada vista reciba y almacene su controlador y que este llame a la carga inicial.
  - [ ] Errores silenciosos en los métodos de carga (try/except que oculta el error real).
    - *Solución:* Loggear todas las excepciones y mostrar mensajes de error en la UI.

## 2. Factory de módulos y fallback
  - [ ] El nombre del módulo en el botón no coincide exactamente con el esperado en el factory.
    - *Solución:* Unificar nombres y claves en el diccionario del factory y en los botones del sidebar. Usar una función de normalización.
  - [ ] El import de la vista/modelo/controlador falla (archivo faltante, error de sintaxis, etc.).
    - *Solución:* Revisar los imports y agregar tests de importación. Mostrar el error real en la UI.
  - [ ] El método de creación del módulo no está implementado en el factory.
    - *Solución:* Implementar todos los métodos de creación de módulos en el factory.

## 3. Errores de inicialización de tablas
  - [ ] Siempre verificar que `header` no sea `None` antes de llamar a métodos sobre él.
    - *Justificación:* Si la tabla no tiene columnas, `horizontalHeader()` devuelve `None` y causa un crash.
    - *Solución:* Usar `if header is not None:` antes de modificar el header.

## 4. Falta de conexión entre formularios y base de datos
  - [ ] El botón “Guardar” no está conectado al controlador.
    - *Solución:* Conectar el botón a un método que valide y envíe los datos al controlador.
  - [ ] El controlador no llama al método correcto del modelo.
    - *Solución:* Revisar que el controlador invoque el método de inserción/actualización correcto.
  - [ ] El modelo no implementa el método de inserción o consulta.
    - *Solución:* Implementar los métodos faltantes en el modelo y testearlos con datos reales.
  - [ ] Faltan señales o métodos de actualización de la tabla tras guardar.
    - *Solución:* Llamar a la recarga de la tabla después de guardar/editar.

## 5. Nombres y tildes en los módulos
  - [ ] Unificar nombres y claves en el diccionario del factory y en los botones.
    - *Justificación:* Si el nombre no coincide exactamente, se muestra el fallback.
    - *Solución:* Usar una función de normalización de nombres (sin tildes, minúsculas) tanto en el sidebar como en el factory.

## 6. Falta de feedback visual o mensajes de error
  - [ ] Agregar mensajes de error visibles en la UI y logs detallados.
    - *Justificación:* El usuario no sabe si la app está funcionando mal o si solo no hay datos.
    - *Solución:* Usar `QMessageBox` o banners de error en la UI y logs en consola/archivo.

## 7. Errores de importación o inicialización silenciosos
  - [ ] Revisar los logs y mostrar mensajes de error en pantalla.
    - *Justificación:* Si hay un error en el import, el usuario solo ve el fallback y no sabe por qué.
    - *Solución:* Capturar excepciones y mostrar el mensaje real en la UI.

## 8. Falta de datos de prueba o base de datos vacía
  - [ ] Agregar datos de ejemplo o scripts de carga rápida.
    - *Justificación:* Sin datos de prueba, es difícil validar la UI y la lógica.
    - *Solución:* Crear scripts de carga de datos y/o un modo demo.

## 9. Código duplicado y falta de reutilización
  - [ ] Extraer funciones utilitarias para carga de datos, manejo de errores y normalización de nombres.
    - *Justificación:* Facilita el mantenimiento y reduce bugs por cambios en un solo lugar.
    - *Solución:* Crear utilidades en `utils/` y usarlas en todos los módulos.

## 10. Falta de validación de formularios
  - [ ] Agregar validaciones antes de guardar (campos obligatorios, formatos, etc.).
    - *Justificación:* Evita datos corruptos o errores en la base.
    - *Solución:* Validar en el frontend y backend antes de insertar/actualizar.

## 11. Falta de documentación y comentarios
  - [ ] Documentar cada clase y método clave.
    - *Justificación:* Facilita el onboarding y el mantenimiento.
    - *Solución:* Agregar docstrings y comentarios explicativos.


> Actualiza este checklist a medida que avances en cada punto. Si necesitas ayuda para resolver un ítem, indícalo aquí. Si encuentras un problema nuevo, agrégalo con su justificación y propuesta de solución.
