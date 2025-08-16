# Rexus.app — breve guía

Este repositorio contiene la aplicación Rexus.app.

- Documentación de referencia: `CLAUDE.md` (fuente única de verdad).
- Documentación de desarrollo: `project_scripts/README-DEV.md` y `README-DEV.md`.
- Arranque rápido: `python main.py` (ver `project_scripts/` para comandos Docker/Makefile).

Estructura principal:

- `main.py` — punto de entrada de la aplicación.
- `rexus/` — código principal (modules, core, ui, utils).
- `project_scripts/` — scripts y tooling para desarrollo y despliegue.
- `legacy_root/` — backups y archivos históricos (no tocar salvo necesidad).
# Rexus.app - resumen rápido

Este repositorio contiene la aplicación Rexus.app.

- Documentación principal y reglas de organización: `CLAUDE.md`
- Guía de desarrollo y comandos: `project_scripts/README-DEV.md` (ver `project_scripts/`)

Archivos importantes en la raíz:
- `main.py` — punto de entrada
- `requirements.txt` — dependencias
- `CLAUDE.md` — guía y reglas del proyecto

Para desarrollo local:
1. Copiar `.env.example` a `.env` y completar variables.
2. Crear un entorno virtual e instalar dependencias:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3. Ejecutar en modo desarrollo:

```powershell
python main.py
```
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
