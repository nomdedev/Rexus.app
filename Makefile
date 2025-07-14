# Makefile para automatización de tareas del proyecto

.PHONY: test test-quick test-edge test-all coverage security format lint clean install help

# Comandos principales
test:  ## Ejecutar tests críticos
	python -m pytest tests/utils/ tests/test_schema_consistency.py -v

test-quick:  ## Ejecutar tests rápidos
	python -m pytest tests/utils/ -v

test-edge:  ## Ejecutar tests de edge cases
	python -m pytest tests/inventario/test_inventario_edge_cases.py tests/obras/test_obras_edge_cases.py -v

test-all:  ## Ejecutar todos los tests
	python -m pytest tests/ -v

coverage:  ## Generar reporte de cobertura
	python -m pytest tests/ --cov=modules --cov=core --cov=utils --cov-report=html --cov-report=term

security:  ## Ejecutar análisis de seguridad
	python scripts/verificacion/analizar_seguridad_sql_codigo.py
	python scripts/verificacion/escanear_vulnerabilidades.py

metrics:  ## Generar métricas del proyecto
	python scripts/verificacion/metricas_rapidas.py

analyze:  ## Ejecutar análisis completo de módulos
	python scripts/verificacion/analizador_modulos.py
	python scripts/verificacion/ejecutar_analisis_completo.py

format:  ## Formatear código
	black modules/ core/ utils/ scripts/
	isort modules/ core/ utils/ scripts/

lint:  ## Análisis estático de código
	flake8 modules/ core/ utils/ --max-line-length=88
	mypy modules/ core/ utils/ --ignore-missing-imports

install:  ## Instalar dependencias
	pip install -r requirements.txt
	pip install pytest pytest-cov pytest-mock black isort flake8 mypy

clean:  ## Limpiar archivos temporales
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf coverage_html
	rm -rf .coverage

setup-dev:  ## Configurar entorno de desarrollo
	pip install pre-commit
	pre-commit install
	$(MAKE) install

ci:  ## Simular pipeline de CI/CD localmente
	$(MAKE) format
	$(MAKE) lint
	$(MAKE) security
	$(MAKE) test-all
	$(MAKE) coverage

help:  ## Mostrar esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

# Comandos de desarrollo
dev-check:  ## Verificación rápida antes de commit
	$(MAKE) test
	$(MAKE) lint

prod-check:  ## Verificación completa para producción
	$(MAKE) ci
	python scripts/verificacion/verificacion_completa.py

# Reportes
report-full:  ## Generar reporte completo
	$(MAKE) metrics
	$(MAKE) analyze
	$(MAKE) coverage
	python scripts/verificacion/reporte_final_cobertura.py
