# Script PowerShell para automatización de tareas del proyecto
# Equivalente al Makefile para entornos Windows

param(
    [Parameter(Position=0)]
    [string]$Task = "help"
)

function Show-Help {
    Write-Host "🚀 TAREAS DISPONIBLES PARA STOCK.APP" -ForegroundColor Cyan
    Write-Host "=" * 50 -ForegroundColor Gray
    Write-Host ""
    Write-Host "  test          " -ForegroundColor Green -NoNewline
    Write-Host "Ejecutar tests críticos"
    Write-Host "  test-quick    " -ForegroundColor Green -NoNewline
    Write-Host "Ejecutar tests rápidos"
    Write-Host "  test-edge     " -ForegroundColor Green -NoNewline
    Write-Host "Ejecutar tests de edge cases"
    Write-Host "  test-all      " -ForegroundColor Green -NoNewline
    Write-Host "Ejecutar todos los tests"
    Write-Host "  coverage      " -ForegroundColor Yellow -NoNewline
    Write-Host "Generar reporte de cobertura"
    Write-Host "  security      " -ForegroundColor Red -NoNewline
    Write-Host "Ejecutar análisis de seguridad"
    Write-Host "  metrics       " -ForegroundColor Blue -NoNewline
    Write-Host "Generar métricas del proyecto"
    Write-Host "  analyze       " -ForegroundColor Blue -NoNewline
    Write-Host "Ejecutar análisis completo de módulos"
    Write-Host "  format        " -ForegroundColor Magenta -NoNewline
    Write-Host "Formatear código"
    Write-Host "  lint          " -ForegroundColor Magenta -NoNewline
    Write-Host "Análisis estático de código"
    Write-Host "  install       " -ForegroundColor White -NoNewline
    Write-Host "Instalar dependencias"
    Write-Host "  clean         " -ForegroundColor DarkGray -NoNewline
    Write-Host "Limpiar archivos temporales"
    Write-Host "  ci            " -ForegroundColor Cyan -NoNewline
    Write-Host "Simular pipeline de CI/CD completo"
    Write-Host ""
    Write-Host "Uso: .\run.ps1 <tarea>" -ForegroundColor Yellow
    Write-Host "Ejemplo: .\run.ps1 test" -ForegroundColor Yellow
}

function Invoke-Test {
    Write-Host "🧪 EJECUTANDO TESTS CRÍTICOS" -ForegroundColor Green
    Write-Host "-" * 40 -ForegroundColor Gray
    & python -m pytest tests/utils/ tests/test_schema_consistency.py -v
}

function Invoke-TestQuick {
    Write-Host "⚡ EJECUTANDO TESTS RÁPIDOS" -ForegroundColor Green
    Write-Host "-" * 40 -ForegroundColor Gray
    & python -m pytest tests/utils/ -v
}

function Invoke-TestEdge {
    Write-Host "🎯 EJECUTANDO TESTS DE EDGE CASES" -ForegroundColor Green
    Write-Host "-" * 40 -ForegroundColor Gray
    & python -m pytest tests/inventario/test_inventario_edge_cases.py tests/obras/test_obras_edge_cases.py -v
}

function Invoke-TestAll {
    Write-Host "🧪 EJECUTANDO TODOS LOS TESTS" -ForegroundColor Green
    Write-Host "-" * 40 -ForegroundColor Gray
    & python -m pytest tests/ -v
}

function Invoke-Coverage {
    Write-Host "📊 GENERANDO REPORTE DE COBERTURA" -ForegroundColor Yellow
    Write-Host "-" * 40 -ForegroundColor Gray
    & python -m pytest tests/ --cov=modules --cov=core --cov=utils --cov-report=html --cov-report=term
    Write-Host ""
    Write-Host "📄 Reporte HTML disponible en: coverage_html/index.html" -ForegroundColor Cyan
}

function Invoke-Security {
    Write-Host "🔒 EJECUTANDO ANÁLISIS DE SEGURIDAD" -ForegroundColor Red
    Write-Host "-" * 40 -ForegroundColor Gray
    & python scripts/verificacion/analizar_seguridad_sql_codigo.py
    & python scripts/verificacion/escanear_vulnerabilidades.py
}

function Invoke-Metrics {
    Write-Host "📈 GENERANDO MÉTRICAS DEL PROYECTO" -ForegroundColor Blue
    Write-Host "-" * 40 -ForegroundColor Gray
    & python scripts/verificacion/metricas_rapidas.py
}

