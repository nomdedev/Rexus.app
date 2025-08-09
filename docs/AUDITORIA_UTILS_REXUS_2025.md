# Auditoría Profunda de Utilitarios - rexus/utils/

**Fecha:** 8 de agosto de 2025
**Estándares:** MITRE CWE, OWASP Top 10, MIT Secure Coding, NIST
---

## Estructura del Reporte
- Por cada archivo: resumen, hallazgos, riesgos, recomendaciones.
- Se actualizará progresivamente con cada utilitario auditado.

---

**Resumen:**
- No expone rutas ni datos sensibles en logs, pero utiliza print para errores (mejorable: logging seguro).
- No hay hardcodeo de credenciales ni uso de funciones peligrosas como eval/exec.
- No hay validación de permisos de archivos antes de eliminar o comprimir (riesgo bajo, pero recomendable chequear permisos).
- No hay cifrado de backups, solo compresión (no es crítico, pero recomendable para entornos sensibles).

**Riesgos:**
- Pérdida de logs si la compresión/eliminación falla y no hay backup previo.
- Uso de print para errores puede exponer rutas en consola/logs.
- Si se expone a entrada de usuario, riesgo de path traversal.

- Documentar claramente el comportamiento de eliminación tras compresión.

- MIT Secure Coding: Cumple parcialmente (manejo de archivos, errores, documentación)



**Resumen:**
Sistema completo de backup automatizado para las bases de datos del sistema. Incluye compresión, rotación, restauración, notificaciones, logging y scheduler automático.

**Hallazgos:**
- Buen uso de logging seguro y manejo de errores (logging, no print).
- Manejo robusto de archivos y directorios, con verificación de existencia y backups previos antes de sobrescribir.
- No hay cifrado de backups, solo compresión (recomendable para entornos sensibles).
- No hay validación de permisos de archivos antes de eliminar o restaurar (recomendable chequear permisos).
**Riesgos:**
- Pérdida de backups si la compresión/eliminación/restauración falla y no hay backup previo.
- No hay cifrado de backups (riesgo bajo, pero relevante para datos sensibles).
**Recomendaciones:**
- Validar permisos antes de eliminar/comprimir/restaurar archivos.
- Sanitizar nombres de archivos/directorios si hay entrada externa.
- Considerar cifrado de backups para mayor seguridad.
- Documentar claramente el comportamiento de eliminación y restauración.
- Considerar persistencia del scheduler (servicio o daemon).

- MIT Secure Coding: Cumple parcialmente (manejo de archivos, errores, documentación, concurrencia)

## cache_manager.py
Sistema de caché inteligente en memoria con TTL, compresión, métricas, limpieza automática y decoradores para cachear funciones. Usa serialización (pickle/json), compresión (gzip), locking y estadísticas avanzadas.
**Hallazgos:**
- Buen uso de locking (threading.RLock) para concurrencia segura.
- Serialización segura (json para tipos simples, pickle para complejos). Pickle puede ser riesgoso si se expone a datos no confiables (CWE-502).
- Compresión opcional de valores grandes (gzip).
- Decoradores para cachear funciones, con TTL configurable.
- Limpieza automática de entradas expiradas y política LRU para expulsión.

- Usar logging seguro en vez de print para errores.

**Cumplimiento:**
- OWASP: Cumple parcialmente (A8:2017-Insecure Deserialization, A6:2017-Sensitive Data Exposure)

**Resumen:**
**Hallazgos:**
- Uso correcto de enumeraciones para categorías, severidad y códigos de error (mejora la mantenibilidad y trazabilidad).
- Separación clara entre mensajes para usuario y técnicos (buenas prácticas de seguridad y UX).
- Truncado de valores en contexto para evitar exposición de datos sensibles (cumple CWE-209).
- No hay logging directo, pero provee funciones para formatear mensajes técnicos (debe integrarse con sistema de logging estructurado).
**Riesgos:**
- Si el contexto es controlado por el usuario, podría manipular mensajes o sugerencias (riesgo bajo, CWE-117).
- No hay soporte multilenguaje (i18n), lo que limita la escalabilidad internacional.

- Validar y sanear el contexto recibido antes de personalizar mensajes.
- Considerar soporte para internacionalización de mensajes.
- Documentar claramente el uso seguro del contexto en la personalización de mensajes.

**Cumplimiento:**
- MITRE CWE: Cumple parcialmente (CWE-209, CWE-117, CWE-778)
- OWASP: Cumple parcialmente (A6:2017-Sensitive Data Exposure, A10:2017-Insufficient Logging & Monitoring)
- MIT Secure Coding: Cumple parcialmente (manejo de errores, separación de mensajes, documentación)
## contextual_error_system.py


**Hallazgos:**
- Catálogo centralizado y extensible de errores por categoría y severidad.
- Historial y estadísticas de errores para monitoreo y auditoría.
- Soporte para handlers personalizados y señales Qt para integración con UI.
- Mensajes y sugerencias parametrizables con datos de contexto.
- Logging seguro configurado, pero no se observa integración directa con logs estructurados (solo print en algunos handlers).
- No hay validación/sanitización de datos de contexto antes de formatear mensajes (riesgo bajo de manipulación de UI o logs).
- No hay internacionalización (i18n), solo español.


**Recomendaciones:**
- Considerar soporte para internacionalización de mensajes y UI.
- Documentar claramente el uso seguro del contexto y handlers personalizados.
**Cumplimiento:**
- OWASP: Cumple parcialmente (A6:2017-Sensitive Data Exposure, A10:2017-Insufficient Logging & Monitoring)
- MIT Secure Coding: Cumple parcialmente (manejo de errores, separación de mensajes, documentación, integración UI)

---

## data_sanitizer.py

- Sanitización robusta de texto, SQL, HTML, emails y nombres de archivo (mitiga CWE-79, CWE-89, CWE-116, CWE-20).
- Remueve caracteres peligrosos, limita longitud y escapa HTML.
- Validación de emails y teléfonos con expresiones regulares.
- Limpieza recursiva de diccionarios y listas.
- No hay soporte para listas blancas/permitidas (solo listas negras).
**Riesgos:**
- La sanitización de SQL no es suficiente si se usan queries dinámicos (debe usarse siempre parámetros en queries).
- La sanitización de HTML puede ser evadida por técnicas avanzadas (considerar librerías como `bleach` para mayor robustez).
- No hay logging de intentos de entrada maliciosa (útil para monitoreo y alertas).

