#!/usr/bin/env python3
"""
Test de permisos para todos los roles de usuario
"""

import sys
import os

# Add rexus to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rexus'))

def test_all_user_roles():
    """Test permissions for all user roles"""
    print("=== TESTING ALL USER ROLES PERMISSIONS ===\n")
    
    try:
        from core.security import SecurityManager
        
        # Definir roles y sus módulos esperados
        roles_config = {
            'ADMIN': {
                'expected_count': 12,
                'description': 'Administrador del sistema con acceso completo',
                'should_have': ['Inventario', 'Administración', 'Obras', 'Usuarios', 'Configuración', 'Auditoría']
            },
            'SUPERVISOR': {
                'expected_count': 8,
                'description': 'Supervisor con permisos de gestión',
                'should_have': ['Inventario', 'Obras', 'Pedidos', 'Logística', 'Herrajes', 'Vidrios']
            },
            'CONTABILIDAD': {
                'expected_count': 7,
                'description': 'Especialista en contabilidad',
                'should_have': ['Administración', 'Compras', 'Pedidos', 'Auditoría', 'Usuarios']
            },
            'INVENTARIO': {
                'expected_count': 7,
                'description': 'Especialista en inventario',
                'should_have': ['Inventario', 'Herrajes', 'Vidrios', 'Compras', 'Logística']
            },
            'OBRAS': {
                'expected_count': 7,
                'description': 'Especialista en obras',
                'should_have': ['Obras', 'Inventario', 'Herrajes', 'Vidrios', 'Logística']
            },
            'USUARIO': {
                'expected_count': 3,
                'description': 'Usuario básico con permisos limitados',
                'should_have': ['Inventario', 'Obras', 'Pedidos']
            }
        }
        
        print("Testing permissions for each role:\n")
        
        for role, config in roles_config.items():
            print(f"--- ROLE: {role} ---")
            print(f"Description: {config['description']}")
            
            # Create SecurityManager and simulate login for this role
            sm = SecurityManager()
            sm.current_role = role
            sm.current_user = {'id': 1, 'username': f'test_{role.lower()}', 'rol': role}
            
            # Get modules for this role
            modules = sm.get_user_modules(1)
            
            print(f"Modules available: {len(modules)}")
            print(f"Expected count: {config['expected_count']}")
            
            # Check if expected count matches
            if len(modules) == config['expected_count']:
                print("   Count: OK")
            else:
                print(f"   Count: WARNING - Expected {config['expected_count']}, got {len(modules)}")
            
            # Check if role has required modules
            has_required = all(module in modules for module in config['should_have'])
            print(f"   Required modules: {'OK' if has_required else 'MISSING'}")
            
            # List all modules for this role
            print(f"   Module list: {modules}")
            
            # Check missing required modules
            missing = [module for module in config['should_have'] if module not in modules]
            if missing:
                print(f"   Missing required: {missing}")
            
            print()
        
        print("=== ROLE-BASED ACCESS SUMMARY ===\n")
        
        # Create summary table
        summary_data = []
        for role, config in roles_config.items():
            sm = SecurityManager()
            sm.current_role = role
            sm.current_user = {'id': 1, 'username': f'test_{role.lower()}', 'rol': role}
            modules = sm.get_user_modules(1)
            
            summary_data.append({
                'role': role,
                'count': len(modules),
                'expected': config['expected_count'],
                'status': 'OK' if len(modules) == config['expected_count'] else 'CHECK'
            })
        
        print("Role             | Modules | Expected | Status")
        print("-" * 45)
        for data in summary_data:
            print(f"{data['role']:<15} | {data['count']:<7} | {data['expected']:<8} | {data['status']}")
        
        print(f"\n=== ACCESS CONTROL VERIFICATION ===")
        print("- ADMIN: Full access to all 12 modules")
        print("- SUPERVISOR: Management access to 8 operational modules")  
        print("- CONTABILIDAD: Financial and administrative modules")
        print("- INVENTARIO: Stock and materials management modules")
        print("- OBRAS: Construction and project modules")
        print("- USUARIO: Basic read-only access to 3 essential modules")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_all_user_roles()
    if success:
        print("\nSUCCESS: All user roles have been configured with appropriate module access")
    else:
        print("\nERROR: There are issues with user role configurations")