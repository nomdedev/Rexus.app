## Auditoría: rexus/main/app.py

Resumen
- Archivo: `rexus/main/app.py`
- Alcance: Inicialización de la app, Qt/WebEngine, seguridad, carga de módulos y factory pattern.

Hallazgos clave
- Diseño sólido: factory para módulos, fallbacks robustos y manejo de vistas faltantes.
- Buenos fallbacks de UI para módulos no implementados y logging con detalles para debugging.
- Seguridad: existe un `security_manager` y se intentan estableces roles antes de obtener módulos, pero el flujo de errores permite continuar sin seguridad (variable `security_manager = None`) lo que puede dejar la app en un estado inseguro.
- Dependencia global: `main_window` se asigna como variable global en `cargar_main_window_con_seguridad` — riesgo de estado global y pruebas complicadas.
- Mezcla de impresión (print) y UI dialogs (QMessageBox) para errores; falta un logger centralizado y niveles claros (INFO/WARN/ERROR).
- Llamadas a `module_manager.create_module_safely` suponen que `module_manager` está disponible globalmente; no hay validación previa.
- Uso intensivo de strings hard-coded y CSS inline en la UI: dificulta mantenimiento y pruebas.

Riesgos y severidad
- Riesgo de seguridad: alto — la app puede inicializarse sin security manager y continuar.
- Mantenibilidad: medio — código largo, funciones grandes y mezcla de responsabilidades.
- Robustez: bajo-medio — buenos fallbacks, pero dependencias no verificadas y logs inconsistentes.

Recomendaciones (priorizadas)
1. Imponer fallo seguro: si `security_manager` no se inicializa, bloquear la app o forzar un modo de solo lectura limitado.
2. Reemplazar prints por un logger configurado (logging module) y usar niveles.
3. Evitar variables globales (`main_window`), inyectar dependencias explícitamente.
4. Validar `module_manager` y documentar contract de `create_module_safely`.
5. Extraer estilos CSS a recursos o archivos separados.
6. Añadir tests unitarios para el factory y fallback behaviors.

Acciones siguientes
- Auditar controllers relacionados (ya en progreso).
- Proponer patch mínimo para manejo seguro de security_manager si el usuario desea.

Estado: informe creado.