**Recomendaciones:**
- Documentar que la sanitización de SQL es solo una capa y no reemplaza el uso de parámetros.
**Cumplimiento:**
- MITRE CWE: Cumple parcialmente (CWE-20, CWE-79, CWE-89, CWE-116)

---
## database.py
**Resumen:**
Archivo alias que reexporta todo desde `database_manager.py` para mantener compatibilidad con imports existentes.

**Hallazgos:**
- No contiene lógica propia, solo reexporta símbolos.
- No hay riesgos de seguridad ni problemas de calidad en este archivo.

**Recomendaciones:**
- Mantener documentación clara sobre el propósito de alias y compatibilidad.

**Cumplimiento:**
- Sin riesgos ni incumplimientos.


## database_manager.py

**Resumen:**
Gestor avanzado de base de datos con pool de conexiones, manejo seguro de concurrencia, logging, transacciones y control de errores. Utiliza SQLite3 y threading para optimizar el acceso concurrente.

**Hallazgos:**
- No hay validación/sanitización de queries ni parámetros (depende del uso externo, riesgo CWE-89 si se usa mal).
- No hay soporte para cifrado de base de datos ni conexiones (limitación de SQLite3).
**Riesgos:**
- Si se usan queries construidas dinámicamente sin sanitización, riesgo de inyección SQL (CWE-89).
- No hay cifrado de datos en reposo ni en tránsito (limitación de SQLite3, considerar para entornos críticos).
**Recomendaciones:**
- Documentar claramente que los queries y parámetros deben ser validados/saneados antes de usarse.
- Considerar integración con sistemas de auditoría y monitoreo de acceso para entornos sensibles.
- Evaluar alternativas con cifrado si se requiere mayor seguridad.

**Cumplimiento:**
- MITRE CWE: Cumple parcialmente (CWE-89, CWE-778)
## demo_data_generator.py


**Hallazgos:**
- No utiliza datos sensibles ni reales, solo ejemplos ficticios.
- No hay logging de generación ni control de uso (no crítico para datos demo).
- Permite detección de modo demo por variable de entorno.
- No hay soporte para generación de datos maliciosos o edge cases para pruebas de seguridad.

**Riesgos:**
- Si se reutilizan los datos demo en producción, podría haber confusión o exposición accidental.
- No hay generación de datos para pruebas de seguridad (inyección, XSS, etc.).
- Agregar logging opcional para auditoría de uso en entornos de testing.

- OWASP: Cumple (no expone datos reales, útil para testing seguro)
- MIT Secure Coding: Cumple (no hay manipulación de datos externos)
---
## demo_mode.py

**Resumen:**

**Hallazgos:**
- Generación y provisión de datos demo realistas para usuarios, obras, inventario, compras y logística.
- No hay generación de datos para pruebas de edge cases o seguridad.
- No hay advertencia explícita si se usan datos demo en producción.
- Si se habilita el modo demo en producción, puede haber exposición accidental de datos ficticios o confusión operativa.
- No hay logging/auditoría de uso del modo demo (útil para detectar activaciones accidentales o maliciosas).
- Considerar advertencias explícitas en la UI cuando el modo demo está activo.
- Agregar generación de datos para pruebas de edge cases y seguridad.
**Cumplimiento:**
- MITRE CWE: Sin riesgos directos (datos controlados, no sensibles)
## diagnostic_widget.py

**Hallazgos:**
- Uso de subprocess para ejecutar scripts de corrección (riesgo de seguridad si no se controla el input).
- No hay validación/sanitización de los datos de error antes de mostrarlos (riesgo bajo de XSS en UI, CWE-79).
- El reporte de error se guarda en archivo local, pero no hay envío automático ni integración con sistemas de tickets.
- No hay internacionalización (i18n), solo español.

**Recomendaciones:**
- Considerar soporte para internacionalización de la UI.
**Cumplimiento:**
- MIT Secure Coding: Cumple parcialmente (diagnóstico, manejo de errores, integración UI)
---

## error_handler.py

**Resumen:**
Sistema centralizado de manejo de errores para la aplicación. Incluye logging estructurado, decoradores para captura segura de errores, excepciones personalizadas y fallback para mostrar errores al usuario.

**Hallazgos:**
- Logging estructurado de errores críticos y excepciones no capturadas.
- Decoradores para captura de errores en funciones y validación de conexión a base de datos.
- Excepciones personalizadas para base de datos, validación y seguridad.
- Fallback para mostrar errores en consola si PyQt6 no está disponible.
- Instalación de un manejador global de errores (`sys.excepthook`).
- No hay integración con sistemas de monitoreo externo o alertas automáticas.
- No hay internacionalización (i18n) de los mensajes de error.

**Riesgos:**
- Si el logging falla o no está configurado, los errores pueden perderse.
- No hay notificación automática a soporte o monitoreo externo en caso de errores críticos.

**Recomendaciones:**
- Considerar integración con sistemas de monitoreo/alertas para errores críticos.
- Agregar soporte para internacionalización de mensajes de error.
- Documentar claramente el uso de los decoradores y excepciones personalizadas.

**Cumplimiento:**
- MITRE CWE: Cumple parcialmente (CWE-778, CWE-209)
- OWASP: Cumple parcialmente (A10:2017-Insufficient Logging & Monitoring)
- MIT Secure Coding: Cumple parcialmente (manejo de errores, logging estructurado)

---

## error_manager.py

**Resumen:**
Sistema de gestión de errores contextualizados con catálogo centralizado, tipos, severidad, sugerencias, detalles técnicos y utilidades para mostrar mensajes en la UI. Permite personalización de mensajes y sugerencias según contexto y severidad.

