026 - Re-auditoría profunda: `configuracion/controller.py`

Resumen rápido
- Archivo auditado: `rexus/modules/configuracion/controller.py`.
- Objetivo: revisar seguridad de export/import, pruebas de conexión y aplicación de cambios.

Hallazgos clave
- Métodos sensibles: `importar_configuracion` y `exportar_configuracion` que leen/escriben archivos; riesgo si no valida contenidos.
- `probar_conexion_bd` actualmente solo reporta los valores de configuración; falta la lógica real de conexión y manejo de credenciales.
- Uso de `admin_required` para acciones críticas (bien).
- Uso de `QFileDialog` y `QMessageBox` directamente en controller — combinación UI/logic que dificulta testing.

Recomendaciones
1. Mover la lógica de lectura/escritura a `ConfiguracionModel` y dejar en el controller solo la interacción UI (selección de archivos, confirmaciones).
2. Validar y sanitizar el contenido importado antes de aplicarlo; usar esquemas JSON y reglas de validación.
3. Implementar la prueba real de conexión en `probar_conexion_bd` con timeouts y manejo seguro de credenciales (no imprimir contraseñas).
4. Añadir pruebas unitarias para `importar_configuracion` con archivos maliciosos y casos límite.
5. Audit logging: registrar quién importó/exportó configuraciones y cuándo.

Estado: listo.

### Estado de migración y mejoras (2025-08-19)
- Migración de prints a logger: EN PROGRESO
- Consolidación de mensajes hardcodeados: EN PROGRESO
- Migración SQL: COMPLETA
- No se detectaron señales faltantes críticas.

Recomendaciones adicionales:
- Unificar uso de logger centralizado y message_system.
- Documentar contratos de métodos y señales para facilitar testing.
- Añadir tests unitarios para flujos de configuración y validación de IO.
