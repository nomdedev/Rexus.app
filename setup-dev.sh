#!/bin/bash

echo "🚀 Configurando Rexus.app para desarrollo..."
echo

# Verificar que estamos en el directorio correcto
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py no encontrado"
    echo "   Ejecuta este script desde el directorio raíz de Rexus.app"
    exit 1
fi

# Instalar dependencias para hot-reload si no están
echo "📦 Verificando dependencias de desarrollo..."
python3 -c "import watchdog" 2>/dev/null || {
    echo "🔧 Instalando watchdog..."
    pip3 install watchdog
}

python3 -c "import dotenv" 2>/dev/null || {
    echo "🔧 Instalando python-dotenv..."
    pip3 install python-dotenv
}

# Verificar que existe el archivo .env.development
if [ ! -f ".env.development" ]; then
    echo "⚠️  Archivo .env.development no encontrado"
    echo "🔧 Creando configuración por defecto..."
    cat > .env.development << EOF
REXUS_DEV_USER=admin
REXUS_DEV_PASSWORD=admin
REXUS_DEV_AUTO_LOGIN=true
HOTRELOAD_ENABLED=true
EOF
fi

echo
echo "✅ Configuración completada!"
echo
echo "🎯 Cómo usar el servidor de desarrollo:"
echo "   👉 python3 dev-server-new.py"
echo
echo "🔐 Credenciales configuradas:"
echo "   Usuario: admin"
echo "   Contraseña: admin"
echo "   (edita .env.development para cambiar)"
echo

# Hacer el script ejecutable
chmod +x dev-server-new.py