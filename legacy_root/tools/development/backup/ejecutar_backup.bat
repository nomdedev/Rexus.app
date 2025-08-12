@echo off
echo =====================================================
echo   Sistema de Backup Automatizado - Rexus.app v2.0.0
echo =====================================================
echo.

REM Verificar que estemos en el directorio correcto
if not exist "rexus" (
    echo ERROR: No se encuentra el directorio 'rexus'
    echo Este script debe ejecutarse desde la raiz del proyecto
    pause
    exit /b 1
)

REM Configurar PYTHONPATH
set PYTHONPATH=%CD%

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en PATH
    pause
    exit /b 1
)

REM Verificar sqlcmd
sqlcmd /? >nul 2>&1
if errorlevel 1 (
    echo ADVERTENCIA: sqlcmd no encontrado. Algunas funciones de backup pueden no funcionar.
    echo Instale SQL Server Command Line Tools para funcionalidad completa.
    echo.
)

REM Crear directorio de backups si no existe
if not exist "backups" mkdir backups

echo Iniciando sistema de backup...
echo.

REM Ejecutar el sistema de backup
python tools\development\backup\sistema_backup_automatizado.py

if errorlevel 1 (
    echo.
    echo ERROR: El sistema de backup termino con errores
    pause
    exit /b 1
)

echo.
echo Sistema de backup finalizado correctamente
pause