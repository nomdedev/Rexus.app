# Organización de archivos en la raíz de Rexus.app

- CLAUDE.md: Mantener siempre en raíz (referencia de arquitectura/contexto)
- checklist_pendientes.md: Único checklist vivo, mantener en raíz
- main.py: Script principal de la app
- .env, .env.docker, .gitignore, requirements.txt, Dockerfile, docker-compose.yml, Makefile, sonar-project.properties: Infraestructura/configuración
- docs/: Documentación general y legacy
- reports/: Reportes de auditoría, UI, módulos, contrastes, etc.
- scripts/dev/: Scripts de arranque y desarrollo
- tests/: Pruebas unitarias y de integración
- rexus/, config/, data/, logs/, project_scripts/, scripts/, ui/, uploads/, utils/, backups/: Código, datos y utilidades

## Archivos eliminados o movidos
- checklist_reorganizado.md, checklist_uiux_botones.md, pendientes.md: Eliminados por duplicidad o estar vacíos
- DEVELOPMENT_GUIDE.md, SISTEMA_COMPLETADO.md: Movidos a docs/
- DASHBOARD_MODERNIZATION_REPORT.md, modules_audit_report.txt, OBRAS_UI_COMPLETION_REPORT.md, contrast_report.txt: Movidos a reports/
- start-dev.bat, start-dev.sh, dev-server.py: Movidos a scripts/dev/

