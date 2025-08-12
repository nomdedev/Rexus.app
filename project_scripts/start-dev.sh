#!/bin/bash

# Script para desarrollo rápido local (sin Docker)
echo "🔥 Configurando entorno de desarrollo Rexus.app"

# Verificar si Python está instalado
if ! command -v python &> /dev/null; then
    echo "❌ Python no encontrado. Instala Python 3.10+"
    exit 1
fi

# Verificar si pip está instalado
if ! command -v pip &> /dev/null; then
    echo "❌ pip no encontrado"
    exit 1
fi

echo "📦 Instalando dependencias para hot-reload..."

# Instalar watchdog si no está instalado
pip install watchdog python-dotenv

echo "🚀 Iniciando servidor de desarrollo con hot-reload..."
echo "Presiona Ctrl+C para detener"
echo ""

# Ejecutar el servidor de desarrollo
python dev-server.py
