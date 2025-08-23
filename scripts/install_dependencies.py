#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instalador de Dependencias Faltantes - Rexus.app
Instala automáticamente las dependencias que faltan en el sistema
"""

import subprocess
import sys
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Lista de dependencias requeridas
REQUIRED_PACKAGES = [
    'PyQt6-WebEngine',
    'requests',
    'pandas',
    'openpyxl',  # Para exportar a Excel
    'pillow',    # Para manejo de imágenes
    'pyodbc',    # Para SQL Server
    'cryptography',  # Para seguridad
    'qrcode',    # Para códigos QR
    'reportlab', # Para PDFs
]

OPTIONAL_PACKAGES = [
    'psutil',    # Para monitoreo del sistema
    'schedule',  # Para tareas programadas
    'matplotlib', # Para gráficos
    'plotly',    # Para gráficos interactivos
]

def check_package_installed(package_name):
    """Verifica si un paquete está instalado."""
    try:
        __import__(package_name.replace('-', '_').lower())
        return True
    except ImportError:
        return False

def install_package(package_name):
    """Instala un paquete usando pip."""
    try:
        logger.info(f"Instalando {package_name}...")
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', package_name],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"✅ {package_name} instalado exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Error instalando {package_name}: {e}")
        logger.error(f"Salida: {e.stdout}")
        logger.error(f"Error: {e.stderr}")
        return False

def upgrade_pip():
    """Actualiza pip a la última versión."""
    try:
        logger.info("Actualizando pip...")
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info("✅ pip actualizado exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        logger.warning(f"⚠️ No se pudo actualizar pip: {e}")
        return False

def check_python_version():
    """Verifica que la versión de Python sea compatible."""
    python_version = sys.version_info
    
    if python_version < (3, 8):
        logger.error(f"❌ Python {python_version.major}.{python_version.minor} no es compatible")
        logger.error("Se requiere Python 3.8 o superior")
        return False
    
    logger.info(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} es compatible")
    return True

def install_dependencies():
    """Instala todas las dependencias necesarias."""
    
    print("🚀 INSTALADOR DE DEPENDENCIAS - REXUS.APP")
    print("=" * 50)
    
    # Verificar versión de Python
    if not check_python_version():
        return False
    
    # Actualizar pip
    upgrade_pip()
    
    print("\n📦 INSTALANDO DEPENDENCIAS REQUERIDAS...")
    print("-" * 40)
    
    required_success = 0
    required_failed = []
    
    for package in REQUIRED_PACKAGES:
        # Verificar si ya está instalado
        package_import_name = package.replace('-', '_').lower()
        
        # Mapeo especial para algunos paquetes
        special_imports = {
            'pyqt6_webengine': 'PyQt6.QtWebEngine',
            'pyqt6': 'PyQt6',
            'reportlab': 'reportlab.pdfgen',
            'openpyxl': 'openpyxl',
            'pillow': 'PIL'
        }
        
        import_name = special_imports.get(package_import_name, package_import_name)
        
        try:
            if import_name.startswith('PyQt6'):
                # Para PyQt6, intentar importar el módulo específico
                __import__(import_name)
            else:
                __import__(import_name)
            logger.info(f"✅ {package} ya está instalado")
            required_success += 1
        except ImportError:
            # Intentar instalar
            if install_package(package):
                required_success += 1
            else:
                required_failed.append(package)
    
    print(f"\n📊 DEPENDENCIAS REQUERIDAS: {required_success}/{len(REQUIRED_PACKAGES)} instaladas")
    
    if required_failed:
        print("❌ Falló la instalación de:")
        for package in required_failed:
            print(f"   - {package}")
    
    print("\n📦 INSTALANDO DEPENDENCIAS OPCIONALES...")
    print("-" * 40)
    
    optional_success = 0
    optional_failed = []
    
    for package in OPTIONAL_PACKAGES:
        package_import_name = package.replace('-', '_').lower()
        
        try:
            __import__(package_import_name)
            logger.info(f"✅ {package} ya está instalado")
            optional_success += 1
        except ImportError:
            if install_package(package):
                optional_success += 1
            else:
                optional_failed.append(package)
    
    print(f"\n📊 DEPENDENCIAS OPCIONALES: {optional_success}/{len(OPTIONAL_PACKAGES)} instaladas")
    
    if optional_failed:
        print("⚠️ No se pudieron instalar (opcional):")
        for package in optional_failed:
            print(f"   - {package}")
    
    # Resumen final
    print("\n" + "=" * 50)
    print("📋 RESUMEN DE INSTALACIÓN")
    print("=" * 50)
    
    total_required = len(REQUIRED_PACKAGES)
    total_optional = len(OPTIONAL_PACKAGES)
    
    print(f"✅ Dependencias requeridas: {required_success}/{total_required}")
    print(f"📦 Dependencias opcionales: {optional_success}/{total_optional}")
    
    if required_success == total_required:
        print("\n🎉 ¡INSTALACIÓN COMPLETADA EXITOSAMENTE!")
        print("Todas las dependencias requeridas están disponibles")
        
        if optional_success == total_optional:
            print("🌟 ¡BONUS! Todas las dependencias opcionales también están instaladas")
        
        return True
    else:
        print(f"\n⚠️ INSTALACIÓN PARCIAL")
        print(f"Faltan {len(required_failed)} dependencias requeridas")
        print("El sistema funcionará con funcionalidad limitada")
        
        return False

def create_requirements_file():
    """Crea archivo requirements.txt actualizado."""
    
    requirements_content = """# Dependencias requeridas - Rexus.app
PyQt6>=6.5.0
PyQt6-WebEngine>=6.5.0
requests>=2.31.0
pandas>=2.0.0
openpyxl>=3.1.0
Pillow>=10.0.0
pyodbc>=4.0.0
cryptography>=41.0.0
qrcode>=7.4.0
reportlab>=4.0.0

# Dependencias opcionales
psutil>=5.9.0
schedule>=1.2.0
matplotlib>=3.7.0
plotly>=5.15.0

# Testing
pytest>=7.4.0
pytest-qt>=4.2.0
pytest-mock>=3.11.0
pytest-cov>=4.1.0
"""
    
    try:
        with open('requirements.txt', 'w', encoding='utf-8') as f:
            f.write(requirements_content)
        logger.info("✅ Archivo requirements.txt actualizado")
    except Exception as e:
        logger.error(f"❌ Error creando requirements.txt: {e}")

def main():
    """Función principal del instalador."""
    
    print("Verificando dependencias del sistema...")
    
    # Crear archivo requirements.txt
    create_requirements_file()
    
    # Instalar dependencias
    success = install_dependencies()
    
    if success:
        print("\n🚀 El sistema está listo para ejecutarse")
        print("Puedes ejecutar: python main.py")
    else:
        print("\n🔧 Algunas dependencias no se pudieron instalar")
        print("Revisa los errores arriba e instala manualmente si es necesario")
        print("\nComandos sugeridos:")
        print("pip install PyQt6-WebEngine")
        print("pip install -r requirements.txt")
    
    return success

if __name__ == '__main__':
    main()