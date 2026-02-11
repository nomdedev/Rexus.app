# Configuraciones - Rexus.app

**Fecha de actualizacion:** 2025-02-10
**Version:** 2.0.0

---

## Resumen Ejecutivo

Este documento consolida todas las configuraciones del proyecto, incluyendo variables de entorno seguras, configuraciones de herramientas de analisis de codigo y configuraciones de desarrollo.

---

## 1. Configuracion Segura

### Variables de Entorno Requeridas

Para una configuracion segura, configure las siguientes variables de entorno:

#### Base de Datos
```bash
export REXUS_DB_SERVER="tu_servidor_db"
export REXUS_DB_PORT="1433"
export REXUS_DB_NAME="rexus_db"
export REXUS_DB_USER="tu_usuario_db"
export REXUS_DB_PASSWORD="tu_password_seguro"
```

#### Email (para notificaciones)
```bash
export REXUS_EMAIL_SMTP_SERVER="smtp.gmail.com"
export REXUS_EMAIL_SMTP_PORT="587"
export REXUS_EMAIL_USER="tu_email@gmail.com"
export REXUS_EMAIL_PASSWORD="tu_password_app"
export REXUS_EMAIL_SSL="true"
```

#### Sistema
```bash
export REXUS_DEBUG="false"
export REXUS_LOG_LEVEL="INFO"
```

### Configuracion del Archivo

1. Copie `config/rexus_config.example.json` a `config/rexus_config.json`
2. Configure los valores basicos (no confidenciales) en el archivo JSON
3. Las credenciales sensibles deben configurarse unicamente via variables de entorno

### Archivo .env (Opcional)

Para desarrollo local, puede crear un archivo `.env`:

```bash
cp .env.example .env
# Edite .env con sus valores reales
```

**IMPORTANTE:** Nunca commitee el archivo `.env` al repositorio. Asegurese de que este en `.gitignore`.

### Verificacion

Ejecute el script de configuracion para verificar:

```bash
python -c "from rexus.utils.secure_config import get_config; c = get_config(); print('✅ Configuracion OK' if not c.validate_required(['database.server', 'database.user', 'database.password']) else '❌ Configuracion incompleta')"
```

### Seguridad

- ✅ Credenciales en variables de entorno (nunca en codigo)
- ✅ Archivo de configuracion separado de credenciales
- ✅ Validacion de configuracion requerida
- ✅ Logging de configuracion cargada (sin mostrar passwords)
- ✅ Soporte para diferentes entornos (desarrollo, produccion)

---

## 2. Configuracion de Analisis de Codigo

Este documento explica como configurar las herramientas de analisis de codigo para excluir archivos y directorios que no necesitan ser analizados.

### Herramientas Configuradas

#### 1. Bandit (Analisis de Seguridad)
- **Archivo**: `.bandit`
- **Excluye**: tests, scripts, examples, backups, reports, cache, logs
- **Skips**: B101 (asserts), B601 (shell usage en tests)

#### 2. Pylance/Pyright (Analisis de Tipos)
- **Archivos**: `pyrightconfig.json`, `.vscode/settings.json`
- **Excluye**: tests, scripts, examples, backups, reports, cache, logs
- **Modo**: type checking basico

#### 3. SonarQube (Analisis de Calidad)
- **Archivo**: `sonar-project.properties`
- **Excluye**: tests, scripts, examples, backups, reports, cache, logs
- **Fuentes**: solo `rexus/` y `main.py`

#### 4. Pylint (Linting)
- **Archivo**: `.pylintrc`
- **Excluye**: tests, scripts, examples, backups, reports, cache, logs
- **Reglas**: configuradas para Python moderno

#### 5. Flake8 (Linting)
- **Archivo**: `.flake8`
- **Excluye**: tests, scripts, examples, backups, reports, cache, logs
- **Limites**: linea maxima 100 caracteres

#### 6. MyPy (Type Checking)
- **Archivo**: `.mypy.ini`
- **Excluye**: tests, scripts, examples, backups, reports, cache, logs
- **Modo**: estricto pero practico

#### 7. Pre-commit Hooks
- **Archivo**: `.pre-commit-config.yaml`
- **Herramientas**: black, isort, flake8, bandit
- **Excluye**: mismas carpetas que otras herramientas