**Hallazgos:**
- Catálogo extensible de errores con códigos, títulos, mensajes, sugerencias y detalles técnicos.
- Utilidades para mostrar errores y validaciones en la UI con PyQt6.
- Personalización de mensajes y sugerencias usando datos de contexto.
- Soporte para severidad, tipos y ayuda contextual.
- No hay logging estructurado de errores mostrados ni auditoría de uso.
- No hay internacionalización (i18n), solo español.
- No hay integración con sistemas de monitoreo externo o tickets.
- No hay validación/sanitización de los datos de contexto antes de usarlos en mensajes (riesgo bajo de manipulación de UI).

**Riesgos:**
- Si los datos de contexto provienen de fuentes externas, posible manipulación de mensajes o UI (CWE-79).
- Los errores solo se muestran en la UI, no quedan registrados para auditoría o monitoreo.

**Recomendaciones:**
- Validar y sanear los datos de contexto antes de usarlos en mensajes y sugerencias.
- Agregar logging estructurado de errores mostrados y uso del sistema de errores.
- Considerar integración con sistemas de monitoreo/tickets y soporte para internacionalización.
- Documentar claramente el uso seguro de los datos de contexto.

**Cumplimiento:**
- MITRE CWE: Cumple parcialmente (CWE-79, CWE-778)
- OWASP: Cumple parcialmente (A6:2017-Sensitive Data Exposure, A10:2017-Insufficient Logging & Monitoring)
- MIT Secure Coding: Cumple parcialmente (manejo de errores, integración UI)

---

## dialogs.py

**Resumen:**
Sistema de utilidades para mostrar diálogos de información, advertencia, error, pregunta y confirmación de forma consistente usando PyQt6. Incluye funciones con títulos predeterminados y manejo básico de errores.

**Hallazgos:**
- Uso correcto de QMessageBox para mostrar diálogos modales en la UI.
- Manejo de excepciones para evitar fallos en la UI si ocurre un error al mostrar el diálogo.
- Funciones de conveniencia para títulos predeterminados y confirmaciones.
- No hay logging estructurado de errores al mostrar diálogos (solo print).
- No hay internacionalización (i18n), solo español.
- No hay validación/sanitización de los mensajes antes de mostrarlos (riesgo bajo de XSS en UI, CWE-79).

**Riesgos:**
- Si los mensajes provienen de fuentes externas, posible manipulación de la UI (CWE-79).
- Los errores al mostrar diálogos solo se imprimen por consola, no quedan registrados para auditoría.

**Recomendaciones:**
- Validar y sanear los mensajes antes de mostrarlos si provienen de fuentes externas.
- Agregar logging estructurado de errores al mostrar diálogos.
- Considerar soporte para internacionalización de los títulos y mensajes.

**Cumplimiento:**
- MITRE CWE: Cumple parcialmente (CWE-79, CWE-778)
- OWASP: Cumple parcialmente (A6:2017-Sensitive Data Exposure, A10:2017-Insufficient Logging & Monitoring)
- MIT Secure Coding: Cumple parcialmente (manejo de errores, integración UI)

---

## dialog_utils.py

**Resumen:**
Utilidades avanzadas para diálogos CRUD y formularios reutilizables en PyQt6. Incluye formularios dinámicos, validación, confirmaciones, gestión de diálogos de creación, edición y eliminación, y configuración estándar de formularios.

**Hallazgos:**
- Implementa formularios dinámicos y reutilizables con validación de campos requeridos.
- Manejo de errores y mensajes de éxito/fracaso integrados en la UI.
- Confirmaciones de eliminación y gestión de callbacks para operaciones CRUD.
- No hay sanitización/validación avanzada de los datos ingresados (solo campos requeridos).
- No hay logging estructurado de errores ni de operaciones CRUD realizadas.
- No hay internacionalización (i18n), solo español.
- No hay control de tipos o formatos avanzados en los datos ingresados (solo validación básica).

**Riesgos:**
- Si los datos ingresados provienen de usuarios, posible riesgo de XSS o datos maliciosos si no se validan/sanean antes de usarse (CWE-79, CWE-20).
- Los errores solo se muestran en la UI, no quedan registrados para auditoría.

**Recomendaciones:**
- Agregar sanitización y validación avanzada de los datos ingresados antes de procesarlos o almacenarlos.
- Agregar logging estructurado de errores y operaciones CRUD para trazabilidad y auditoría.
- Considerar soporte para internacionalización de los textos y mensajes.
- Documentar claramente el uso seguro de los datos ingresados en los formularios.

**Cumplimiento:**
- MITRE CWE: Cumple parcialmente (CWE-20, CWE-79, CWE-778)
- OWASP: Cumple parcialmente (A6:2017-Sensitive Data Exposure, A10:2017-Insufficient Logging & Monitoring)
- MIT Secure Coding: Cumple parcialmente (validación básica, integración UI)

---

## error_notification_widget.py

**Resumen:**
Widget visual moderno para mostrar mensajes de error contextualizados en la UI, con soporte para severidad, sugerencias, detalles técnicos, animaciones y notificaciones no intrusivas. Integra señales Qt y utilidades para mostrar, copiar y gestionar errores.

**Hallazgos:**
- Presentación visual clara y diferenciada por severidad (info, warning, error, crítico).
- Sugerencias y detalles técnicos accesibles desde la UI.
- Animaciones y auto-dismiss para mensajes informativos y advertencias.
- Soporte para copiar detalles técnicos al portapapeles.
- Manejo de múltiples notificaciones y límite de errores visibles.
- No hay logging estructurado de errores mostrados ni auditoría de uso.
- No hay internacionalización (i18n), solo español.
- No hay validación/sanitización de los datos de error/contexto antes de mostrarlos (riesgo bajo de manipulación de UI).

**Riesgos:**
- Si los datos de error/contexto provienen de fuentes externas, posible manipulación de la UI (CWE-79).
- Los errores solo se muestran en la UI, no quedan registrados para auditoría o monitoreo.

**Recomendaciones:**
- Validar y sanear los datos de error/contexto antes de mostrarlos en la UI.
- Agregar logging estructurado de errores mostrados y uso del widget.
- Considerar soporte para internacionalización de los textos y mensajes.
- Documentar claramente el uso seguro de los datos de contexto.

