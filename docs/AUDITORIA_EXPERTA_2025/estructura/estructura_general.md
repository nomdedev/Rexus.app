# Auditoría de Estructura General - Rexus.app (2025)

## 1. Raíz del Proyecto

- .env, .gitignore, requirements.txt, Dockerfile, docker-compose.yml, Makefile, sonar-project.properties: **Infraestructura/configuración**
- main.py: **Script principal de la app**
- CLAUDE.md: **Documentación central de arquitectura/contexto**
- checklist_pendientes.md: **Checklist único y vigente**
- start-dev.bat, start-dev.sh, dev-server.py: **Scripts de arranque/desarrollo**
- contrast_report.txt, modules_audit_report.txt: **Reportes técnicos**
- expert_audit.py, cleanup_duplicates.py: **Scripts utilitarios/auditoría**

## 2. Carpetas principales

- rexus/: **Código fuente principal (MVC, módulos, UI, lógica de negocio)**
- config/: **Configuraciones y utilidades globales**
- data/: **Datos de ejemplo, fixtures, migraciones**
- docs/: **Documentación general y legacy**
- legacy_root/: **(Eliminada/Migrada) - Ya no existe código legacy en producción**
- logs/: **Logs de ejecución y auditoría**
- project_scripts/: **Scripts de mantenimiento y automatización**
- reports/: **Reportes de auditoría, UI, módulos, contrastes, etc.**
- scripts/: **Scripts utilitarios y de desarrollo**
- tests/: **Pruebas unitarias y de integración**
- ui/: **Recursos de interfaz gráfica (QSS, imágenes, layouts)**
- uploads/: **Archivos subidos por usuarios o procesos**
- utils/: **Utilidades y helpers globales**
- backups/: **Backups automáticos y manuales**

## 3. Observaciones

- Estructura general es clara y modular, con separación adecuada entre código, datos, documentación y utilidades.
- Las carpetas legacy han sido eliminadas o migradas. Scripts utilitarios revisados y depurados.
- No se detectan archivos huérfanos críticos en la raíz.
- CLAUDE.md y Checklist pendientes.md están actualizados y son la fuente de verdad para arquitectura y auditoría.

---

**Siguiente paso:** Auditoría de módulos principales (uno por uno en /modulos) y barrido de errores globales.
