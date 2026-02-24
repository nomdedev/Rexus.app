# Estructura de Directorios Propuesta para Rexus.app

## Problemas Identificados

1. **Archivos de prueba en la raíz**: Archivos como `check_dependencies.py`, `test_corrections.py`, `simple_test.py`, `test_module_imports.py` que deberían estar en un directorio de pruebas.

2. **Scripts de utilidad dispersos**: Scripts de corrección y mantenimiento en la raíz (`fix_*.py`, `final_syntax_fix.py`) que deberían estar organizados adecuadamente.

3. **Archivos temporales mezclados**: Archivos como `temp_line.txt`, `pytest_temp.ini` están mezclados con el código fuente.

4. **Duplicación de archivos**: Múltiples archivos similares y copias de seguridad dispersas por todo el proyecto.

5. **Scripts y herramientas desorganizados**: Los scripts están divididos entre `scripts/`, `tools/` y la raíz sin una clara distinción de propósito.

## Estructura de Directorios Propuesta

### 1. Estructura Principal del Proyecto

```
Rexus.app/
├── rexus/                          # Módulo principal de la aplicación
│   ├── __init__.py
│   ├── bootstrap.py                # Inicialización de la aplicación
│   ├── main/                       # Punto de entrada principal
│   ├── api/                        # Componentes API
│   ├── core/                       # Componentes centrales
│   ├── models/                     # Modelos de datos
│   ├── modules/                    # Módulos de funcionalidad
│   │   ├── 01_inventario/
│   │   ├── 02_obras/
│   │   ├── 03_herrajes/
│   │   ├── 04_compras/
│   │   ├── 05_logistica/
│   │   ├── 06_pedidos/
│   │   ├── 07_vidrios/
│   │   ├── 08_administracion/
│   │   │   ├── contabilidad/
│   │   │   └── recursos_humanos/
│   │   ├── 09_mantenimiento/
│   │   ├── 10_auditoria/
│   │   ├── 11_usuarios/
│   │   ├── 12_configuracion/
│   │   └── 13_notificaciones/
│   ├── repositories/               # Repositorios de datos
│   ├── security/                   # Componentes de seguridad
│   ├── services/                   # Servicios de negocio
│   ├── ui/                         # Componentes de interfaz de usuario
│   │   └── components/
│   └── utils/                      # Utilidades generales
├── tests/                          # Pruebas del sistema
├── scripts/                        # Scripts de desarrollo y mantenimiento
├── tools/                          # Herramientas de desarrollo
├── temp/                           # Archivos temporales y de desarrollo
├── docs/                           # Documentación
├── config/                         # Configuraciones
├── sql/                            # Scripts SQL
├── resources/                      # Recursos estáticos
├── logs/                           # Logs de la aplicación
├── backups/                        # Copias de seguridad
├── cache/                          # Caché de la aplicación
├── monitoring/                     # Monitoreo
├── reports/                        # Reportes generados
├── docker/                         # Configuraciones Docker
├── examples/                       # Ejemplos de uso
└── .venv/                          # Entorno virtual
```

### 2. Organización de Tests

