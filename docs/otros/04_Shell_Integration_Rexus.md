# Integración de Shell y Automatización en Rexus.app

## Terminal integrada (PowerShell)

Puedes ejecutar comandos y scripts útiles desde la terminal de VS Code (PowerShell):

### Ejemplos útiles

- **Ejecutar todos los tests:**
  ```powershell
  python -m unittest discover -s tests
  ```
- **Ejecutar la app principal:**
  ```powershell
  python main.py
  ```
- **Backup de la base de datos:**
  ```powershell
  python scripts/backup_db.py
  ```
- **Restaurar backup:**
  ```powershell
  python scripts/restore_db.py
  ```
- **Migraciones SQL:**
  ```powershell
  python scripts/migrar_sql.py
  ```

## Tareas automatizadas en VS Code

Ya tienes una tarea configurada para correr todos los tests desde el menú de tareas:

- Abre la paleta de comandos (Ctrl+Shift+P) y busca `Tareas: Ejecutar tarea`.
- Selecciona **Run All Tests** para ejecutar todos los tests automáticamente.

Puedes agregar más tareas en `.vscode/tasks.json` para otros scripts frecuentes.

---

**Tip:** Si necesitas agregar más scripts, solo crea el archivo en `scripts/` y agrégalo como tarea en VS Code.

---

Actualizado: 2025-08-07
