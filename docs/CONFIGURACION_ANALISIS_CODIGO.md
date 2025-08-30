# Configuración de Análisis de Código

Este documento explica cómo configurar las herramientas de análisis de código para excluir archivos y directorios que no necesitan ser analizados.

## Herramientas Configuradas

### 1. Bandit (Análisis de Seguridad)
- **Archivo**: `.bandit`
- **Excluye**: tests, scripts, examples, backups, reports, cache, logs
- **Skips**: B101 (asserts), B601 (shell usage en tests)

### 2. Pylance/Pyright (Análisis de Tipos)
- **Archivos**: `pyrightconfig.json`, `.vscode/settings.json`
- **Excluye**: tests, scripts, examples, backups, reports, cache, logs
- **Modo**: type checking básico

### 3. SonarQube (Análisis de Calidad)
- **Archivo**: `sonar-project.properties`
- **Excluye**: tests, scripts, examples, backups, reports, cache, logs
- **Fuentes**: solo `rexus/` y `main.py`

### 4. Pylint (Linting)
- **Archivo**: `.pylintrc`
- **Excluye**: tests, scripts, examples, backups, reports, cache, logs
- **Reglas**: configuradas para Python moderno

### 5. Flake8 (Linting)
- **Archivo**: `.flake8`
- **Excluye**: tests, scripts, examples, backups, reports, cache, logs
- **Límites**: línea máxima 100 caracteres

### 6. MyPy (Type Checking)
- **Archivo**: `.mypy.ini`
- **Excluye**: tests, scripts, examples, backups, reports, cache, logs
- **Modo**: estricto pero práctico

### 7. Pre-commit Hooks
- **Archivo**: `.pre-commit-config.yaml`
- **Herramientas**: black, isort, flake8, bandit
- **Excluye**: mismas carpetas que otras herramientas

## Directorios Excluidos

Los siguientes directorios están excluidos del análisis:

- `tests/` - Archivos de pruebas unitarias
- `scripts/` - Scripts de uso único o utilitarios
- `examples/` - Ejemplos y código de demostración
- `backups/` - Archivos de respaldo
- `reports/` - Reportes generados automáticamente
- `.pytest_cache/` - Cache de pytest
- `__pycache__/` - Cache de Python
- `rexus_app.egg-info/` - Metadata del paquete
- `.git/` - Control de versiones
- `.vscode/` - Configuración del IDE
- `logs/` - Archivos de log
- `cache/` - Archivos de cache
- `.claude/` - Configuración de Claude
- `sql/` - Scripts SQL
- `resources/` - Recursos estáticos
- `config/` - Archivos de configuración
- `docs/` - Documentación

## Cómo Usar

1. **VSCode**: Las configuraciones se aplican automáticamente
2. **Bandit**: `bandit -r .` (respeta `.bandit`)
3. **SonarQube**: Subir proyecto con configuraciones aplicadas
4. **Pre-commit**: `pre-commit install` para activar hooks

## Beneficios

- ✅ Análisis más rápido y eficiente
- ✅ Menos falsos positivos
- ✅ Enfoque en código de producción
- ✅ Mejor experiencia de desarrollo
- ✅ Configuración consistente entre herramientas
