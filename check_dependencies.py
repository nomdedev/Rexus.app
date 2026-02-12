#!/usr/bin/env python3
"""
Script para verificar e instalar dependencias faltantes
"""
import subprocess
import sys
from pathlib import Path

def parse_requirements(file_path):
    """Parsea un archivo de requisitos."""
    requirements = []
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            # Ignorar comentarios y líneas vacías
            if line and not line.startswith('#'):
                # Extraer nombre del paquete
                pkg = line.split('>=')[0].split('==')[0].split('<=')[0].split('>')[0].split('<')[0].strip()
                if pkg:
                    requirements.append((pkg, line))
    return requirements

def check_package_installed(package_name):
    """Verifica si un paquete está instalado."""
    try:
        __import__(package_name.replace('-', '_'))
        return True
    except ImportError:
        return False

def main():
    root = Path(__file__).parent
    req_file = root / 'requirements.txt'
    
    print("🔍 Verificando dependencias...\n")
    
    requirements = parse_requirements(req_file)
    missing = []
    installed = []
    
    for pkg_name, full_spec in requirements:
        if check_package_installed(pkg_name):
            installed.append(pkg_name)
            print(f"✓ {pkg_name}")
        else:
            missing.append(full_spec)
            print(f"✗ {pkg_name} - FALTANTE")
    
    print(f"\n{'='*60}")
    print(f"Instaladas: {len(installed)}")
    print(f"Faltantes: {len(missing)}")
    print(f"{'='*60}\n")
    
    if missing:
        print("Dependencias faltantes:")
        for spec in missing:
            print(f"  - {spec}")
        
        print("\nInstalando dependencias faltantes...")
        print(f"{'='*60}\n")
        
        # Instalar cada una
        for spec in missing:
            print(f"Instalando: {spec}")
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', spec],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"✓ {spec} instalado exitosamente\n")
            else:
                print(f"✗ Error instalando {spec}")
                print(result.stderr[:200])
                print()
    else:
        print("✓ Todas las dependencias están instaladas!")

if __name__ == '__main__':
    main()
