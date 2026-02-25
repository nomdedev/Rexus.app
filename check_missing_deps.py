#!/usr/bin/env python3
"""
Verifica qué dependencias de requirements.txt faltan instalar
"""
import subprocess
import sys
from typing import List, Tuple


def normalize_package_name(name: str) -> str:
    """Normaliza nombre de paquete para comparación robusta."""
    return name.strip().lower().replace("_", "-")

# Dependencias requeridas en requirements.txt
REQUIRED_PACKAGES = [
    "PyQt6>=6.6.0",
    "PyQt6-Qt6>=6.6.0",
    "PyQt6-WebEngine>=6.6.0",
    "pyodbc>=4.0.35",
    "cryptography>=41.0.0",
    "bcrypt>=4.0.1",
    "argon2-cffi>=21.3.0",
    "redis>=5.0.0",
    "hiredis>=2.2.0",
    "python-dotenv>=1.0.0",
    "psutil>=5.9.0",
    "typing-extensions>=4.7.0",
    "python-dateutil>=2.8.2",
    "pandas>=2.0.0",
    "openpyxl>=3.1.0",
    "qrcode>=7.4.0",
    "reportlab>=4.0.0",
    "Pillow>=10.0.0",
    "schedule>=1.2.0",
    "requests>=2.31.0",
    "pyotp>=2.9.0",
    "flask>=3.0.0",
    "fastapi>=0.111.0",
    "starlette>=0.37.0",
    "prometheus-client>=0.20.0",
    "folium>=0.17.0",
    "pytest>=7.4.0",
    "pytest-qt>=4.2.0",
    "pytest-cov>=4.1.0",
    "black>=23.7.0",
    "flake8>=6.0.0",
    "memory-profiler>=0.60.0",
    "colorlog>=6.7.0",
    "sphinx>=7.1.0",
    "sphinx-rtd-theme>=1.3.0",
    "waitress>=2.1.2",
]

def get_installed_packages() -> List[str]:
    """Obtiene lista de paquetes instalados"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=freeze"],
            capture_output=True,
            text=True,
            check=True
        )
        installed = {}
        for line in result.stdout.strip().split('\n'):
            if '==' in line:
                name, version = line.split('==', 1)
                installed[normalize_package_name(name)] = version
        return installed
    except subprocess.CalledProcessError:
        return {}

def check_package(package_spec: str, installed: dict) -> Tuple[bool, str, str]:
    """
    Verifica si un paquete está instalado cumpliendo con la versión requerida
    Retorna: (está_instalado, nombre_paquete, estado)
    """
    # Extraer nombre y versión
    if '>=' in package_spec:
        name = package_spec.split('>=')[0].strip()
    else:
        name = package_spec

    # Buscar paquete instalado (case-insensitive)
    installed_version = installed.get(normalize_package_name(name))

    if installed_version:
        status = f"[OK] {name} ({installed_version} instalado)"
        return True, name, status
    else:
        status = f"[X] {name} (requerido: {package_spec})"
        return False, name, status

def main():
    print("=" * 70)
    print("Verificacion de dependencias de Rexus.app")
    print("=" * 70)
    print()

    # Obtener paquetes instalados
    installed = get_installed_packages()
    print(f"Paquetes instalados: {len(installed)}")
    print()

    # Verificar cada paquete requerido
    missing = []
    present = []

    print("DEPENDENCIAS REQUERIDAS:")
    print("-" * 70)

    for package_spec in REQUIRED_PACKAGES:
        is_installed, name, status = check_package(package_spec, installed)
        print(status)
        if is_installed:
            present.append(name)
        else:
            missing.append(package_spec)

    print()
    print("=" * 70)
    print("RESUMEN:")
    print("=" * 70)
    print(f"Instaladas: {len(present)}/{len(REQUIRED_PACKAGES)}")
    print(f"Faltantes: {len(missing)}/{len(REQUIRED_PACKAGES)}")
    print()

    if missing:
        print("PAQUETES FALTANTES:")
        print("-" * 70)
        for pkg in missing:
            print(f"  - {pkg}")
        print()
        print("Comando para instalar las dependencias faltantes:")
        print()
        print(f"pip install {' '.join(missing)}")
        print()
        print("O instala todas las dependencias:")
        print("pip install -r requirements.txt")
        return 1
    else:
        print("Todas las dependencias estan instaladas")
        return 0

if __name__ == "__main__":
    sys.exit(main())
