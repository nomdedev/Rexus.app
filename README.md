# Rexus.app (breve)

Este repositorio contiene la aplicación Rexus.app.

- Documentación y reglas de proyecto completas en `CLAUDE.md` (raíz).
- Guía de desarrollo y scripts en `project_scripts/` y `README-DEV.md`.

Para iniciar en desarrollo:

1. Copiar `.env.example` a `.env` y completar variables.
2. Crear un entorno virtual e instalar dependencias:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3. Ejecutar la app (modo desarrollo):

```powershell
python main.py
```
