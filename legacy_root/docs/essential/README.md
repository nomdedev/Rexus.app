# Índice de documentación y estándares

## 📚 Guía de uso de bases de datos

**¡IMPORTANTE!**
Lee y respeta la guía de uso de bases de datos y tablas:

- [docs/USO_BASES_DE_DATOS.md](USO_BASES_DE_DATOS.md)

---

Este índice centraliza el acceso a todos los documentos clave del proyecto. Consulta cada estándar antes de modificar o agregar código.

## Estándares y guías
- [Estándares visuales](estandares_visuales.md)
- [Estándares de logging y feedback visual](estandares_logging.md)
- [Formato y rotación de logs (JSON y texto)](estandares_logging.md#formato-json-y-rotacion)
- [Estándares de seguridad y manejo de datos sensibles](estandares_seguridad.md)
- [Estándares de feedback visual y procedimientos de carga](estandares_feedback.md)
- [Estándares de auditoría y registro de acciones](estandares_auditoria.md)
- [Checklist unificado de mejoras UI/UX y accesibilidad](checklists/checklist_unificado_mejoras_uiux.md)
- [Checklist de mejoras UI/UX por módulo](checklists/checklist_mejoras_uiux_por_modulo.md)

## Flujos y buenas prácticas
- [Flujo de integración Obras/Material/Vidrios](flujo_obras_material_vidrios.md)
- [Buenas prácticas en configuraciones críticas](buenas_practicas_configuraciones_criticas.md)
- [Errores frecuentes en login y soluciones](errores_frecuentes_login.md)
- [Decisiones de diseño en main.py](decisiones_main.md)
- [Pendientes de tests y controladores](pendientes_tests_y_controladores.md)
- [Bloqueo de tests UI y motivos](bloqueo_tests_ui.md)

## Auditoría y reportes
- [Auditoría y reportes](auditoria/README.md)

## Organización de recursos y estructura del proyecto

- **QSS:** Todos los archivos de estilos están en `resources/qss/`.
- **Íconos:** Todos los íconos SVG y PNG están en `resources/icons/`.
- **Scripts de base de datos:** Centralizados en `scripts/db/`.
- **PDFs y Excels de auditoría:** En `docs/auditoria/`.
- **Estructura de tablas por módulo:** [Estructura de tablas](estructura_tablas_por_modulo.md).
- **Tests:** Subcarpetas por módulo en `tests/` y datos de prueba en `tests/fixtures/`.

Consulta el README principal para detalles y convenciones de cada carpeta.

---

## Conexión robusta a base de datos: timeout y reintentos

La conexión a la base de datos implementa:
- **Timeout configurable:** El tiempo máximo de espera para conectar se define por variable de entorno (`DB_TIMEOUT`) o parámetro.
- **Reintentos automáticos:** Si la conexión falla, se reintenta hasta `DB_MAX_RETRIES` veces (por defecto 3), con backoff exponencial.
- **Logging detallado:** Cada intento y error se registra en los logs para trazabilidad y diagnóstico.

**Justificación:**
- Mejora la resiliencia ante caídas temporales de red o base de datos.
- Evita fallos inmediatos por problemas transitorios.
- Permite ajustar el comportamiento según el entorno (desarrollo, producción, CI).
- Facilita el monitoreo y la auditoría de problemas de conectividad.

**Convención:** Usa siempre la clase `BaseDatabaseConnection` o sus derivadas para aprovechar este mecanismo. No implementes reintentos manuales en los módulos.

---

## 🤝 Guía rápida para colaboradores y desarrolladores

### ¿Por dónde empezar?
- El punto de entrada principal es `run.py`. Ejecuta `python run.py` para iniciar la app.
- Si la app principal no está disponible, el script puede adaptarse para lanzar el modo demo (`demo_app.py`), que permite probar la interfaz y módulos sin base de datos.
- El archivo `demo_app.py` muestra todos los módulos y funcionalidades usando datos mock y emojis, ideal para testing visual y onboarding.

### Estructura y convenciones clave
- **Estándares visuales:** El proyecto usa emojis para feedback, botones y navegación en vez de íconos SVG/PNG. Consulta `docs/estandares_visuales.md` para ver el estándar actual y casos especiales.
- **Variables de entorno:** `run.py` configura automáticamente variables críticas si no existen. Puedes personalizarlas en tu entorno local.
- **Modularidad:** Cada módulo (Inventario, Obras, Contabilidad, etc.) tiene su propia carpeta y checklist de verificación en `docs/checklists/`.
- **Accesibilidad y feedback:** Todos los botones y acciones deben tener tooltips, feedback visual claro y accesible. Revisa los checklists y los estándares antes de modificar la UI.

### ¿Cómo ayudar?
- Lee los estándares y checklists antes de proponer cambios.
- Si agregas un nuevo módulo, funcionalidad o flujo, documenta y enlaza en este README.
- Si encuentras un bug, mejora o excepción visual, documenta en el archivo correspondiente y en el checklist del módulo.
- Usa el modo demo para validar cambios visuales y de UX antes de integrarlos a la app principal.

### Recursos útiles
- [Estándares visuales y uso de emojis](estandares_visuales.md)
- [Modo demo y testing visual](../demo_app.py)
- [Checklist de mejoras UI/UX por módulo](checklists/checklist_mejoras_uiux_por_modulo.md)
- [Checklist general de estado y pendientes](CHECKLIST_ESTADO_PROYECTO.md)

---

## **Convención:** Si agregas un nuevo estándar, guía o flujo, enlázalo aquí y describe brevemente su propósito.

## **Actualización:**
- [14/06/2025] Documentación y checklists actualizados tras la unificación visual, accesibilidad y feedback en Mantenimiento, Configuración, Contabilidad y Notificaciones. Todos los ítems marcados como completos en los checklists correspondientes.

Última actualización: 14 de junio de 2025
