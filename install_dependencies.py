#!/usr/bin/env python3
import subprocess
import sys

def install_package(package):
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", package], 
                      check=True, capture_output=True, text=True)
        print(f"✅ {package} instalado exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando {package}: {e}")
        return False

# Instalar dependencias críticas
packages = [
    "PyQt6-WebEngine",
    "folium>=0.20.0",
    "pyodbc",
    "python-dotenv"
]

print("🔧 Instalando dependencias críticas...")
for package in packages:
    install_package(package)

print("✅ Instalación de dependencias completada")