```
tests/
├── __init__.py
├── conftest.py                     # Configuración global de pytest
├── unit/                           # Pruebas unitarias
│   ├── __init__.py
│   ├── inventario/
│   ├── obras/
│   ├── herrajes/
│   ├── compras/
│   ├── logistica/
│   ├── pedidos/
│   ├── vidrios/
│   ├── administracion/
│   ├── mantenimiento/
│   ├── auditoria/
│   ├── usuarios/
│   ├── configuracion/
│   ├── notificaciones/
│   ├── models/
│   ├── repositories/
│   ├── security/
│   ├── services/
│   ├── ui/
│   └── utils/
├── integration/                    # Pruebas de integración
│   ├── __init__.py
│   ├── test_cache_manager.py
│   ├── test_compras_inventario_integration.py
│   ├── test_dashboard_integration.py
│   ├── test_flujo_obra_completo.py
│   └── test_database_integration.py
├── e2e/                           # Pruebas de extremo a extremo
│   ├── __init__.py
│   ├── test_workflow_compra_completo.py
│   └── test_workflows_completos.py
├── security/                      # Pruebas de seguridad
│   ├── __init__.py
│   ├── test_rate_limiter.py
│   ├── test_security_complete.py
│   └── test_sql_injection.py
├── ui/                            # Pruebas de interfaz de usuario
│   ├── __init__.py
│   ├── contrast_test.py
│   └── test_ui_interactions.py
├── performance/                   # Pruebas de rendimiento
│   ├── __init__.py
│   └── test_performance.py
├── utils/                         # Utilidades de testing
│   ├── __init__.py
│   ├── mock_factories.py
│   ├── module_import_helper.py
│   └── security_helpers.py
├── fixtures/                      # Datos de prueba
│   ├── __init__.py
│   ├── sample_data.json
│   └── test_database.sql
└── reports/                       # Reportes de pruebas
    ├── coverage/
    ├── performance/
    └── security/
```

### 3. Estructura de Scripts

```
scripts/
├── __init__.py
├── development/                   # Scripts de desarrollo
│   ├── __init__.py
│   ├── dev.py                     # Script principal de desarrollo
│   ├── start-dev.sh               # Script para iniciar entorno de desarrollo
│   ├── validate_env.py            # Validación de entorno
│   └── temp_app.py                # Aplicación temporal para pruebas
├── testing/                       # Scripts relacionados con pruebas
│   ├── __init__.py
│   ├── run_tests.py              # Script para ejecutar pruebas
│   ├── generate_coverage.py     # Generación de reportes de cobertura
│   └── test_runner.py            # Runner personalizado de pruebas
├── maintenance/                   # Scripts de mantenimiento
│   ├── __init__.py
│   ├── cleanup.py                # Limpieza de archivos temporales
│   ├── backup.py                 # Gestión de copias de seguridad
│   └── database_maintenance.py   # Mantenimiento de base de datos
├── deployment/                    # Scripts de despliegue
│   ├── __init__.py
│   ├── deploy.py                 # Script de despliegue
│   ├── rollback.py               # Script de rollback
│   └── environment_setup.py       # Configuración de entorno
├── migration/                     # Scripts de migración
│   ├── __init__.py
│   ├── migrate_secrets.py        # Migración de secretos
│   └── database_migration.py     # Migración de base de datos
└── tools/                         # Scripts de herramientas
    ├── __init__.py
    ├── fix_code_quality.py       # Corrección de calidad de código
    └── critical_syntax_fixer.py   # Corrección de sintaxis crítica
```

### 4. Directorio para Archivos Temporales

```
temp/
├── development/                   # Archivos temporales de desarrollo
│   ├── temp_app.py
│   ├── temp_line.txt
│   └── pytest_temp.ini
├── cache/                         # Caché temporal
│   ├── __init__.py
│   └── .gitkeep
├── logs/                          # Logs temporales
│   ├── __init__.py
│   └── .gitkeep
├── reports/                       # Reportes temporales
│   ├── __init__.py
│   └── .gitkeep
└── .gitkeep                       # Para mantener el directorio en git
```

### 5. Organización de Herramientas y Utilidades

