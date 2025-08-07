@echo off
REM Dependency Security Audit Script - Rexus.app
REM Ejecuta auditoría completa de dependencias de seguridad

echo.
echo ========================================
echo  AUDITORÍA DE SEGURIDAD - REXUS.APP
echo ========================================
echo.

REM Verificar si estamos en el directorio correcto
if not exist requirements.txt (
    echo ❌ Error: No se encuentra requirements.txt
    echo    Ejecutar desde el directorio raíz del proyecto
    pause
    exit /b 1
)

echo 🔍 Iniciando auditoría de dependencias...
echo.

REM 1. Verificar pip-audit
echo 📦 Verificando herramienta pip-audit...
pip show pip-audit > nul 2>&1
if errorlevel 1 (
    echo ⚠️  pip-audit no está instalado
    echo 📥 Instalando pip-audit...
    pip install pip-audit
    if errorlevel 1 (
        echo ❌ Error instalando pip-audit
        pause
        exit /b 1
    )
)

echo ✅ pip-audit disponible
echo.

REM 2. Ejecutar pip-audit
echo 🔒 Ejecutando auditoría de vulnerabilidades...
pip-audit --format=table --desc
if errorlevel 1 (
    echo.
    echo ⚠️  Se encontraron vulnerabilidades. Ver detalles arriba.
) else (
    echo.
    echo ✅ No se encontraron vulnerabilidades conocidas
)

echo.

REM 3. Verificar paquetes desactualizados
echo 📦 Verificando paquetes desactualizados...
pip list --outdated --format=table

echo.

REM 4. Ejecutar script de auditoría personalizado
echo 🛡️  Ejecutando auditoría personalizada...
python tools\security\dependency_security_audit.py
if errorlevel 1 (
    echo ⚠️  Auditoría completada con advertencias
) else (
    echo ✅ Auditoría completada exitosamente
)

echo.
echo 📊 AUDITORÍA COMPLETADA
echo ========================================
echo.
echo 💡 ACCIONES RECOMENDADAS:
echo    1. Revisar vulnerabilidades encontradas
echo    2. Actualizar paquetes críticos
echo    3. Ejecutar tests después de actualizar
echo    4. Configurar auditorías automáticas
echo.

pause