**Cumplimiento:**
- MITRE CWE: Cumple parcialmente (CWE-79, CWE-778)
- OWASP: Cumple parcialmente (A6:2017-Sensitive Data Exposure, A10:2017-Insufficient Logging & Monitoring)
- MIT Secure Coding: Cumple parcialmente (manejo de errores, integración UI)

---

## feedback_manager.py

**Resumen:**
Sistema centralizado para feedback visual, integrado con el sistema de temas y señales Qt. Permite mostrar mensajes, confirmaciones y estados visuales consistentes en toda la aplicación, con soporte para estilos dinámicos y logging.

**Hallazgos:**
- Integración avanzada con temas y estilos personalizados para cada tipo de mensaje (info, success, warning, error).
- Uso de señales Qt para notificar eventos de feedback.
- Logging estructurado de eventos de feedback y errores al mostrar mensajes.
- Fallback seguro si ocurre un error al mostrar el mensaje.
- No hay internacionalización (i18n), solo español.
- No hay validación/sanitización de los mensajes antes de mostrarlos (riesgo bajo de XSS en UI, CWE-79).
- No hay auditoría de uso de feedback ni integración con sistemas externos de monitoreo.

**Riesgos:**
- Si los mensajes provienen de fuentes externas, posible manipulación de la UI (CWE-79).
- Los eventos de feedback solo quedan en logs locales, no hay monitoreo externo.

**Recomendaciones:**
- Validar y sanear los mensajes antes de mostrarlos si provienen de fuentes externas.
- Considerar soporte para internacionalización de los textos y mensajes.
- Documentar claramente el uso seguro de los datos en los mensajes de feedback.
- Considerar integración con sistemas de monitoreo/auditoría para eventos críticos.

**Cumplimiento:**
- MITRE CWE: Cumple parcialmente (CWE-79, CWE-778)
- OWASP: Cumple parcialmente (A6:2017-Sensitive Data Exposure, A10:2017-Insufficient Logging & Monitoring)
- MIT Secure Coding: Cumple parcialmente (manejo de errores, integración UI, logging)

---

# Auditoría de dependencias: requirements.txt (08/08/2025)

---

## format_utils.py
---

## sql_script_loader.py
---

## sql_security.py
---

## sql_query_manager.py
---

## smart_tooltips.py
---

## security.py
---

## security_backup.py
---

## security_clean.py
---

## security_fixed.py
---

## password_security.py
---

## theme_manager.py
---

## unified_sanitizer.py

**Resumen:**
Sistema unificado de sanitización de datos: strings, números, emails, HTML, SQL, URLs, teléfonos y diccionarios. Incluye patrones avanzados para SQLi/XSS, validación de rangos y funciones de conveniencia globales.

**Hallazgos:**
- Uso de patrones avanzados para detección y remoción de SQL Injection y XSS.
- Sanitización configurable de strings, números, emails, teléfonos, URLs y diccionarios.
- Escape de HTML/XML y soporte para tags seguros (básico, no usa librerías externas).
- Validación de emails, rangos numéricos y formatos de teléfono/URL.
- Logging de advertencias ante errores de sanitización.
- No hay hardcodeo de credenciales ni uso de funciones peligrosas.
- No hay integración con librerías especializadas (ej: bleach para HTML, sqlparse para SQL).
- No hay internacionalización (i18n) de mensajes/logs.
- No hay logging/auditoría de intentos de entrada maliciosa ni integración con sistemas de monitoreo.

**Riesgos:**
- La sanitización de HTML y SQL es básica y puede ser evadida por técnicas avanzadas (CWE-79, CWE-89).
- No hay logging/auditoría de intentos de entrada maliciosa ni alertas automáticas.
- No hay soporte para localización o internacionalización de mensajes/logs.

**Recomendaciones:**
- Integrar librerías especializadas para sanitización de HTML (bleach) y SQL en entornos críticos.
- Agregar logging/auditoría de intentos de entrada maliciosa y alertas automáticas.
- Considerar soporte para internacionalización de mensajes/logs.
- Documentar claramente las limitaciones de la sanitización y los patrones usados.

**Cumplimiento:**
- MITRE CWE: Cumple parcialmente (CWE-79, CWE-89, CWE-116, CWE-209)
- OWASP: Cumple parcialmente (A1:2017-Injection, A7:2017-XSS, A10:2017-Insufficient Logging & Monitoring)
- MIT Secure Coding: Cumple parcialmente (validación, sanitización, documentación)

**Resumen:**
Gestor centralizado de temas visuales para PyQt6, con persistencia, señales, callbacks, generación dinámica de estilos y soporte para fuentes. Permite personalización avanzada y compatibilidad con temas oscuros/claros.

**Hallazgos:**
- Uso de señales Qt y callbacks para notificar cambios de tema y fuente.
- Persistencia de preferencias en archivo JSON, con manejo de errores y valores por defecto.
- Generación dinámica de stylesheets a partir de paletas de colores y metadatos.
- Logging estructurado de eventos y errores de tema.
- No hay hardcodeo de credenciales ni acceso a recursos externos peligrosos.
- No hay validación/sanitización de los datos leídos del archivo de preferencias (riesgo bajo si solo se manipula internamente).
- No hay internacionalización (i18n) de nombres de temas, fuentes o mensajes de log.
- No hay integración directa con sistemas de monitoreo externo o analítica de uso.
- No hay control de acceso a la modificación de preferencias (riesgo bajo en entorno desktop).

**Riesgos:**
- Si el archivo de preferencias es manipulado externamente, posible corrupción de estado o errores de carga.
- No hay logging/auditoría de cambios de tema por usuario ni de errores críticos.
- No hay soporte para localización o internacionalización de nombres de temas o mensajes.

**Recomendaciones:**
- Validar y sanear los datos leídos del archivo de preferencias antes de aplicarlos.
- Agregar logging/auditoría de cambios de tema por usuario y errores críticos.
- Considerar soporte para internacionalización de nombres de temas y mensajes.
- Documentar claramente el formato y la ubicación del archivo de preferencias.

