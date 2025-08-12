@echo off
echo 🔥 Configurando entorno de desarrollo Rexus.app

REM Verificar si Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python no encontrado. Instala Python 3.10+
    pause
    exit /b 1
)

echo 📦 Instalando dependencias para hot-reload...

REM Instalar watchdog si no está instalado
pip install watchdog python-dotenv

echo.
echo 🚀 Iniciando servidor de desarrollo con hot-reload...
echo Presiona Ctrl+C para detener
echo.

REM Ejecutar el servidor de desarrollo
python dev-server.py

pause
