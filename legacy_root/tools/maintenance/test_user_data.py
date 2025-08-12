#!/usr/bin/env python3
"""
Verificar datos completos del usuario
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Configurar path del proyecto
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Cargar variables de entorno
load_dotenv()

def test_user_data():
    """Verificar datos completos del usuario"""
    print("VERIFICACION DE DATOS COMPLETOS DEL USUARIO")
    print("=" * 50)
    
    try:
        from src.core.auth import get_auth_manager
        
        auth_manager = get_auth_manager()
        user_data = auth_manager.authenticate_user("admin", "admin")
        
        if user_data:
            print("Datos del usuario autenticado:")
            for key, value in user_data.items():
                print(f"  {key}: {value}")
            
            # Verificar campos específicos
            required_fields = ['id', 'username', 'role', 'nombre', 'apellido', 'nombre_completo', 'email']
            missing_fields = [field for field in required_fields if field not in user_data]
            
            if missing_fields:
                print(f"\nCampos faltantes: {missing_fields}")
            else:
                print(f"\nTodos los campos requeridos estan presentes")
                
            return True
        else:
            print("ERROR: No se pudo autenticar usuario")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_user_data()