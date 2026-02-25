# 👨‍💻 Guía de Desarrollo - Rexus.app v2.0.0

Guía completa para desarrolladores que contribuyen al proyecto Rexus.app.

## 📋 Índice

- [Instalación](#instalación)
- [Configuración de Entorno](#configuración-de-entorno)
- [Testing](#testing)
- [Calidad de Código](#calidad-de-código)
- [CI/CD Pipeline](#cicd-pipeline)
- [Git Workflow](#git-workflow)
- [Troubleshooting](#troubleshooting)

---

## 🚀 Instalación

### Requisitos Previos

- Python 3.10 o superior
- Git
- Docker Desktop (opcional, para contenedores)

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/rexus/app.git
cd rexus/app
```

### Paso 2: Crear Entorno Virtual

```bash
# Crear entorno virtual
python -m venv .venv

# Activar (Windows)
.venv\Scripts\activate

# Activar (Linux/Mac)
source .venv/bin/activate
```

### Paso 3: Instalar Dependencias

```bash
# Dependencias de producción
pip install -r requirements.txt

# Dependencias de desarrollo
pip install -r requirements-dev.txt

# Configurar pre-commit hooks
python scripts/dev.py setup
```

### Paso 4: Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar con tus credenciales
# ⚠️ NUNCA commits .env al repositorio
```

---

## 🔧 Configuración de Entorno

### Archivos de Configuración

- **`.env`**: Variables de entorno (NO commitear este archivo)
- **`pyproject.toml`**: Configuración de herramientas Python
- **`setup.cfg`**: Configuración adicional de herramientas
- **`.pre-commit-config.yaml`**: Git hooks automatizados

### Pre-commit Hooks

Los pre-commit hooks se ejecutan automáticamente antes de cada commit:

```bash
# Se ejecutan automáticamente al hacer git commit
git commit -m "mensaje"

# O ejecutar manualmente en todos los archivos
pre-commit run --all-files
```

Hooks configurados:
- ✅ Black (formateo)
- ✅ isort (imports)
- ✅ Flake8 (linting)
- ✅ MyPy (tipos)
- ✅ Bandit (seguridad)
- ✅ Detect-secrets (credenciales)

---

## 🧪 Testing

### Ejecutar Todos los Tests

```bash
# Ejecutar suite completa
pytest

# Con cobertura
pytest --cov=rexus --cov-report=html

# Paralelizado (más rápido)
pytest -n auto
```

### Tests Específicos

```bash
# Solo tests unitarios
pytest tests/unit/

# Solo tests de seguridad
pytest tests/security/

# Tests específicos
pytest tests/security/test_rate_limiter.py

# Tests con marca específica
pytest -m "not slow"  # Excluir tests lentos
pytest -m "security"  # Solo tests de seguridad
```

### Debuggear Tests

```bash
# Con pdb (debugger)
pytest --pdb

# Con ipdb (mejor debugger)
pytest --pdbcls=IPython.terminal.debugger:TerminalPdb

# Solo en fallos
pytest --pdb -x
```

### Cobertura de Código

```bash
# Generar reporte HTML
pytest --cov=rexus --cov-report=html

# Abrir reporte
# Windows: start htmlcov/index.html
# Linux/Mac: open htmlcov/index.html

# Ver en terminal
pytest --cov=rexus --cov-report=term-missing
```

---

## 📏 Calidad de Código

### Formatear Código

```bash
# Formatear automáticamente
python scripts/dev.py format --fix

# Verificar sin modificar
python scripts/dev.py format
```

### Linting

```bash
# Ejecutar todos los linters
python scripts/dev.py lint

# Individualmente
black rexus/ tests/           # Formateador
isort rexus/ tests/           # Imports
flake8 rexus/ tests/          # PEP 8
pylint rexus/                 # Análisis profundo
mypy rexus/                   # Type checking
bandit -r rexus/              # Security
```

### Ejecutar Todo

```bash
# Pipeline completo (format + lint + test + security)
python scripts/dev.py all

# Con corrección automática
python scripts/dev.py all --fix
```

---

## 🚀 CI/CD Pipeline

El pipeline de CI/CD se ejecuta automáticamente en GitHub Actions:

### Triggers

- Push a `main` o `develop`
- Pull Request a `main`
- Ejecución manual (workflow_dispatch)

### Jobs

1. **lint-style** - Formato y estilo
2. **lint-quality** - Calidad de código
3. **test-unit** - Tests unitarios
4. **test-integration** - Tests de integración
5. **security-scan** - Análisis de seguridad
6. **build** - Build Docker image
7. **deploy-staging** - Deploy a staging
8. **deploy-production** - Deploy a producción (manual)

### Verificar Status Localmente

```bash
# Ejecutar el mismo pipeline que CI
python scripts/dev.py all
```

---

## 🌿 Git Workflow

### Branches

- `main` - Producción
- `develop` - Desarrollo
- `feature/nombre-feature` - Nuevas features
- `bugfix/nombre-bug` - Corrección de bugs
- `hotfix/nombre-hotfix` - Fixes urgentes en producción

### Commits

```bash
# Feature branch
git checkout develop
git checkout -b feature/nueva-funcionalidad

# Trabajar...
git add .
git commit -m "feat: agregar nueva funcionalidad"

# Push
git push origin feature/nueva-funcionalidad
```

### Mensajes de Commit

Usar **Conventional Commits**:

```
feat: agregar nueva funcionalidad X
fix: corregir error Y en módulo Z
docs: actualizar README con instrucciones
style: formatear código con black
refactor: reorganizar estructura del módulo
test: agregar tests para RateLimiter
chore: actualizar dependencias
```

### Pull Requests

1. Crear PR desde feature branch a `develop`
2. CI/CD se ejecuta automáticamente
3. Revisar cambios
4. Solicitar aprobación
5. Merge cuando CI pase

---

## 🐛 Troubleshooting

### Problema: Tests fallan con "ImportError"

**Solución:**
```bash
# Asegúrate de estar en el entorno virtual
# Windows:
.venv\Scripts\activate

# Linux/Mac:
source .venv/bin/activate

# Reinstalar dependencias
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Problema: Pre-commit hooks no se ejecutan

**Solución:**
```bash
# Reinstalar pre-commit
pip install pre-commit

# Instalar hooks
pre-commit install

# Verificar instalación
pre-commit run --all-files
```

### Problema: Coverage muy baja

**Solución:**
```bash
# Verificar qué archivos no están cubiertos
pytest --cov=rexus --cov-report=term-missing

# Agregar tests a archivos sin cobertura
```

### Problema: CI/CD falla localmente pero pasa en GitHub

**Solución:**
```bash
# Asegúrate de usar las mismas versiones
python --version  # Debe ser 3.10+

# Actualizar herramientas
pip install --upgrade pip
pip install -r requirements-dev.txt
```

### Problema: "ModuleNotFoundError: No module named 'PyQt6'"

**Solución:**
```bash
# Instalar PyQt6
pip install PyQt6

# Si falla, instalar desde wheels
pip install --only-binary :all: PyQt6
```

---

## 📚 Recursos Adicionales

### Documentación

- [CLAUDE.md](docs/CLAUDE.md) - Documentación de arquitectura
- [AUDITORIA_COMPLETA_EXPERTA_2025.md](docs/AUDITORIA_COMPLETA_EXPERTA_2025.md) - Auditoría completa

### Guías de Estilo

- [PEP 8](https://peps.python.org/pep-0008/) - Style Guide de Python
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Black Documentation](https://black.readthedocs.io/)

### Herramientas

- [Black](https://black.readthedocs.io/) - Formateador de código
- [Pytest](https://docs.pytest.org/) - Framework de testing
- [Pylint](https://pylint.pycqa.org/) - Linter avanzado
- [MyPy](https://mypy.readthedocs.io/) - Type checking

---

## 🤝 Contribuyendo

### Antes de Contribuir

1. Lee [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
2. Lee [CONTRIBUTING.md](CONTRIBUTING.md)
3. Instala dependencias de desarrollo
4. Configura pre-commit hooks

### Proceso de Contribución

1. Fork el repositorio
2. Crear feature branch
3. Hacer cambios con tests
4. Ejecutar `python scripts/dev.py all`
5. Crear Pull Request
6. Esperar revisión y CI/CD

---

## 📞 Soporte

### Canales de Comunicación

- **Issues**: [GitHub Issues](https://github.com/rexus/app/issues)
- **Discussions**: [GitHub Discussions](https://github.com/rexus/app/discussions)
- **Email**: dev@rexus.app

### Reportar Bugs

Usa el template de bug report en GitHub Issues:

```markdown
## Descripción
Breve descripción del bug

## Pasos para Reproducir
1. Ir a...
2. Hacer click en...
3. Ver error

## Comportamiento Esperado
Debería pasar X pero pasa Y

## Screenshots
Si es aplicable, agrega screenshots

## Entorno
- OS: [Windows 10, Ubuntu 22.04, etc.]
- Python Version: [3.10, 3.11, etc.]
- Rexus.app Version: [2.0.0]
```

---

## 📝 Notas de Desarrollo

### Estándares de Código

- **Longitud de línea**: Máximo 100 caracteres
- **Indentación**: 4 espacios (NO tabs)
- **Imports**: Ordenados con isort (stdlib, third-party, local)
- **Docstrings**: Google style para funciones y clases
- **Type hints**: Requerido en funciones públicas

### Patrones de Diseño

- **MVC**: Model-View-Controller para módulos
- **Repository**: Para acceso a datos
- **Service**: Para lógica de negocio compleja
- **Factory**: Para creación de objetos

### Convenciones de Nombres

- **Clases**: PascalCase (`UsuarioModel`)
- **Funciones/variables**: snake_case (`obtener_usuarios`)
- **Constantes**: UPPER_SNAKE_CASE (`MAX_INTENTOS`)
- **Privadas**: _leading_underscore (`_internal_method`)

---

**Última actualización:** 07 de Febrero 2025
**Versión:** 2.0.0
**Mantenedores:** Rexus.app Team
