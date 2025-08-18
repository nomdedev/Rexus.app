## Auditoría: rexus/modules/administracion/controller.py

Resumen
- Archivo: `rexus/modules/administracion/controller.py`
- Alcance: Controlador principal de administración, integra contabilidad y RRHH y coordina el dashboard.

Hallazgos clave
- Controlador grande con muchas responsabilidades (orquestación, timers, múltiples actualizaciones periódicas).
- Uso de `get_security_manager()` y dependencia fuerte en manager global.
- Inicialización de submódulos con imports relativos; hay riesgo de acoplamiento y carga tardía.
- Falta de pruebas visibles para actualizar múltiples secciones coordinadas.

Riesgos y severidad
- Mantenibilidad: medio-alto — clase demasiado grande, difícil de testear y de mantener.
- Performance: medio — actualizaciones frecuentes (30s) podrían tener impacto; necesita debounce y checks de estado.

Recomendaciones
1. Refactorizar en subcomponentes más pequeños (DashboardUpdater, DataRefresher, SubmoduleOrchestrator).
2. Inyectar `security_manager` o pasarlo en constructor para permitir tests.
3. Añadir toggles/flags para desactivar timers en entornos de test/CI.
4. Añadir cobertura de tests unitarios para orquestación y manejo de errores en submódulos.

Estado: informe creado.

### Estado de migración y mejoras (2025-08-18)
- Migración de prints a logger: EN PROGRESO
- Consolidación de mensajes hardcodeados: EN PROGRESO
- Migración SQL: EN PROGRESO
- No se detectaron señales faltantes críticas.

Recomendaciones adicionales:
- Completar migración SQL y eliminar queries hardcodeadas.
- Unificar uso de logger centralizado y message_system.
- Documentar contratos de métodos y señales para facilitar testing.
- Añadir tests unitarios para flujos de administración y validación de errores.