**Cumplimiento:**
- MITRE CWE: Cumple parcialmente (CWE-209, CWE-778)
- OWASP: Cumple parcialmente (A10:2017-Insufficient Logging & Monitoring)
- MIT Secure Coding: Cumple parcialmente (persistencia, logging, documentación)

**Resumen:**
Sistema avanzado para hash y verificación de contraseñas usando Argon2, bcrypt y PBKDF2, con fallback SHA-256 legacy. Incluye detección de método, migración de hashes antiguos, validación de fortaleza y generación de salt seguro.

**Hallazgos:**
- Selección automática del mejor algoritmo disponible (Argon2 > bcrypt > PBKDF2 > SHA-256).
- Soporte para migración y detección de hashes legacy inseguros.
- Validación robusta de fortaleza de contraseñas (longitud, complejidad, patrones débiles).
- Manejo de errores y excepciones personalizado.
- No hay hardcodeo de credenciales ni uso de funciones peligrosas.
- No hay logging/auditoría de intentos fallidos de login ni de migraciones de hash.
- No hay internacionalización (i18n) de mensajes de error.
- No hay integración directa con sistemas de monitoreo externo o SIEM.
- No hay control de intentos fallidos de login ni bloqueo automático.

**Riesgos:**
- Si se permite el uso de hashes legacy (SHA-256), riesgo de ataques por fuerza bruta (CWE-916).
- No hay logging/auditoría de intentos fallidos de login ni de migraciones de hash.
- No hay soporte para localización o internacionalización de mensajes/logs.

**Recomendaciones:**
- Forzar migración de hashes legacy a algoritmos modernos en el primer login exitoso.
- Agregar logging/auditoría de intentos fallidos de login y migraciones de hash.
- Considerar integración con sistemas de monitoreo externo/SIEM para eventos críticos.
- Documentar claramente las limitaciones y el flujo de migración de hashes.

**Cumplimiento:**
- MITRE CWE: Cumple parcialmente (CWE-916, CWE-209)
- OWASP: Cumple parcialmente (A2:2017-Broken Authentication, A6:2017-Sensitive Data Exposure, A10:2017-Insufficient Logging & Monitoring)
- MIT Secure Coding: Cumple parcialmente (hashing, validación, documentación)

**Resumen:**
Utilidades críticas de seguridad (versión fixed): hashing y verificación de contraseñas, sanitización de entrada, validación de emails e identificadores SQL, generación de tokens, validación de fortaleza de contraseñas y logging de eventos de seguridad a archivo.

**Hallazgos:**
- Uso de PBKDF2 con SHA-256 y salt aleatorio para hashing de contraseñas (seguro, aunque menos robusto que bcrypt/argon2).
- Sanitización básica de entrada (escapado de caracteres y remoción de scripts/eventos JS).
- Validación de emails y de identificadores SQL (nombres de tablas/campos).
- Generación de tokens seguros con `secrets`.
- Validación de fortaleza de contraseñas con criterios estándar.
- Logging estructurado de eventos de seguridad a archivo dedicado (`logs/security.log`).
- No hay hardcodeo de credenciales ni uso de funciones peligrosas.
- No hay internacionalización (i18n) de mensajes/logs.
- No hay integración directa con sistemas de monitoreo externo o SIEM.
- No hay control de intentos fallidos de login ni bloqueo automático.

**Riesgos:**
- El uso de PBKDF2 es seguro, pero bcrypt/argon2 son más robustos ante ataques modernos (CWE-916).
- La sanitización de entrada es básica y puede ser evadida por técnicas avanzadas de XSS o inyección (CWE-79, CWE-20).
- No hay logging/auditoría de intentos fallidos de login ni alertas automáticas ante patrones sospechosos.
- No hay soporte para localización o internacionalización de mensajes/logs.

**Recomendaciones:**
- Considerar el uso de bcrypt o argon2 para hashing de contraseñas en entornos críticos.
- Mejorar la sanitización de entrada usando librerías especializadas para XSS y validación de input.
- Agregar control y logging de intentos fallidos de login y bloqueo automático tras múltiples fallos.
- Considerar integración con sistemas de monitoreo externo/SIEM para eventos críticos.
- Documentar claramente las limitaciones de la sanitización y los algoritmos usados.

**Cumplimiento:**
- MITRE CWE: Cumple parcialmente (CWE-79, CWE-916, CWE-20, CWE-209)
- OWASP: Cumple parcialmente (A2:2017-Broken Authentication, A6:2017-Sensitive Data Exposure, A10:2017-Insufficient Logging & Monitoring)
- MIT Secure Coding: Cumple parcialmente (hashing, logging, validación, documentación)

**Resumen:**
Utilidades críticas de seguridad (versión clean): hashing y verificación de contraseñas, sanitización de entrada, validación de emails e identificadores SQL, generación de tokens, validación de fortaleza de contraseñas y logging de eventos de seguridad.

**Hallazgos:**
- Uso de PBKDF2 con SHA-256 y salt aleatorio para hashing de contraseñas (buena práctica, aunque se recomienda bcrypt/argon2 para mayor robustez).
- Sanitización básica de entrada para prevenir XSS (escapado de caracteres y patrones comunes).
- Validación de emails y de identificadores SQL (nombres de tablas/campos).
- Generación de tokens seguros con `secrets`.
- Validación de fortaleza de contraseñas con criterios estándar.
- Logging estructurado de eventos de seguridad, configurable por logger dedicado.
- No hay hardcodeo de credenciales ni uso de funciones peligrosas.
- No hay internacionalización (i18n) de mensajes de error o logs.
- No hay integración directa con sistemas de monitoreo externo o SIEM.
- No hay control de intentos fallidos de login ni bloqueo automático.

**Riesgos:**
- El uso de PBKDF2 es seguro, pero bcrypt/argon2 son más robustos ante ataques modernos (CWE-916).
- La sanitización de entrada es básica y puede ser evadida por técnicas avanzadas de XSS (CWE-79).
- No hay logging/auditoría de intentos fallidos de login ni alertas automáticas ante patrones sospechosos.
- No hay soporte para localización o internacionalización de mensajes/logs.

