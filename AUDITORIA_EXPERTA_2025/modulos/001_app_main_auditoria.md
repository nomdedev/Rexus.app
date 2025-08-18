## Auditoría: rexus/main/app.py

Resumen
- Archivo: `rexus/main/app.py`
- Alcance: Inicialización de la app, Qt/WebEngine, seguridad, carga de módulos y factory pattern.

Hallazgos clave
- Diseño sólido: factory para módulos, fallbacks robustos y manejo de vistas faltantes.
- Buenos fallbacks de UI para módulos no implementados y logging con detalles para debugging.
- Seguridad: existe un `security_manager` y se intentan estableces roles antes de obtener módulos, pero el flujo de errores permite continuar sin seguridad (variable `security_manager = None`) lo que puede dejar la app en un estado inseguro.
- Dependencia global: `main_window` se asigna como variable global en `cargar_main_window_con_seguridad` — riesgo de estado global y pruebas complicadas.
- Mezcla de impresión (print) y UI dialogs (QMessageBox) para errores; migración a logger centralizado en curso. Niveles INFO/WARN/ERROR implementados en módulos corregidos.
- Llamadas a `module_manager.create_module_safely` suponen que `module_manager` está disponible globalmente; no hay validación previa.
- Uso intensivo de strings hard-coded y CSS inline en la UI: migración de estilos a archivos externos en progreso.

Riesgos y severidad
- Riesgo de seguridad: alto — la app puede inicializarse sin security manager y continuar.
- Mantenibilidad: medio — código largo, funciones grandes y mezcla de responsabilidades.
- Robustez: bajo-medio — buenos fallbacks, pero dependencias no verificadas y logs inconsistentes.

Recomendaciones (priorizadas)
1. Imponer fallo seguro: si `security_manager` no se inicializa, bloquear la app o forzar un modo de solo lectura limitado.
2. Reemplazar prints por un logger configurado (logging module) y usar niveles. Progreso: prints migrados en Vidrios y Herrajes.
3. Evitar variables globales (`main_window`), inyectar dependencias explícitamente.
4. Validar `module_manager` y documentar contract de `create_module_safely`.
5. Extraer estilos CSS a recursos o archivos separados. Progreso: migración en curso.
6. Añadir tests unitarios para el factory y fallback behaviors.

Acciones siguientes
- Auditar controllers relacionados (ya en progreso).
- Proponer patch mínimo para manejo seguro de security_manager si el usuario desea.

Estado: informe creado.

### Estado de migración y mejoras (2025-08-18)
- Migración de prints a logger: EN PROGRESO
- Consolidación de mensajes hardcodeados: EN PROGRESO
- Migración SQL: NO APLICA (no queries directas)
- Se recomienda reforzar el manejo seguro de security_manager y migrar completamente a logger centralizado.

Recomendaciones adicionales:
- Finalizar migración a logger centralizado y eliminar prints.
- Extraer estilos CSS a archivos externos.
- Documentar contratos de métodos y dependencias globales.
- Añadir tests unitarios para inicialización y fallbacks.
