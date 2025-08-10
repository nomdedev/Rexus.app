@echo off
echo 🚀 Configurando Rexus.app para desarrollo...
echo.

REM Verificar que estamos en el directorio correcto
if not exist "main.py" (
    echo ❌ Error: main.py no encontrado
    echo    Ejecuta este script desde el directorio raíz de Rexus.app
    pause
    exit /b 1
)

REM Instalar dependencias para hot-reload si no están
echo 📦 Verificando dependencias de desarrollo...
python -c "import watchdog" 2>nul || (
    echo 🔧 Instalando watchdog...
    pip install watchdog
)

python -c "import dotenv" 2>nul || (
    echo 🔧 Instalando python-dotenv...
    pip install python-dotenv
)

REM Verificar que existe el archivo .env.development
if not exist ".env.development" (
    echo ⚠️  Archivo .env.development no encontrado
    echo 🔧 Creando configuración por defecto...
    echo REXUS_DEV_USER=admin > .env.development
    echo REXUS_DEV_PASSWORD=admin >> .env.development
    echo REXUS_DEV_AUTO_LOGIN=true >> .env.development
    echo HOTRELOAD_ENABLED=true >> .env.development
)

echo.
echo ✅ Configuración completada!
echo.
echo 🎯 Cómo usar el servidor de desarrollo:
echo    👉 python dev-server-new.py
echo.
echo 🔐 Credenciales configuradas:
echo    Usuario: admin
echo    Contraseña: admin
echo    (edita .env.development para cambiar)
echo.
pause