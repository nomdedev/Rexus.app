#!/usr/bin/env python3
"""
Script simple para verificar problemas comunes en módulos sin PyQt6.
"""

import sys
import os
from pathlib import Path

# Configurar entorno
root_dir = Path(__file__).parent
os.chdir(root_dir)
sys.path.insert(0, str(root_dir))

def check_basic_imports():
    """Verifica que las importaciones básicas funcionen."""
    print("=== VERIFICACION DE IMPORTACIONES BASICAS ===")
    
    modulos_a_verificar = [
        ('rexus.modules.inventario.model', 'InventarioModel'),
        ('rexus.modules.inventario.controller', 'InventarioController'),
        ('rexus.modules.herrajes.model', 'HerrajesModel'),
        ('rexus.modules.herrajes.controller', 'HerrajesController'),
        ('rexus.modules.configuracion.model', 'ConfiguracionModel'),
        ('rexus.modules.configuracion.controller', 'ConfiguracionController'),
        ('rexus.modules.obras.model', 'ObrasModel'),
        ('rexus.modules.obras.controller', 'ObrasController'),
    ]
    
    for modulo, clase in modulos_a_verificar:
        try:
            print(f"Verificando {modulo}.{clase}...", end=" ")
            mod = __import__(modulo, fromlist=[clase])
            getattr(mod, clase)
            print("OK")
        except Exception as e:
            print(f"ERROR: {e}")

def check_model_instantiation():
    """Verifica que los modelos se puedan instanciar."""
    print("\\n=== VERIFICACION DE INSTANCIACION DE MODELOS ===")
    
    try:
        from rexus.modules.inventario.model import InventarioModel
        model = InventarioModel()
        print("InventarioModel: OK")
    except Exception as e:
        print(f"InventarioModel: ERROR - {e}")
    
    try:
        from rexus.modules.herrajes.model import HerrajesModel
        model = HerrajesModel()
        print("HerrajesModel: OK")
    except Exception as e:
        print(f"HerrajesModel: ERROR - {e}")
    
    try:
        from rexus.modules.configuracion.model import ConfiguracionModel
        model = ConfiguracionModel()
        print("ConfiguracionModel: OK")
    except Exception as e:
        print(f"ConfiguracionModel: ERROR - {e}")
    
    try:
        from rexus.modules.obras.model import ObrasModel
        model = ObrasModel()
        print("ObrasModel: OK")
    except Exception as e:
        print(f"ObrasModel: ERROR - {e}")

def check_controller_instantiation():
    """Verifica que los controladores se puedan instanciar."""
    print("\\n=== VERIFICACION DE INSTANCIACION DE CONTROLADORES ===")
    
    # Crear modelos mock para los controladores
    try:
        from rexus.modules.inventario.model import InventarioModel
        from rexus.modules.inventario.controller import InventarioController
        
        model = InventarioModel()
        # Los controladores necesitan una vista, pero podemos usar None para la prueba
        controller = InventarioController(model, None)
        print("InventarioController: OK")
    except Exception as e:
        print(f"InventarioController: ERROR - {e}")
    
    try:
        from rexus.modules.herrajes.model import HerrajesModel
        from rexus.modules.herrajes.controller import HerrajesController
        
        model = HerrajesModel()
        controller = HerrajesController(model, None)
        print("HerrajesController: OK")
    except Exception as e:
        print(f"HerrajesController: ERROR - {e}")
    
    try:
        from rexus.modules.configuracion.model import ConfiguracionModel
        from rexus.modules.configuracion.controller import ConfiguracionController
        
        model = ConfiguracionModel()
        controller = ConfiguracionController(model, None)
        print("ConfiguracionController: OK")
    except Exception as e:
        print(f"ConfiguracionController: ERROR - {e}")

def check_database_connection():
    """Verifica la conectividad de base de datos."""
    print("\\n=== VERIFICACION DE CONEXION A BASE DE DATOS ===")
    
    # Cargar variables de entorno
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("Variables de entorno cargadas")
    except ImportError:
        print("WARNING: python-dotenv no instalado")
    
    try:
        from rexus.core.database import validate_environment, InventarioDatabaseConnection
        
        if validate_environment():
            print("Variables de entorno: OK")
            
            try:
                db_conn = InventarioDatabaseConnection()
                if db_conn.connect():
                    print("Conexion BD: OK")
                    db_conn.close()
                else:
                    print("Conexion BD: FALLO - No se pudo conectar")
            except Exception as e:
                print(f"Conexion BD: ERROR - {e}")
        else:
            print("Variables de entorno: FALTANTES - Modo demo")
            
    except Exception as e:
        print(f"Error verificando BD: {e}")

if __name__ == "__main__":
    check_basic_imports()
    check_model_instantiation()
    check_controller_instantiation()
    check_database_connection()
    
    print("\\n=== VERIFICACION COMPLETADA ===")
    print("Si todos los componentes muestran 'OK', el problema podria estar")
    print("en la inicializacion de PyQt6 o en el widget de vista específico.")