### Directorios Excluidos

Los siguientes directorios estan excluidos del analisis:

- `tests/` - Archivos de pruebas unitarias
- `scripts/` - Scripts de uso unico o utilitarios
- `examples/` - Ejemplos y codigo de demostracion
- `backups/` - Archivos de respaldo
- `reports/` - Reportes generados automaticamente
- `.pytest_cache/` - Cache de pytest
- `__pycache__/` - Cache de Python
- `rexus_app.egg-info/` - Metadata del paquete
- `.git/` - Control de versiones
- `.vscode/` - Configuracion del IDE
- `logs/` - Archivos de log
- `cache/` - Archivos de cache
- `.claude/` - Configuracion de Claude
- `sql/` - Scripts SQL
- `resources/` - Recursos estaticos
- `config/` - Archivos de configuracion
- `docs/` - Documentacion

### Como Usar

1. **VSCode**: Las configuraciones se aplican automaticamente
2. **Bandit**: `bandit -r .` (respeta `.bandit`)
3. **SonarQube**: Subir proyecto con configuraciones aplicadas
4. **Pre-commit**: `pre-commit install` para activar hooks

### Beneficios

- ✅ Analisis mas rapido y eficiente
- ✅ Menos falsos positivos
- ✅ Enfoque en codigo de produccion
- ✅ Mejor experiencia de desarrollo
- ✅ Configuracion consistente entre herramientas

---

## 3. Configuracion de Desarrollo

### Python Moderna

**Archivos:**
- `pyproject.toml` (300 lineas) - Configuracion moderna
- `setup.cfg` - Configuracion heredada
- `.pre-commit-config.yaml` - Git hooks

**Herramientas:** Black, Flake8, Pylint, MyPy, Bandit, Safety

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        exclude: ^(tests/|scripts/)

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        exclude: ^(tests/|scripts/)

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        exclude: ^tests/
```

### Instalacion

```bash
# Instalar pre-commit
pip install pre-commit

# Instalar hooks
pre-commit install

# Ejecutar manualmente
pre-commit run --all-files
```

---

## 4. Configuracion de Tests

### pytest.ini

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
addopts = -v --tb=short --cov=rexus
```

### Estructura de Tests

```
tests/
├── unit/          # Pruebas unitarias
├── integration/   # Pruebas de integracion
├── ui/           # Pruebas de interfaz
├── e2e/          # Pruebas end-to-end
└── conftest.py   # Configuracion
```

### Ejecucion de Tests

```bash
# Suite completa
python -m pytest tests/ -v

# Por categorias
python -m pytest -m unit         # Tests unitarios
python -m pytest -m integration  # Tests de integracion
python -m pytest -m security     # Tests de seguridad

# Con cobertura
python -m pytest tests/ --cov=rexus --cov-report=html
```

---

## 5. Configuracion Docker

### Dockerfile

```dockerfile
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get install -y build-essential libgl1 libegl1...
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

### docker-compose.yml

```yaml
version: '3.8'
services:
  rexus:
    build: .
    volumes: [".:/app"]
    environment:
      - PYTHONUNBUFFERED=1
    command: ["python", "main.py"]
```

### docker-compose.dev.yml

```yaml
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - ./docker/redis/redis.conf:/usr/local/etc/redis/redis.conf

  redis-commander:
    image: rediscommander/redis-commander:latest
    ports:
      - "8081:8081"
    environment:
      - REDIS_HOSTS=local:redis:6379
```

---

## 6. Configuracion de Cache (Redis)

### Configuracion

```env
CACHE_TYPE=memory
CACHE_DEFAULT_TIMEOUT=3600
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

### Redis Config

```conf
# docker/redis/redis.conf
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

---

## Documentacion Relacionada

- [ESTADO_PROYECTO.md](ESTADO_PROYECTO.md) - Estado actual del proyecto
- [MEJORAS_PENDIENTES.md](MEJORAS_PENDIENTES.md) - Lista de mejoras
- [CACHING_QUICKSTART.md](CACHING_QUICKSTART.md) - Guia de implementacion de cache
- [CI_CD_SETUP.md](CI_CD_SETUP.md) - Configuracion CI/CD

---

**Fecha de actualizacion:** 2025-02-10
