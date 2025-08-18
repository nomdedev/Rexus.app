Resumen consolidado — Auditoría de controllers (AUDITORIA_EXPERTA_2025)

Fecha: 2025-08-15
Alcance: Todos los `controller.py` encontrados bajo `rexus/modules/*`.

Objetivo
- Consolidar hallazgos y priorizar acciones para mejorar seguridad, estabilidad y mantenibilidad del código en la capa de controladores.

Estado general
- Todos los controllers han sido auditados (mix de auditorías iniciales y re-auditorías profundas). Informes individuales generados en `AUDITORIA_EXPERTA_2025/modulos/` (IDs 001–027 y variantes).
- Migración de prints a logger y consolidación de mensajes hardcodeados en progreso. Migración SQL casi completa (restan Usuarios, Inventario, Obras).
- Controllers de Vidrios y Herrajes ya corregidos y validados.

Hallazgos comunes (ordenados por prioridad)

1) Manejo de errores demasiado genérico
- Patrón: uso extensivo de `except Exception:` en métodos públicos y privados.
- Riesgo: enmascaramiento de errores, pérdida de stacktraces en producción, respuestas no deterministas.
- Acción recomendada: capturar excepciones concretas (DatabaseError, ValueError, IOError), usar `logger.exception()` cuando corresponda. Añadir tests que provoquen errores para validar comportamiento y mensajes.

2) Logging vs prints
- Patrón: mezcla de `print(...)` y logging central (`rexus.utils.app_logger`) o `logging` directo.
- Riesgo: inconsistencia en monitoreo y dificultad para correlacionar eventos en producción.
- Acción: migrar `print` a un logger central con niveles (DEBUG/INFO/WARN/ERROR). Añadir correlación (request_id/session_id) en logs para trazabilidad.

3) Sanitización y acceso a DB
- Patrón: algunas controllers sanitizan con utilidades (`SecurityUtils`, `unified_sanitizer`), pero hay puntos con `cursor.execute(query)` y queries construidas en controladores o modelos.
- Riesgo: potencial SQL injection y fugas de recursos (cursores sin context managers).
- Acción: garantizar consultas parametrizadas en todos los modelos. Usar context managers para cursores/conn y centralizar acceso DB en capas de modelo/DAO.

4) Mezcla UI/logic en controllers
- Patrón: uso directo de `QFileDialog`/`QMessageBox` y lógica de lectura/escritura (import/export) dentro del controller.
- Riesgo: dificulta testing unitario y separación de responsabilidades.
- Acción: mover IO y parsing a `Model`/servicios; controller solo maneja interacción UI y llamadas a servicios. Introducir interfaces/mocks para vistas.

5) Respuestas inconsistentes y simulaciones
- Patrón: métodos que retornan tipos mixtos (bool, tuple, int, "SIM_001") o usan `hash(codigo)` como ID en señales.
- Riesgo: consumidores del API de controller fallarán por suposiciones de tipo.
- Acción: definir y documentar un contrato claro (ej. siempre retornar dict: {exito: bool, mensaje: str, data: Any}) y normalizar implementaciones. Evitar valores simulados en producción; usar modos de test configurables.

6) Decoradores y permisos duplicados
- Patrón: duplicación de `@auth_required` y `@admin_required` en algunos métodos.
- Riesgo: confusión y potencial doble-ejecución de validación, coste innecesario.
- Acción: revisar y limpiar decoradores; introducir pruebas de permisos (unitarias) para cada endpoint crítico.

7) Tests y cobertura
- Patrón: falta de tests unitarios/integración específicos para flows críticos (inventario paginado, creación de pedidos, import de configuración, integraciones inventario/compras).
- Acción: añadir tests unitarios para controllers con mocks de `model` y `view`. Añadir tests de integración para `InventoryIntegration`, `ProgramacionMantenimientoModel` y `AuthManager`.

8) Señales faltantes en vistas: Ejemplo reciente en Vidrios (`buscar_requested`). Acción: agregar y documentar todas las señales requeridas en las vistas.

Acciones de alta prioridad (plan de trabajo recomendado)

- P0 (seguridad/estabilidad, 1–2 semanas)
  1. Forzar consultas parametrizadas + cerrar cursores con context managers (modelo primero, controllers con fallback). (Inventario, Pedidos, Compras)
  2. Reemplazar `print` por logger central y añadir logger.exception en excepts. Progreso: Vidrios y Herrajes completados, otros módulos en curso.
  3. Añadir validaciones de tipo y normalizar respuestas públicas (contrato API).

- P1 (calidad/mantenibilidad, 2–4 semanas)
  1. Desacoplar IO (import/export) de `ConfiguracionController` hacia `ConfiguracionModel` o servicio.
  2. Documentar API esperada de las vistas (métodos/signals) y crear tests fakes para las vistas.
  3. Limpiar decoradores duplicados y revisar permisos.

- P2 (mejoras y hardening, 4–8 semanas)
  1. Implementar telemetría/metrics para errores frecuentes.
  2. Añadir límites/ratelimits para notificaciones y creación de recursos críticos.
  3. Revisión manual de integraciones `InventoryIntegration` e `Inventory DB`.

Mapeo rápido: archivos y recomendaciones específicas
- `inventario/controller.py` — revisar cursores + parametrización (ver `016_inventario_controller_reauditoria.md`).
- `usuarios/controller.py` — integrar auditoría y revisar duplicados de decoradores (ver `017_usuarios_controller_reauditoria.md`).
- `vidrios/controller.py` — añadir validaciones previas a persistir (ver `018_vidrios_controller_reauditoria.md`).
- `pedidos/controller.py`, `compras/*` — completar TODOs y normalizar respuestas (ver `019`, `024`, `025`).
- `notificaciones/controller.py` — inyección de modelo, añadir ratelimits (ver `020`).
- `logistica/controller.py` — inicializar `usuario_actual` desde `AuthManager`, normalizar tipos de retorno (ver `022`).
- `mantenimiento/controller.py` — prevenir reprogramaciones infinitas; tests de carga (ver `023`).
- `configuracion/controller.py` — mover IO a model/servicio y añadir validación de JSON (ver `026`).
- `herrajes/controller.py` — eliminar import duplicado, emitir IDs reales y limpiar export simulado (ver `027`).

Siguientes pasos sugeridos (elige una o combinalas)
1. Implementar P0 en una rama feature/seguridad-controllers: small PRs por área (DB handling, logging, errores). Puedo crear PRs y archivos de cambio si quieres.
2. Añadir tests unitarios para 6 controllers críticos (inventario, usuarios, compras, pedidos, configuracion, logistica). Puedo generar un scaffold de tests con pytest + mocks.
3. Ejecutar un script de análisis estático para detectar `cursor.execute` y `except Exception` en todo el repo y generar un checklist automático. Lo hago y entrego CSV/report.

Requisitos cubiertos
- Identificación de controllers pendientes: verificado; todos auditados.
- Lectura y análisis por controller: completado en lotes.
- Siguientes tareas prácticas y priorizadas: incluidas arriba.

Estado: listo para la siguiente acción. Indica si:
- quieres que implemente P0 (empezando por seguridad DB y logging),
- que genere los tests scaffold (opción 2), o
- que ejecute el análisis estático global (opción 3).
