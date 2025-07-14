@echo off
REM Script batch para automatización de tareas del proyecto stock.app
REM Uso: run.bat <tarea>

if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="test" goto test
if "%1"=="test-quick" goto test-quick
if "%1"=="test-edge" goto test-edge
if "%1"=="test-all" goto test-all
if "%1"=="coverage" goto coverage
if "%1"=="security" goto security
if "%1"=="metrics" goto metrics
if "%1"=="analyze" goto analyze
if "%1"=="clean" goto clean
if "%1"=="install" goto install

echo Tarea desconocida: %1
goto help

:help
echo.
echo === TAREAS DISPONIBLES PARA STOCK.APP ===
echo.
echo   test          Ejecutar tests criticos
echo   test-quick    Ejecutar tests rapidos
echo   test-edge     Ejecutar tests de edge cases
echo   test-all      Ejecutar todos los tests
echo   coverage      Generar reporte de cobertura
echo   security      Ejecutar analisis de seguridad
echo   metrics       Generar metricas del proyecto
echo   analyze       Ejecutar analisis completo de modulos
echo   clean         Limpiar archivos temporales
echo   install       Instalar dependencias
echo.
echo Uso: run.bat ^<tarea^>
echo Ejemplo: run.bat test
echo.
goto end

:test
echo.
echo === EJECUTANDO TESTS CRITICOS ===
python -m pytest tests/utils/ tests/test_schema_consistency.py -v
goto end

:test-quick
echo.
echo === EJECUTANDO TESTS RAPIDOS ===
python -m pytest tests/utils/ -v
goto end

:test-edge
echo.
echo === EJECUTANDO TESTS DE EDGE CASES ===
python -m pytest tests/inventario/test_inventario_edge_cases.py tests/obras/test_obras_edge_cases.py -v
goto end

:test-all
echo.
echo === EJECUTANDO TODOS LOS TESTS ===
python -m pytest tests/ -v
goto end

:coverage
echo.
echo === GENERANDO REPORTE DE COBERTURA ===
python -m pytest tests/ --cov=modules --cov=core --cov=utils --cov-report=html --cov-report=term
echo.
echo Reporte HTML disponible en: coverage_html/index.html
goto end

:security
echo.
echo === EJECUTANDO ANALISIS DE SEGURIDAD ===
python scripts/verificacion/analizar_seguridad_sql_codigo.py
python scripts/verificacion/escanear_vulnerabilidades.py
goto end

:metrics
echo.
echo === GENERANDO METRICAS DEL PROYECTO ===
python scripts/verificacion/metricas_rapidas.py
goto end

:analyze
echo.
echo === EJECUTANDO ANALISIS COMPLETO DE MODULOS ===
python scripts/verificacion/analizador_modulos.py
python scripts/verificacion/ejecutar_analisis_completo.py
goto end

:clean
echo.
echo === LIMPIANDO ARCHIVOS TEMPORALES ===
for /r %%i in (*.pyc) do del "%%i" 2>nul
for /d /r %%i in (__pycache__) do rmdir /s /q "%%i" 2>nul
if exist .pytest_cache rmdir /s /q .pytest_cache 2>nul
if exist coverage_html rmdir /s /q coverage_html 2>nul
if exist .coverage del .coverage 2>nul
echo Archivos temporales eliminados
goto end

:install
echo.
echo === INSTALANDO DEPENDENCIAS ===
pip install -r requirements.txt
pip install pytest pytest-cov pytest-mock black isort flake8 mypy
echo Dependencias instaladas
goto end

:end