**Recomendaciones:**
- Considerar el uso de bcrypt o argon2 para hashing de contraseñas en entornos críticos.
- Mejorar la sanitización de entrada usando librerías especializadas para XSS (ej: `bleach`).
- Agregar control y logging de intentos fallidos de login y bloqueo automático tras múltiples fallos.
- Considerar integración con sistemas de monitoreo externo/SIEM para eventos críticos.
- Documentar claramente las limitaciones de la sanitización y los algoritmos usados.

**Cumplimiento:**
- MITRE CWE: Cumple parcialmente (CWE-79, CWE-916, CWE-209)
- OWASP: Cumple parcialmente (A2:2017-Broken Authentication, A6:2017-Sensitive Data Exposure, A10:2017-Insufficient Logging & Monitoring)
- MIT Secure Coding: Cumple parcialmente (hashing, logging, validación, documentación)

**Resumen:**
Utilidades de seguridad (versión alternativa/backup): hashing y verificación de contraseñas, sanitización de entrada, validación de emails, generación de tokens, validación de nombres de archivo y logging de eventos de seguridad.

**Hallazgos:**
- Uso de PBKDF2 con SHA-256 y salt aleatorio para hashing de contraseñas (seguro, aunque menos robusto que bcrypt/argon2).
- Sanitización básica de entrada (remueve caracteres peligrosos y limita longitud).
- Validación de emails y de nombres de archivo (incluye chequeo de nombres reservados en Windows).
- Generación de tokens seguros con `secrets`.
- Logging de eventos de seguridad configurable por nivel.
- No hay hardcodeo de credenciales ni uso de funciones peligrosas.
- No hay internacionalización (i18n) de mensajes/logs.
- No hay integración directa con sistemas de monitoreo externo o SIEM.
- No hay control de intentos fallidos de login ni bloqueo automático.

**Riesgos:**
- El uso de PBKDF2 es seguro, pero bcrypt/argon2 son más robustos ante ataques modernos (CWE-916).
- La sanitización de entrada es básica y puede ser evadida por técnicas avanzadas de XSS o inyección (CWE-79, CWE-20).
- No hay logging/auditoría de intentos fallidos de login ni alertas automáticas ante patrones sospechosos.
- No hay soporte para localización o internacionalización de mensajes/logs.

**Recomendaciones:**
- Considerar el uso de bcrypt o argon2 para hashing de contraseñas en entornos críticos.
- Mejorar la sanitización de entrada usando librerías especializadas para XSS y validación de input.
- Agregar control y logging de intentos fallidos de login y bloqueo automático tras múltiples fallos.
- Considerar integración con sistemas de monitoreo externo/SIEM para eventos críticos.
- Documentar claramente las limitaciones de la sanitización y los algoritmos usados.

**Cumplimiento:**
- MITRE CWE: Cumple parcialmente (CWE-79, CWE-916, CWE-20, CWE-209)
- OWASP: Cumple parcialmente (A2:2017-Broken Authentication, A6:2017-Sensitive Data Exposure, A10:2017-Insufficient Logging & Monitoring)
- MIT Secure Coding: Cumple parcialmente (hashing, logging, validación, documentación)

**Resumen:**
Utilidades críticas de seguridad: hashing y verificación de contraseñas, sanitización de entrada, validación de emails e identificadores SQL, generación de tokens, validación de fortaleza de contraseñas y logging de eventos de seguridad.

**Hallazgos:**
- Uso de PBKDF2 con SHA-256 y salt aleatorio para hashing de contraseñas (buena práctica, aunque se recomienda usar bcrypt/argon2 para mayor robustez).
- Sanitización básica de entrada para prevenir XSS (escapado de caracteres y patrones comunes).
- Validación de emails y de identificadores SQL (nombres de tablas/campos).
- Generación de tokens seguros con `secrets`.
- Validación de fortaleza de contraseñas con criterios estándar.
- Logging estructurado de eventos de seguridad, configurable por logger dedicado.
- No hay hardcodeo de credenciales ni uso de funciones peligrosas.
- No hay internacionalización (i18n) de mensajes de error o logs.
- No hay integración directa con sistemas de monitoreo externo o SIEM.
- No hay control de intentos fallidos de login ni bloqueo automático.

**Riesgos:**
- El uso de PBKDF2 es seguro, pero bcrypt/argon2 son más robustos ante ataques modernos (CWE-916).
- La sanitización de entrada es básica y puede ser evadida por técnicas avanzadas de XSS (CWE-79).
- No hay logging/auditoría de intentos fallidos de login ni alertas automáticas ante patrones sospechosos.
- No hay soporte para localización o internacionalización de mensajes/logs.

**Recomendaciones:**
- Considerar el uso de bcrypt o argon2 para hashing de contraseñas en entornos críticos.
- Mejorar la sanitización de entrada usando librerías especializadas para XSS (ej: `bleach`).
- Agregar control y logging de intentos fallidos de login y bloqueo automático tras múltiples fallos.
- Considerar integración con sistemas de monitoreo externo/SIEM para eventos críticos.
- Documentar claramente las limitaciones de la sanitización y los algoritmos usados.

**Cumplimiento:**
- MITRE CWE: Cumple parcialmente (CWE-79, CWE-916, CWE-209)
- OWASP: Cumple parcialmente (A2:2017-Broken Authentication, A6:2017-Sensitive Data Exposure, A10:2017-Insufficient Logging & Monitoring)
- MIT Secure Coding: Cumple parcialmente (hashing, logging, validación, documentación)

**Resumen:**
Sistema avanzado de tooltips inteligentes y contextuales para la UI, con catálogo centralizado, soporte para tipos, ejemplos, atajos y personalización. Permite aplicar tooltips a widgets, formularios y tablas de PyQt6.

