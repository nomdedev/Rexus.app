018 - Re-auditoría profunda: `vidrios/controller.py`

Resumen rápido
- Archivo auditado: `rexus/modules/vidrios/controller.py`.
- Objetivo: revisar flujos de creación/edición, señales emitidas y manejo de errores.

Hallazgos
- Buen uso de señales para comunicar eventos (`vidrio_agregado`, `vidrio_actualizado`, etc.).
- Métodos simples y claros; la mayor parte de la lógica delegada al modelo.
- Manejo de errores con `try/except` que llama a `mostrar_error` en la vista.
- Faltan validaciones explícitas en `agregar_vidrio` y `editar_vidrio` antes de llamar al modelo.

Recomendaciones
1. Añadir validaciones previas (schema/required fields) antes de persistir.
2. Asegurar que los IDs retornados por el modelo son validados (entero >0).
3. Añadir logging en lugar de prints y `mostrar_error`.
4. Añadir pruebas unitarias para cada método que mockee el modelo y la vista.

### Estado de migración y mejoras (2025-08-18)
- Migración de prints a logger: COMPLETA
- Consolidación de mensajes hardcodeados: EN PROGRESO
- Migración SQL: COMPLETA
- Se detectó y corrigió señal faltante `buscar_requested` en la vista.

Recomendaciones adicionales:
- Finalizar consolidación de mensajes hardcodeados.
- Documentar contratos de métodos y señales para facilitar testing.
- Añadir tests unitarios para señales y flujos de error.

Estado: listo.
