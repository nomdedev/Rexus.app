## Auditoría: rexus/modules/herrajes/controller.py

Resumen
- Archivo: `rexus/modules/herrajes/controller.py`
- Alcance: CRUD y gestión de inventario de herrajes, exportación y diálogos.

Hallazgos clave
- Buen uso de sanitizadores (`unified_sanitizer`) para inputs antes de persistir.
- Duplicación accidental de import (`sanitize_string` importado dos veces) — pequeño bug estético.
- Uso de señales y métodos claros para crear/actualizar/eliminar.
- Métodos con simulaciones útiles cuando `model` no existe.

Riesgos y severidad
- Calidad: bajo — duplicación de import y prints en vez de logger.
- Robustez: bajo — sanitización presente pero falta validación profunda (ej.: límites de stock).

Recomendaciones
1. Eliminar import duplicado.
2. Reemplazar prints por logging y configurar logger module-level.
3. Añadir validaciones de negocio adicionales (por ejemplo, stock_minimo <= stock_actual).
4. Añadir tests para exportación y diálogos (mock QFileDialog).

Estado: informe creado.

### Estado de migración y mejoras (2025-08-18)
- Migración de prints a logger: COMPLETA
- Consolidación de mensajes hardcodeados: EN PROGRESO
- Migración SQL: COMPLETA
- No se detectaron señales faltantes críticas.

Recomendaciones adicionales:
- Finalizar consolidación de mensajes hardcodeados.
- Documentar contratos de métodos y señales para facilitar testing.
- Añadir tests unitarios para flujos de herrajes y simulaciones.