**Hallazgos:**
- Uso de dataclasses y enums para estructurar la configuración de tooltips (mejora mantenibilidad y claridad).
- Catálogo centralizado y extensible de tooltips por campo, tipo y módulo.
- Permite tooltips personalizados y temporales, con soporte para rich text y estadísticas de uso.
- No hay hardcodeo de credenciales ni acceso a recursos externos.
- No hay validación/sanitización de los textos de tooltip (riesgo bajo si provienen solo del código, pero relevante si se permite entrada externa).
- No hay logging/auditoría de uso de tooltips ni de errores al aplicar tooltips.
- No hay internacionalización (i18n), todos los textos y ejemplos están en español.
- No hay integración directa con sistemas de monitoreo o analítica de uso.
- El mapeo de campos y botones es estático y puede requerir mantenimiento frecuente.

**Riesgos:**
- Si se permite tooltips personalizados desde entrada externa, posible XSS o manipulación de la UI (CWE-79).
- No hay logging/auditoría de uso ni de errores, lo que dificulta la trazabilidad de problemas o mejoras de UX.
- No hay soporte para localización o internacionalización de tooltips.

**Recomendaciones:**
- Validar y sanear los textos de tooltips si se permite entrada externa o personalizada.
- Agregar logging/auditoría de uso y errores al aplicar tooltips.
- Considerar soporte para internacionalización y localización de tooltips.
- Documentar claramente el uso seguro de tooltips personalizados.
- Considerar integración con sistemas de analítica de uso para mejorar la UX.

**Cumplimiento:**
- MITRE CWE: Cumple parcialmente (CWE-79, CWE-209)
- OWASP: Cumple parcialmente (A6:2017-Sensitive Data Exposure, A10:2017-Insufficient Logging & Monitoring)
- MIT Secure Coding: Cumple parcialmente (modularidad, documentación, integración UI)

**Resumen:**
Gestor centralizado para cargar, cachear, validar y ejecutar consultas SQL desde archivos externos. Permite parametrización, validación básica de sintaxis y listado de queries disponibles por módulo.

**Hallazgos:**
- Uso de rutas relativas y estructura modular para organización de scripts SQL.
- Cache de consultas para eficiencia y reducción de I/O.
- Validación básica de sintaxis SQL (palabras clave, paréntesis balanceados, no vacío).
- Permite parametrización de queries, pero usa `.format()` para reemplazo (riesgo si se usan datos de usuario sin sanitizar).
- No hay logging estructurado (solo print para eventos de carga y limpieza de cache).
- No hay validación/sanitización de parámetros de formateo antes de aplicar `.format()`.
- No hay control de acceso ni auditoría de uso de queries.
- No hay internacionalización (i18n) de mensajes.
- No hay integración directa con sistemas de monitoreo o alertas.

**Riesgos:**
- Si los parámetros de formateo provienen de entrada externa, posible inyección SQL o manipulación de la consulta (CWE-89).
- No hay logging/auditoría de uso ni de errores de carga/ejecución.
- El uso de `.format()` para queries puede ser riesgoso si no se controla el input.

**Recomendaciones:**
- Documentar claramente que los parámetros deben ser validados/sanitizados antes de usarse en `.format()`.
- Agregar logging estructurado para eventos críticos y errores.
- Considerar integración con sistemas de monitoreo/auditoría para uso de queries.
- Considerar soporte para internacionalización de mensajes.
- Evaluar el uso de parámetros nativos de la base de datos en vez de `.format()` para mayor seguridad.

**Cumplimiento:**
- MITRE CWE: Cumple parcialmente (CWE-89, CWE-209)
- OWASP: Cumple parcialmente (A1:2017-Injection, A10:2017-Insufficient Logging & Monitoring)
- MIT Secure Coding: Cumple parcialmente (modularidad, documentación, separación de lógica)

**Resumen:**
Módulo de utilidades para seguridad SQL: validación de nombres de tablas, sanitización de parámetros, construcción segura de queries y lista blanca de tablas permitidas. Incluye builder de queries y excepciones personalizadas.

**Hallazgos:**
- Uso de lista blanca para tablas permitidas, configurable en tiempo de ejecución.
- Validación estricta de nombres de tablas y columnas (caracteres, longitud, patrones peligrosos).
- Sanitización básica de parámetros SQL (elimina caracteres peligrosos).
- Builder de queries seguro: solo permite queries parametrizadas y previene comandos peligrosos en WHERE.
- No hay hardcodeo de credenciales ni uso de funciones peligrosas.
- No hay logging ni auditoría de intentos de acceso o violaciones detectadas.
- No hay internacionalización (i18n) de mensajes de error.
- No hay integración directa con sistemas de monitoreo o alertas.
- La lista blanca puede ser modificada en tiempo de ejecución (útil, pero requiere control de acceso).

**Riesgos:**
- Si la lista blanca es modificada sin control, puede habilitar acceso a tablas no deseadas (CWE-284).
- La sanitización de parámetros es básica y no reemplaza el uso de parámetros en queries (CWE-89).
- No hay logging/auditoría de intentos de acceso a tablas no permitidas o patrones peligrosos.
- No hay soporte para logging estructurado ni alertas ante violaciones.

**Recomendaciones:**
- Documentar claramente que la sanitización es solo una capa y no reemplaza el uso de parámetros en queries.
- Agregar logging/auditoría de intentos de acceso a tablas no permitidas y patrones peligrosos detectados.
- Controlar el acceso a la modificación de la lista blanca de tablas.
- Considerar integración con sistemas de monitoreo/alertas para violaciones de seguridad SQL.
- Considerar soporte para internacionalización de mensajes de error.

**Cumplimiento:**
- MITRE CWE: Cumple parcialmente (CWE-89, CWE-284, CWE-209)
- OWASP: Cumple parcialmente (A1:2017-Injection, A5:2017-Broken Access Control, A10:2017-Insufficient Logging & Monitoring)
- MIT Secure Coding: Cumple parcialmente (validación, separación de lógica, documentación)

**Resumen:**
Utilidad para cargar y ejecutar scripts SQL desde archivos, con logging de errores y advertencias. Permite parametrización y ejecución segura a través de cursores de base de datos.

