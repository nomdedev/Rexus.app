@echo off
echo 🐳 Probando Docker con auto-login...
echo.

echo 🔧 Construyendo contenedor...
docker-compose -f docker-compose-simple.yml build

echo.
echo 🚀 Iniciando contenedor con auto-login...
echo 🔐 Credenciales configuradas: admin/admin
echo 📺 VNC disponible en: localhost:5900

docker-compose -f docker-compose-simple.yml up