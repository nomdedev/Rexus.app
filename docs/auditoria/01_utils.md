# AUDITORÍA MÓDULO UTILS

## data_sanitizer.py

**Resumen:**
Clase para sanitización de datos: cadenas, SQL, numéricos y diccionarios. Aplica patrones para prevenir XSS y SQLi, y utiliza logging para advertencias.

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

**Resumen:**
Centraliza estilos, fuentes y colores para la UI/UX de la aplicación usando PyQt6.

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

## sql_security.py

**Resumen:**
Utilidades para validar y construir queries SQL de forma segura. Incluye validación de nombres de tablas/columnas y patrones de inyección.

**Hallazgos:**
- Buen enfoque de validación y logging de intentos peligrosos.
- Permite definir tablas permitidas.
- No hay validación de parámetros en where_clause.
- No hay pruebas unitarias incluidas.
- Logging puede exponer información sensible.

**Riesgos:**
- Si where_clause o params no se validan, puede haber inyección.
- Logging excesivo puede exponer datos sensibles.

**Recomendaciones:**
- Validar y parametrizar where_clause y params.
- Añadir pruebas unitarias.
- Limitar información sensible en logs.
- Documentar limitaciones.

**Cumplimiento:**
- MITRE CWE: Parcial (CWE-89, CWE-117)
- OWASP: Parcial (A1:2017-Inyección, A6:2017-Logging)
- MIT Secure Coding: Parcial

---

## two_factor_auth.py

**Resumen:**
Implementa autenticación de dos factores (2FA) usando TOTP (RFC 6238), generación de claves, QR y validación de códigos.

**Hallazgos:**
- Implementación robusta de TOTP y generación de QR.
- Uso de librerías estándar y seguras (secrets, hmac, hashlib).
- No hay logging de intentos fallidos o exitosos.
- No hay protección contra ataques de fuerza bruta (rate limiting).
- No hay pruebas unitarias incluidas.
- No hay internacionalización.

**Riesgos:**
- Sin rate limiting, posible ataque de fuerza bruta.
- Sin logging, difícil auditoría de accesos.
- Sin pruebas, difícil garantizar robustez.

**Recomendaciones:**
- Añadir logging de intentos y rate limiting.
- Añadir pruebas unitarias.
- Documentar dependencias y limitaciones.

**Cumplimiento:**
- MITRE CWE: Parcial (CWE-307, CWE-778)
- OWASP: Parcial (A2:2017-Auth, A7:2017-Logging)
- MIT Secure Coding: Parcial

---

## keyboard_navigation.py

**Resumen:**
Sistema completo de navegación por teclado para PyQt6. Incluye gestión de atajos estándar, orden de tabulación, navegación en tablas, integración con accesibilidad y utilidades para configurar navegación y atajos CRUD en widgets.

**Hallazgos:**
- El sistema cubre la mayoría de los casos de navegación y accesibilidad requeridos en aplicaciones empresariales.
- El diseño es modular y permite integración y extensión sencilla.
- No hay logging de acciones del usuario (navegación, uso de atajos, errores, etc.).
- No hay validación ni sanitización de los atajos o acciones registradas (riesgo bajo, pero relevante si hay entrada de usuario).
- No hay soporte para internacionalización (i18n) en los textos predeterminados.
- No hay control de acceso: cualquier parte de la app puede registrar atajos y acciones.
- No hay protección contra uso en entornos sin GUI (puede fallar si no hay QApplication activa).
- El sistema depende de la correcta estructura de los widgets y layouts para aplicar navegación y accesibilidad.
- La integración con lectores de pantalla es solo un stub (print), no implementa APIs reales.

**Riesgos:**
- Si se usan atajos o acciones no validadas, pueden aparecer resultados inesperados o inconsistentes.
- No hay registro de uso para auditoría o debugging.
- Si se usa en scripts sin entorno gráfico, puede lanzar excepciones no controladas.
- Si la estructura del widget/layout no es la esperada, la navegación puede no funcionar correctamente.

**Recomendaciones:**
- Añadir logging opcional de acciones del usuario (navegación, uso de atajos, errores).
- Añadir validación/sanitización de los atajos y acciones si hay entrada externa.
- Considerar soporte para internacionalización en los textos predeterminados.
- Documentar la necesidad de entorno gráfico para su uso.
- Documentar las dependencias de estructura de widgets y layouts.
- Implementar integración real con APIs de accesibilidad si es necesario.

**Cumplimiento:**
- MITRE CWE: Parcial (CWE-20, CWE-200, CWE-778 si se usan datos no validados)
- OWASP: Parcial (A10:2017-Insufficient Logging & Monitoring)
- MIT Secure Coding: Parcial (validación y manejo de errores mejorables)

---

## __init__.py

**Resumen:**
Archivo de inicialización vacío para el módulo utils.

**Hallazgos:**
- No contiene lógica ni riesgos.

**Riesgos:**
- Ninguno.

**Recomendaciones:**
- Ninguna.

**Cumplimiento:**
- N/A

---

# Auditoría de dependencias: requirements.txt (08/08/2025)

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