**Hallazgos:**
- Uso correcto de rutas relativas y detección automática del directorio de scripts.
- Utiliza logging estructurado para advertencias y errores.
- No hay hardcodeo de credenciales ni uso de funciones peligrosas.
- Permite parametrización de queries, mitigando riesgos de inyección SQL si se usa correctamente.
- No hay validación/sanitización del nombre del script recibido (riesgo bajo de path traversal si se expone a entrada externa).
- No hay control de acceso a los scripts ni auditoría de uso.
- No hay internacionalización (i18n) de mensajes de log.
- No hay manejo de encoding configurable (usa utf-8 por defecto).

**Riesgos:**
- Si el nombre del script proviene de entrada externa, posible path traversal o acceso a scripts no autorizados (CWE-22).
- Si los scripts contienen queries dinámicos sin parámetros, riesgo de inyección SQL (CWE-89).
- No hay auditoría de uso ni control de acceso a la ejecución de scripts.

**Recomendaciones:**
- Validar y sanear el nombre del script antes de cargarlo, especialmente si proviene de entrada externa.
- Documentar claramente que los scripts deben usar siempre parámetros y nunca concatenar datos de usuario.
- Considerar agregar auditoría de uso y control de acceso a la ejecución de scripts.
- Considerar soporte para internacionalización de mensajes de log.

**Cumplimiento:**
- MITRE CWE: Cumple parcialmente (CWE-22, CWE-89, CWE-209)
- OWASP: Cumple parcialmente (A1:2017-Injection, A5:2017-Broken Access Control, A10:2017-Insufficient Logging & Monitoring)
- MIT Secure Coding: Cumple parcialmente (manejo de archivos, logging, documentación)

**Resumen:**
Módulo de utilidades de formateo para moneda, fechas, números, texto, estados, tablas y visualización general. Incluye clases especializadas y una función global para formateo conveniente.

**Hallazgos:**
- Buenas prácticas de separación de responsabilidades y reutilización de código.
- No hay uso de funciones peligrosas (`eval`, `exec`, `pickle`, etc.).
- No hay hardcodeo de credenciales ni acceso a recursos externos.
- No hay validación/sanitización avanzada de entradas antes de formatear (riesgo bajo, pero relevante si se usan datos externos).
- No hay logging ni auditoría de uso de los formateadores.
- No hay internacionalización (i18n), todos los textos y formatos están en español y formato local.
- No hay control de errores centralizado, pero sí manejo de excepciones en cada método.
- El formateo de fechas y números asume formatos específicos, lo que puede causar errores silenciosos si la entrada no es válida.
- El formateo de teléfonos y códigos es específico para Argentina, lo que limita la escalabilidad internacional.
- No hay soporte para personalización de formatos por usuario o configuración externa.

**Riesgos:**
- Si se usan datos de usuario sin sanitizar, podría haber errores de visualización o manipulación de la UI (CWE-117, CWE-79).
- El formateo de fechas/números puede fallar silenciosamente y mostrar datos incorrectos si la entrada es inesperada.
- No hay logging de errores de formateo, lo que dificulta la trazabilidad de problemas en producción.
- El formateo de estados y prioridades depende de diccionarios hardcodeados, lo que dificulta la extensión o localización.

**Recomendaciones:**
- Validar y sanear entradas antes de formatear, especialmente si provienen de usuarios o fuentes externas.
- Agregar logging estructurado para errores de formateo y uso de utilidades críticas.
- Considerar soporte para internacionalización (i18n) y localización de formatos/textos.
- Permitir personalización de formatos y textos a través de configuración externa.
- Documentar claramente los formatos esperados y las limitaciones regionales (ej: teléfonos argentinos).
- Considerar integración con sistemas de monitoreo para detectar patrones de errores de formateo.

**Cumplimiento:**
- MITRE CWE: Cumple parcialmente (CWE-117, CWE-79, CWE-209)
- OWASP: Cumple parcialmente (A6:2017-Sensitive Data Exposure, A10:2017-Insufficient Logging & Monitoring)
- MIT Secure Coding: Cumple parcialmente (manejo de errores, documentación, separación de lógica)

## Hallazgos
- Se incluyen dependencias clave para seguridad (cryptography, bcrypt), testing, monitoreo y utilidades modernas.
- Se listan módulos estándar de Python (`sqlite3`, `pathlib`), que no requieren instalación vía pip (puede causar confusión o warnings).
- No se especifican hashes de integridad para los paquetes (recomendado para entornos de alta seguridad, PEP 655).
- No se utiliza un archivo de "constraints" para fijar versiones indirectas (mejora para reproducibilidad).
- No se observa uso de herramientas automáticas de escaneo de vulnerabilidades (como `safety`, `pip-audit`).
- Algunas dependencias opcionales están bien documentadas como tales.
- No hay dependencias obsoletas ni versiones inseguras detectadas en este listado (a la fecha de la auditoría).

## Riesgos y recomendaciones
- **Módulos estándar:** Eliminar `sqlite3` y `pathlib` del requirements.txt, ya que son parte de la librería estándar de Python y no deben instalarse por pip.
- **Hashes de integridad:** Considerar el uso de hashes SHA256 para cada paquete (ver PEP 655, pip --require-hashes) en entornos críticos.
- **Escaneo de vulnerabilidades:** Agregar `safety` o `pip-audit` como dependencia de desarrollo y ejecutar escaneos periódicos.
- **Constraints:** Usar un archivo `constraints.txt` para fijar versiones de dependencias indirectas y mejorar la reproducibilidad.
- **Actualización periódica:** Revisar y actualizar dependencias al menos cada 3 meses para evitar vulnerabilidades conocidas.
- **Documentación:** Mantener comentarios claros sobre dependencias opcionales y su propósito.

## Cumplimiento y estándares
- **OWASP Dependency-Check:** Parcialmente cumplido (faltan escaneos automáticos y hashes).
- **NIST SP 800-53:** Requiere gestión activa de vulnerabilidades y control de integridad.
- **MITRE CWE-1104:** Riesgo bajo, pero puede mejorar con escaneo y fijación de versiones.

## Estado general
El archivo requirements.txt es moderno y está bien documentado, pero puede mejorarse eliminando módulos estándar, agregando escaneo de vulnerabilidades y usando hashes de integridad para cumplir con los estándares internacionales de seguridad de dependencias.

---