```
tools/
├── __init__.py
├── development/                   # Herramientas de desarrollo
│   ├── __init__.py
│   ├── Makefile                   # Comandos comunes de desarrollo
│   ├── .pre-commit-config.yaml    # Configuración de pre-commit
│   ├── .flake8                    # Configuración de flake8
│   ├── .pylintrc                  # Configuración de pylint
│   ├── .mypy.ini                  # Configuración de mypy
│   ├── pyrightconfig.json         # Configuración de pyright
│   └── pytest.ini                 # Configuración de pytest
├── security/                      # Herramientas de seguridad
│   ├── __init__.py
│   ├── .bandit                    # Configuración de bandit
│   ├── bandit_results.json        # Resultados de análisis de seguridad
│   └── security_validator.py      # Validador de seguridad
├── quality/                       # Herramientas de calidad de código
│   ├── __init__.py
│   ├── sonar-project.properties   # Configuración de SonarQube
│   └── check_table_schema.py      # Verificación de esquema de tablas
├── testing/                       # Herramientas de testing
│   ├── __init__.py
│   └── test_modulos_integrales.py # Pruebas integrales de módulos
└── docker/                        # Herramientas Docker
    ├── __init__.py
    ├── .dockerignore              # Archivos a ignorar en Docker
    └── docker-compose.*.yml       # Configuraciones de Docker Compose
```

## Archivos Específicos que Deben Moverse

### De la raíz a temp/development/:
- `temp_line.txt`
- `pytest_temp.ini`
- `temp_app.py` (actualmente en scripts/)

### De la raíz a scripts/maintenance/:
- `check_dependencies.py`
- `check_missing_deps.py`
- `fix_fstrings.py`
- `fix_fstrings_massive.py`
- `fix_encoding_issues.py`
- `fix_all_syntax_errors.py`
- `fix_critical_syntax_errors.py`
- `final_syntax_fix.py`
- `fix_usuarios_controller_complete.py`
- `fix_usuarios_controller_syntax.py`

### De la raíz a scripts/testing/:
- `test_corrections.py`
- `test_module_imports.py`
- `simple_test.py`

### De scripts/ a scripts/development/:
- `dev.py`
- `start-dev.sh`
- `validate_env.py`

### De scripts/tools/ a scripts/tools/:
- `fix_code_quality.py`

### De tools/ a tools/development/:
- `Makefile`
- `.pre-commit-config.yaml`
- `.flake8`
- `.pylintrc`
- `.mypy.ini`
- `pyrightconfig.json`
- `pytest.ini`

### De tools/ a tools/security/:
- `.bandit`
- `bandit_results.json`
- `security_validator.py`

### De tools/ a tools/quality/:
- `sonar-project.properties`
- `check_table_schema.py`

### De tools/ a tools/testing/:
- `test_modulos_integrales.py`

### De tools/ a tools/docker/:
- `.dockerignore`
- `docker-compose.dev.yml`
- `docker-compose.monitoring.yml`

## Plan de Migración

### Fase 1: Preparación
1. Crear la nueva estructura de directorios
2. Crear archivos .gitkeep donde sea necesario
3. Actualizar archivos de configuración para reflejar nuevas rutas

### Fase 2: Migración de Archivos
1. Mover archivos temporales a temp/development/
2. Mover scripts de mantenimiento a scripts/maintenance/
3. Mover scripts de testing a scripts/testing/
4. Mover scripts de desarrollo a scripts/development/
5. Mover herramientas de desarrollo a tools/development/
6. Mover herramientas de seguridad a tools/security/
7. Mover herramientas de calidad a tools/quality/
8. Mover herramientas de testing a tools/testing/
9. Mover herramientas Docker a tools/docker/

### Fase 3: Actualización de Referencias
1. Actualizar importaciones en el código fuente
2. Actualizar configuraciones de IDE
3. Actualizar documentación
4. Actualizar scripts de CI/CD

### Fase 4: Limpieza
1. Eliminar directorios vacíos
2. Actualizar .gitignore
3. Verificar que todo funcione correctamente

## Beneficios de la Nueva Estructura

1. **Organización clara**: Cada tipo de archivo tiene su lugar designado
2. **Separación de responsabilidades**: Los scripts están clasificados por su propósito
3. **Facilidad de mantenimiento**: Es más fácil encontrar y actualizar archivos
4. **Mejor colaboración**: Los desarrolladores pueden navegar más fácilmente
5. **Escalabilidad**: La estructura puede crecer con el proyecto
6. **Consistencia**: Sigue las mejores prácticas de organización de proyectos Python