function Invoke-Analyze {
    Write-Host "🔍 EJECUTANDO ANÁLISIS COMPLETO DE MÓDULOS" -ForegroundColor Blue
    Write-Host "-" * 40 -ForegroundColor Gray
    & python scripts/verificacion/analizador_modulos.py
    & python scripts/verificacion/ejecutar_analisis_completo.py
}

function Invoke-Format {
    Write-Host "🎨 FORMATEANDO CÓDIGO" -ForegroundColor Magenta
    Write-Host "-" * 40 -ForegroundColor Gray
    try {
        & black modules/ core/ utils/ scripts/
        & isort modules/ core/ utils/ scripts/
        Write-Host "✅ Código formateado correctamente" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Instalar black e isort: pip install black isort" -ForegroundColor Yellow
    }
}

function Invoke-Lint {
    Write-Host "🔍 EJECUTANDO ANÁLISIS ESTÁTICO" -ForegroundColor Magenta
    Write-Host "-" * 40 -ForegroundColor Gray
    try {
        & flake8 modules/ core/ utils/ --max-line-length=88
        & mypy modules/ core/ utils/ --ignore-missing-imports
        Write-Host "✅ Análisis estático completado" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Instalar herramientas: pip install flake8 mypy" -ForegroundColor Yellow
    }
}

function Invoke-Install {
    Write-Host "📦 INSTALANDO DEPENDENCIAS" -ForegroundColor White
    Write-Host "-" * 40 -ForegroundColor Gray
    & pip install -r requirements.txt
    & pip install pytest pytest-cov pytest-mock black isort flake8 mypy
    Write-Host "✅ Dependencias instaladas" -ForegroundColor Green
}

function Invoke-Clean {
    Write-Host "🧹 LIMPIANDO ARCHIVOS TEMPORALES" -ForegroundColor DarkGray
    Write-Host "-" * 40 -ForegroundColor Gray

    # Limpiar archivos Python
    Get-ChildItem -Recurse -Include "*.pyc" | Remove-Item -Force
    Get-ChildItem -Recurse -Directory -Name "__pycache__" | Remove-Item -Recurse -Force

    # Limpiar archivos de test
    if (Test-Path ".pytest_cache") { Remove-Item ".pytest_cache" -Recurse -Force }
    if (Test-Path "coverage_html") { Remove-Item "coverage_html" -Recurse -Force }
    if (Test-Path ".coverage") { Remove-Item ".coverage" -Force }

    Write-Host "✅ Archivos temporales eliminados" -ForegroundColor Green
}

function Invoke-CI {
    Write-Host "🚀 SIMULANDO PIPELINE DE CI/CD COMPLETO" -ForegroundColor Cyan
    Write-Host "=" * 50 -ForegroundColor Gray

    Write-Host ""
    Write-Host "1️⃣ Formateando código..." -ForegroundColor Yellow
    Invoke-Format

    Write-Host ""
    Write-Host "2️⃣ Ejecutando análisis estático..." -ForegroundColor Yellow
    Invoke-Lint

    Write-Host ""
    Write-Host "3️⃣ Ejecutando análisis de seguridad..." -ForegroundColor Yellow
    Invoke-Security

    Write-Host ""
    Write-Host "4️⃣ Ejecutando todos los tests..." -ForegroundColor Yellow
    Invoke-TestAll

    Write-Host ""
    Write-Host "5️⃣ Generando reporte de cobertura..." -ForegroundColor Yellow
    Invoke-Coverage

    Write-Host ""
    Write-Host "🎉 PIPELINE CI/CD COMPLETADO" -ForegroundColor Green
    Write-Host "=" * 50 -ForegroundColor Gray
}

# Ejecutar tarea solicitada
switch ($Task.ToLower()) {
    "test" { Invoke-Test }
    "test-quick" { Invoke-TestQuick }
    "test-edge" { Invoke-TestEdge }
    "test-all" { Invoke-TestAll }
    "coverage" { Invoke-Coverage }
    "security" { Invoke-Security }
    "metrics" { Invoke-Metrics }
    "analyze" { Invoke-Analyze }
    "format" { Invoke-Format }
    "lint" { Invoke-Lint }
    "install" { Invoke-Install }
    "clean" { Invoke-Clean }
    "ci" { Invoke-CI }
    "help" { Show-Help }
    default {
        Write-Host "❌ Tarea desconocida: $Task" -ForegroundColor Red
        Write-Host ""
        Show-Help
    }
}
