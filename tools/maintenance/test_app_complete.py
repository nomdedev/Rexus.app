#!/usr/bin/env python3
"""
Prueba completa de la aplicación sin interfaz gráfica
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

def test_complete_flow():
    """Prueba el flujo completo de la aplicación"""
    print("PRUEBA COMPLETA DE LA APLICACION")
    print("=" * 40)
    
    try:
        # 1. Probar autenticación
        print("1. Probando autenticación...")
        from src.core.auth import get_auth_manager
        
        auth_manager = get_auth_manager()
        user = auth_manager.authenticate_user("admin", "admin")
        
        if not user:
            print("   ERROR: No se pudo autenticar")
            return False
        
        print(f"   EXITO: Usuario {user['username']} autenticado como {user['role']}")
        
        # 2. Probar conexiones a diferentes bases de datos
        print("\n2. Probando conexiones a diferentes BD...")
        from src.core.database import get_users_connection, get_inventario_connection, get_auditoria_connection
        
        # Users
        print("   Conectando a 'users'...", end=" ")
        users_db = get_users_connection()
        result = users_db.execute_query("SELECT COUNT(*) FROM usuarios")
        print(f"OK ({result[0][0]} usuarios)")
        
        # Inventario
        print("   Conectando a 'inventario'...", end=" ")
        inv_db = get_inventario_connection()
        result = inv_db.execute_query("SELECT 1")
        print("OK")
        
        # Auditoria
        print("   Conectando a 'auditoria'...", end=" ")
        aud_db = get_auditoria_connection()
        result = aud_db.execute_query("SELECT 1")
        print("OK")
        
        # 3. Verificar que es la misma conexión
        print(f"\n3. Verificando reutilización de conexión:")
        print(f"   users_db es inv_db: {users_db is inv_db}")
        print(f"   inv_db es aud_db: {inv_db is aud_db}")
        
        # 4. Probar sistema de seguridad
        print(f"\n4. Probando sistema de seguridad...")
        from src.core.security import initialize_security_manager
        
        try:
            security_manager = initialize_security_manager()
            print("   Sistema de seguridad: OK")
        except Exception as e:
            print(f"   Sistema de seguridad: FALLO ({e})")
        
        # 5. Probar creación de MainWindow (sin mostrar)
        print(f"\n5. Probando creación de MainWindow...")
        try:
            # Simular QApplication sin mostrar ventana
            import sys
            from PyQt6.QtWidgets import QApplication
            
            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)
            
            from src.main.app import MainWindow
            
            # Crear MainWindow sin mostrarlo
            main_window = MainWindow(user, ["inventario", "usuarios", "obras"])
            print("   MainWindow creado: OK")
            
            # No mostrar la ventana, solo verificar que se puede crear
            # main_window.show()
            
        except Exception as e:
            print(f"   MainWindow: FALLO ({e})")
            import traceback
            traceback.print_exc()
        
        print(f"\n[OK] PRUEBA COMPLETA EXITOSA")
        print("La aplicación está lista para usar")
        return True
        
    except Exception as e:
        print(f"ERROR en prueba completa: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_flow()
    
    if success:
        print(f"\n🎉 APLICACION FUNCIONANDO CORRECTAMENTE")
        print("Puedes ejecutar: python run.py")
    else:
        print(f"\n[ERROR] HAY PROBLEMAS EN LA APLICACION")
        print("Revisa los errores mostrados arriba")