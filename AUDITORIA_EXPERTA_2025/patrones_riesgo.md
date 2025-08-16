# Informe: Patrones de riesgo - Rexus.app

Fecha: 2025-08-15

Resumen rápido
- Objetivo: localizar y priorizar patrones de riesgo (exec/eval, `except Exception`, `cursor.execute`, `print`) para acciones P0.
- Resultado: se encontraron múltiples ocurrencias en capas core, módulos y scripts. Se recomienda abordar primero `exec/eval` (RCE), `except Exception` indiscriminados (ocultan fallos críticos) y cualquier SQL construido con interpolación.

Hallazgos (ejemplos y prioridad)

1) Uso de exec / eval (P0 - riesgo crítico)
- `scripts/test_step_by_step.py` ~ línea 43: exec(f"from rexus.modules.{module}.view import *")
- `aplicar_estilos_premium.py` ~ línea 47: exec(f"from rexus.modules.{module_name}.view import *")
- `legacy_root/tools/development/maintenance/generar_informes_modulos.py` usa `exec(script_content, ...)`

Riesgo: ejecución dinámica de código no validado (posible RCE, difícil auditoría, inseguro). Recomendación: reemplazar por importlib.import_module + getattr o por una fábrica de módulos con whitelist y validación.

2) Broad catches: `except Exception` (P0 - estabilidad / diagnóstico)
- Archivos críticos con múltiples ocurrencias: `rexus/core/database.py`, `rexus/core/module_manager.py`, `rexus/core/security.py`, `rexus/core/database_pool.py`, `utils/unified_sanitizer.py`, `utils/sql_query_manager.py`, `rexus/utils/*`.

Riesgo: silenciamiento de errores, pérdida de traces, comportamiento indefinido. Recomendación: capturar excepciones específicas; cuando se capture Exception agrupar con `logger.exception(...)` y decidir re-raise o return controlado.

3) `cursor.execute` (P0/P1 - seguridad/consistencia)
- Uso extendido en modelos y submódulos: `rexus/modules/*/model.py`, `rexus/modules/usuarios/*`, `rexus/utils/sql_query_manager.py`, `rexus/utils/database_manager.py`, `rexus/utils/query_optimizer.py`.
- Observación positiva: la mayoría usa parámetros (`cursor.execute(query, params)`), pero hay lugares con scripts multilínea y usos de `f-strings`/concatenación en scripts ad-hoc del repo `scripts/`.

Riesgo: inyección SQL si hay interpolación; inconsistencias en manejo de transacciones. Recomendación: refactorizar para usar SQL manager central (`sql_manager`), usar parametrización siempre, y aplicar context managers para commit/rollback.

4) `print()` en producción / herramientas (P1)
- Abundante en `tools/*`, `tests/*`, `deploy_production.py`, y varios scripts.

Riesgo: pérdida de control de logs en producción; inconsistencias. Recomendación: migrar a logger central (`rexus.utils.app_logger.get_logger`) con niveles adecuados. Existe `tools/migrate_prints_to_logging.py` que puede usarse.

Plan inmediato recomendado (mi propuesta)
1. Acción inmediata P0: bloquear y eliminar usos de `exec`/`eval` sensibles; sustituir por importlib y whitelist. (Manual, crítico)
2. Revisión y parche de los `except Exception` en módulos core y DB: convertir a excepciones específicas y añadir `logger.exception()` + re-raise donde corresponda. (Manual/automatizable parcialmente)
3. Ejecutar migración de prints->logging en dry-run y aplicar en scripts y tools no críticos. (Automático, seguro con backups)
4. Añadir tests rápidos que detecten `exec`/`eval` y `except Exception` (audit tests) para CI.

Archivos iniciales priorizados para revisión manual (primer lote P0)
- `scripts/test_step_by_step.py`
- `aplicar_estilos_premium.py`
- `legacy_root/tools/development/maintenance/generar_informes_modulos.py`
- `rexus/core/database.py`
- `rexus/core/module_manager.py`
- `rexus/core/database_pool.py`
- `rexus/core/security.py`

Siguientes pasos realizados en este run
- Crearé y ejecutaré un script *dry-run* para la migración prints->logging que mostrará diffs propuestos sin modificar archivos.

Notas finales
- He detectado cientos de ocurrencias; el siguiente entregable será un diff dry-run con la migración de prints a logger para los controladores listados en `tools/migrate_prints_to_logging.py` y un archivo separado con todas las ubicaciones exactas si quieres que lo exporte (esto puede ser grande).

Estado: listo para ejecutar dry-run de prints->logging y luego aplicar los cambios si confirmas.
