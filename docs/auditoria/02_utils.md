# AUDITORÍA MÓDULO UTILS

**Fecha:** 8 de agosto de 2025
**Estándares:** MITRE CWE, OWASP Top 10, MIT Secure Coding, NIST

---

## Resumen Ejecutivo
- Auditoría profunda de utilitarios: sanitización de datos, estilos, backups, cache, manejo de archivos y logs.
- Se identifican buenas prácticas, pero también riesgos potenciales y áreas de mejora en seguridad, logging y pruebas.

---

## data_sanitizer.py
**Resumen:** Clase para sanitización de datos: cadenas, SQL, numéricos y diccionarios. Aplica patrones para prevenir XSS y SQLi, y utiliza logging para advertencias.

**Hallazgos:**
- Buen uso de patrones para XSS y SQLi, aunque no exhaustivos.
- Logging de advertencias ante posibles inyecciones detectadas.
- Sanitización recursiva en diccionarios.
- No hay soporte para internacionalización.
- No hay control de acceso ni validación de origen de datos.
- No hay pruebas unitarias incluidas.

**Riesgos:**
- Patrones de XSS/SQLi pueden ser evadidos por payloads avanzados.
- Logging puede exponer datos sensibles si no se controla adecuadamente.
- No hay manejo de encoding explícito para todos los casos.

**Recomendaciones:**
- Revisar y actualizar patrones de XSS/SQLi periódicamente.
- Añadir pruebas unitarias.
- Limitar información sensible en logs.
- Documentar limitaciones y casos no cubiertos.

**Cumplimiento:**
- MITRE CWE: Parcial (CWE-79, CWE-89, CWE-117)
- OWASP: Parcial (A1:2017-Inyección, A6:2017-Logging)
- MIT Secure Coding: Parcial

---

## rexus_styles.py
**Resumen:** Centraliza estilos, fuentes y colores para la UI/UX de la aplicación usando PyQt6.

**Hallazgos:**
- Facilita la consistencia visual y el mantenimiento.
- No hay validación de valores de color/fuente.
- No hay soporte para temas oscuros/claros dinámicos.
- No hay internacionalización.
- No hay logging ni control de errores.

**Riesgos:**
- Cambios manuales pueden romper la consistencia visual.
- Valores hardcodeados pueden dificultar personalización futura.

**Recomendaciones:**
- Considerar soporte para temas dinámicos.
- Validar valores de entrada si se exponen a usuarios.
- Documentar dependencias de PyQt6.

**Cumplimiento:**
- MITRE CWE: N/A (no riesgos directos de seguridad)
- OWASP: N/A
- MIT Secure Coding: N/A

---

## utilitarios y backups
**Resumen:**
- No expone rutas ni datos sensibles en logs, pero utiliza print para errores (mejorable: logging seguro).
- No hay hardcodeo de credenciales ni uso de funciones peligrosas como eval/exec.
- No hay validación de permisos de archivos antes de eliminar o comprimir (riesgo bajo, pero recomendable chequear permisos).
- No hay cifrado de backups, solo compresión (no es crítico, pero recomendable para entornos sensibles).

**Riesgos:**
- Pérdida de logs si la compresión/eliminación falla y no hay backup previo.
- Uso de print para errores puede exponer rutas en consola/logs.
- Si se expone a entrada de usuario, riesgo de path traversal.

**Recomendaciones:**
- Documentar claramente el comportamiento de eliminación tras compresión.
- Validar permisos antes de eliminar/comprimir/restaurar archivos.
- Sanitizar nombres de archivos/directorios si hay entrada externa.
- Considerar cifrado de backups para mayor seguridad.
- Considerar persistencia del scheduler (servicio o daemon).

**Cumplimiento:**
- MIT Secure Coding: Cumple parcialmente (manejo de archivos, errores, documentación, concurrencia)

---

## cache_manager.py
Sistema de caché inteligente en memoria con TTL, compresión, métricas, limpieza automática y decoradores para cachear funciones. Usa serialización (pickle/json), compresión (gzip), locking y estadísticas avanzadas.

**Hallazgos:**
- Buen uso de locking (threading.RLock) para concurrencia segura.
- Serialización segura (json para tipos simples, pickle para complejos). Pickle puede ser riesgoso si se expone a datos no confiables (CWE-502).
- Compresión opcional de valores grandes (gzip).
- Decoradores para cachear funciones, con TTL configurable.
- Limpieza automática de entradas expiradas y política LRU para expulsión.
- Usar logging seguro en vez de print para errores.

---

## Cumplimiento General
- Cumple parcialmente buenas prácticas de seguridad y robustez, pero requiere refuerzo en logging seguro, validación de permisos y pruebas unitarias.
