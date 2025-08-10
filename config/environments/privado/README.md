# Política de confidencialidad para archivos sensibles

Esta carpeta (`config/privado/`) contiene archivos de configuración y tests que incluyen credenciales, variables de entorno o información sensible.

- **Nunca subas estos archivos al repositorio.**
- El archivo `.env` debe ser gestionado solo localmente y compartido de forma segura.
- Los tests que requieran datos reales o credenciales deben ubicarse aquí y estar excluidos del control de versiones.

Para más información, consulta `docs/ESTANDARES_Y_CHECKLISTS.md` y `docs/buenas_practicas_configuraciones_criticas.md`.
