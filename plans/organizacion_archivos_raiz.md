# Plan de Organización de Archivos en la Raíz del Proyecto Rexus.app

## Archivos en la Raíz que Necesitan Organización

### 1. Archivos de Pruebas y Testing
**Destino:** `tests/`

- `check_dependencies.py` → `tests/utils/check_dependencies.py`
- `check_missing_deps.py` → `tests/utils/check_missing_deps.py`
- `simple_test.py` → `tests/simple_test.py`
- `test_corrections.py` → `tests/utils/test_corrections.py`
- `test_module_imports.py` → `tests/utils/test_module_imports.py`

### 2. Scripts de Mantenimiento y Corrección
**Destino:** `scripts/maintenance/` (crear subdirectorio si no existe)

- `final_syntax_fix.py` → `scripts/maintenance/final_syntax_fix.py`
- `fix_all_syntax_errors.py` → `scripts/maintenance/fix_all_syntax_errors.py`
- `fix_critical_syntax_errors.py` → `scripts/maintenance/fix_critical_syntax_errors.py`
- `fix_encoding_issues.py` → `scripts/maintenance/fix_encoding_issues.py`
- `fix_fstrings_massive.py` → `scripts/maintenance/fix_fstrings_massive.py`
- `fix_fstrings.py` → `scripts/maintenance/fix_fstrings.py`
- `fix_usuarios_controller_complete.py` → `scripts/maintenance/fix_usuarios_controller_complete.py`
- `fix_usuarios_controller_syntax.py` → `scripts/maintenance/fix_usuarios_controller_syntax.py`

### 3. Archivos Temporales
**Destino:** `temp/` (crear directorio si no existe)

- `pytest_temp.ini` → `temp/pytest_temp.ini`
- `temp_line.txt` → `temp/temp_line.txt`

### 4. Configuraciones de Docker
**Destino:** `docker/`

- `docker-compose.dev.yml` → `docker/docker-compose.dev.yml`
- `docker-compose.monitoring.yml` → `docker/docker-compose.monitoring.yml`
- `Dockerfile` → `docker/Dockerfile`

### 5. Documentación
**Destino:** `docs/`

- `AUDITORIA_FINAL_REPORTE.md` → `docs/auditoria/AUDITORIA_FINAL_REPORTE.md`

### 6. Herramientas de Desarrollo
**Destino:** `tools/`

- `.pre-commit-config.yaml` → (permanece en la raíz, versión más completa)

## Archivos que Deben Permanecer en la Raíz

Estos archivos son estándar y deben permanecer en la raíz del proyecto:

- `.env` - Variables de entorno
- `.gitignore` - Configuración de git
- `main.py` - Punto de entrada principal
- `pyproject.toml` - Configuración del proyecto
- `requirements-dev.txt` - Dependencias de desarrollo
- `requirements.txt` - Dependencias de producción
- `setup.cfg` - Configuración de setup

## Directorios Ocultos que Deben Permanecer

- `.claude/` - Configuración específica de Claude
- `.github/` - Configuración de GitHub
- `.pytest_cache/` - Caché de pytest
- `.venv/` - Entorno virtual
- `.vscode/` - Configuración de VS Code

## Directorios que Deben Permanecer

- `Back-up.rexus-sql/` - Copias de seguridad de SQL
- `backups/` - Copias de seguridad
- `cache/` - Caché de la aplicación
- `config/` - Configuraciones
- `docker/` - Configuraciones Docker
- `docs/` - Documentación
- `examples/` - Ejemplos
- `logs/` - Logs de la aplicación
- `monitoring/` - Monitoreo
- `plans/` - Planes (directorio creado)
- `reports/` - Reportes
- `resources/` - Recursos
- `rexus/` - Código principal
- `rexus_app.egg-info/` - Información del paquete
- `scripts/` - Scripts
- `sql/` - Scripts SQL
- `tests/` - Pruebas
- `tools/` - Herramientas

## Acciones Requeridas

### 1. Crear Directorios Necesarios
```bash
mkdir -p scripts/maintenance
mkdir -p temp
mkdir -p docs/auditoria
```

### 2. Mover Archivos
```bash
# Archivos de pruebas
mv check_dependencies.py tests/utils/
mv check_missing_deps.py tests/utils/
mv simple_test.py tests/
mv test_corrections.py tests/utils/
mv test_module_imports.py tests/utils/

# Scripts de mantenimiento
mkdir -p scripts/maintenance
mv final_syntax_fix.py scripts/maintenance/
mv fix_all_syntax_errors.py scripts/maintenance/
mv fix_critical_syntax_errors.py scripts/maintenance/
mv fix_encoding_issues.py scripts/maintenance/
mv fix_fstrings_massive.py scripts/maintenance/
mv fix_fstrings.py scripts/maintenance/
mv fix_usuarios_controller_complete.py scripts/maintenance/
mv fix_usuarios_controller_syntax.py scripts/maintenance/

# Archivos temporales
mkdir -p temp
mv pytest_temp.ini temp/
mv temp_line.txt temp/

# Configuraciones Docker
mv docker-compose.dev.yml docker/
mv docker-compose.monitoring.yml docker/
mv Dockerfile docker/

# Documentación
mkdir -p docs/auditoria
mv AUDITORIA_FINAL_REPORTE.md docs/auditoria/

# Herramientas
mv .pre-commit-config.yaml tools/
```

### 3. Actualizar Referencias
Después de mover los archivos, será necesario actualizar las referencias en:
- Scripts de CI/CD
- Documentación
- Archivos de configuración
- Importaciones en el código

## Beneficios de esta Organización

1. **Raíz más limpia**: Menos desorden en el directorio principal
2. **Archivos agrupados por propósito**: Cada tipo de archivo está en su lugar correspondiente
3. **Mantenimiento más fácil**: Es más fácil encontrar y actualizar archivos específicos
4. **Estructura estándar**: Sigue las convenciones de proyectos Python
5. **Mejor navegación**: Los desarrolladores pueden encontrar archivos más fácilmente

## Verificación Post-Migración

Después de mover los archivos, verificar:
1. Que todas las pruebas aún funcionen
2. Que los scripts de mantenimiento aún funcionen
3. Que las configuraciones Docker aún funcionen
4. Que no haya referencias rotas en el código
5. Que la documentación esté actualizada