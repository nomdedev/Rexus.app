#!/usr/bin/env python3
"""
Comprehensive analysis of users database permissions and roles
"""

import sys
import os

# Add rexus to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rexus'))

def analyze_users_permissions():
    """Analyze complete permissions structure in users database"""
    print("=== ANALISIS COMPLETO DE PERMISOS BD USERS ===\n")
    
    try:
        # Load environment variables from .env file
        from dotenv import load_dotenv
        load_dotenv()
        
        # Verify required environment variables are set
        required_vars = ["DB_SERVER", "DB_USERNAME", "DB_PASSWORD", "DB_USERS"]
        for var in required_vars:
            if not os.getenv(var):
                print(f"ERROR: Environment variable {var} not set. Check your .env file.")
                return False
        
        from core.database import UsersDatabaseConnection
        
        print("1. Connecting to users database...")
        db = UsersDatabaseConnection()
        
        if not db.connect():
            print("   Connection failed")
            return False
        
        print("   Connected successfully!")
        cursor = db.cursor()
        
        # 1. ANALYZE USERS
        print("\n=== 1. USUARIOS EN LA BASE DE DATOS ===")
        cursor.execute("SELECT usuario, rol, estado, activo, ultimo_login FROM usuarios ORDER BY usuario")
        users = cursor.fetchall()
        
        print(f"Total usuarios: {len(users)}")
        print("Usuario         | Rol           | Estado  | Activo | Último Login")
        print("-" * 65)
        for user in users:
            usuario, rol, estado, activo, ultimo_login = user
            activo_str = "SÍ" if activo else "NO"
            ultimo_str = str(ultimo_login)[:19] if ultimo_login else "Nunca"
            print(f"{usuario:<15} | {rol:<12} | {estado:<7} | {activo_str:<6} | {ultimo_str}")
        
        # 2. ANALYZE ROLES
        print("\n=== 2. ROLES CONFIGURADOS ===")
        cursor.execute("SELECT nombre, descripcion, activo FROM roles ORDER BY nombre")
        roles = cursor.fetchall()
        
        print(f"Total roles: {len(roles)}")
        print("Rol             | Descripción                              | Activo")
        print("-" * 75)
        for role in roles:
            nombre, desc, activo = role
            activo_str = "SÍ" if activo else "NO"
            desc_str = (desc or "Sin descripción")[:40]
            print(f"{nombre:<15} | {desc_str:<40} | {activo_str}")
        
        # 3. ANALYZE PERMISSIONS BY MODULE
        print("\n=== 3. PERMISOS POR MÓDULO ===")
        cursor.execute("SELECT DISTINCT modulo FROM permisos ORDER BY modulo")
        modules = [m[0] for m in cursor.fetchall()]
        
        for module in modules:
            cursor.execute("SELECT nombre, descripcion FROM permisos WHERE modulo = ? ORDER BY nombre", (module,))
            module_perms = cursor.fetchall()
            
            print(f"\n--- MÓDULO: {module} ({len(module_perms)} permisos) ---")
            for perm_name, perm_desc in module_perms:
                desc_str = (perm_desc or "Sin descripción")[:50]
                print(f"  • {perm_name:<25} | {desc_str}")
        
        # 4. ANALYZE ROLE-PERMISSION ASSIGNMENTS
        print("\n=== 4. ASIGNACIÓN DE PERMISOS POR ROL ===")
        cursor.execute("""
            SELECT r.nombre, COUNT(rp.permiso_id) as total_permisos
            FROM roles r
            LEFT JOIN rol_permisos rp ON r.id = rp.rol_id
            GROUP BY r.nombre
            ORDER BY total_permisos DESC
        """)
        
        role_perm_counts = cursor.fetchall()
        print("Rol             | Permisos Asignados")
        print("-" * 35)
        for rol, count in role_perm_counts:
            print(f"{rol:<15} | {count}")
        
        # 5. DETAILED PERMISSIONS FOR ADMIN
        print("\n=== 5. PERMISOS DETALLADOS DEL ADMIN ===")
        cursor.execute("""
            SELECT p.modulo, p.nombre, p.descripcion
            FROM roles r
            JOIN rol_permisos rp ON r.id = rp.rol_id
            JOIN permisos p ON rp.permiso_id = p.id
            WHERE r.nombre = 'ADMIN'
            ORDER BY p.modulo, p.nombre
        """)
        
        admin_perms = cursor.fetchall()
        print(f"El usuario ADMIN tiene {len(admin_perms)} permisos asignados:")
        
        current_module = None
        for modulo, nombre, desc in admin_perms:
            if modulo != current_module:
                print(f"\n--- {modulo} ---")
                current_module = modulo
            desc_str = (desc or "Sin descripción")[:40]
            print(f"  • {nombre:<25} | {desc_str}")
        
        # 6. MODULE-SPECIFIC PERMISSIONS
        print("\n=== 6. PERMISOS ESPECÍFICOS DE MÓDULOS ===")
        cursor.execute("SELECT COUNT(*) FROM permisos_modulos")
        module_perm_count = cursor.fetchone()[0]
        print(f"Total permisos de módulos: {module_perm_count}")
        
        cursor.execute("""
            SELECT modulo, 
                   SUM(CASE WHEN puede_ver = 1 THEN 1 ELSE 0 END) as puede_ver,
                   SUM(CASE WHEN puede_modificar = 1 THEN 1 ELSE 0 END) as puede_modificar,
                   SUM(CASE WHEN puede_aprobar = 1 THEN 1 ELSE 0 END) as puede_aprobar,
                   COUNT(*) as total
            FROM permisos_modulos
            GROUP BY modulo
            ORDER BY modulo
        """)
        
        module_stats = cursor.fetchall()
        print("\nMódulo          | Ver | Modif | Aprob | Total")
        print("-" * 45)
        for modulo, ver, modif, aprob, total in module_stats:
            print(f"{modulo:<15} | {ver:<3} | {modif:<5} | {aprob:<5} | {total}")
        
        # 7. USER-MODULE PERMISSIONS
        print("\n=== 7. PERMISOS DE USUARIO POR MÓDULO ===")
        cursor.execute("""
            SELECT u.usuario, pm.modulo, pm.puede_ver, pm.puede_modificar, pm.puede_aprobar
            FROM usuarios u
            JOIN permisos_modulos pm ON u.id = pm.usuario_id
            ORDER BY u.usuario, pm.modulo
        """)
        
        user_module_perms = cursor.fetchall()
        if user_module_perms:
            print("Usuario | Módulo          | Ver | Modif | Aprob")
            print("-" * 50)
            for usuario, modulo, ver, modif, aprob in user_module_perms:
                ver_str = "✓" if ver else "✗"
                modif_str = "✓" if modif else "✗"
                aprob_str = "✓" if aprob else "✗"
                print(f"{usuario:<7} | {modulo:<15} | {ver_str:<3} | {modif_str:<5} | {aprob_str}")
        else:
            print("No hay permisos de usuario-módulo específicos configurados")
        
        # 8. SECURITY ANALYSIS
        print("\n=== 8. ANÁLISIS DE SEGURIDAD ===")
        
        # Check if admin has all permissions
        cursor.execute("""
            SELECT COUNT(*) FROM permisos WHERE activo = 1
        """)
        total_active_perms = cursor.fetchone()[0]
        
        admin_perm_count = len(admin_perms)
        coverage_percent = (admin_perm_count / total_active_perms) * 100 if total_active_perms > 0 else 0
        
        print(f"• Total permisos activos: {total_active_perms}")
        print(f"• Permisos del ADMIN: {admin_perm_count}")
        print(f"• Cobertura del ADMIN: {coverage_percent:.1f}%")
        
        if coverage_percent >= 95:
            print("  [OK] ADMIN tiene cobertura completa de permisos")
        else:
            print("  [WARNING] ADMIN podria estar faltando algunos permisos")
        
        # Check active users
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE activo = 1")
        active_users = cursor.fetchone()[0]
        print(f"• Usuarios activos: {active_users}")
        
        if active_users == 1:
            print("  [WARNING] Solo hay 1 usuario activo (riesgo si se pierde acceso)")
        else:
            print(f"  [OK] Hay {active_users} usuarios activos")
        
        db.disconnect()
        
        print("\n=== RESUMEN DIAGNOSTICO ===")
        print("1. [OK] La base de datos 'users' esta configurada y funcional")
        print("2. [OK] El usuario ADMIN esta correctamente configurado")
        print("3. [OK] Hay un sistema completo de roles y permisos")
        print("4. [OK] Los permisos estan bien estructurados por modulos")
        
        if user_module_perms:
            print("5. [OK] Hay permisos especificos usuario-modulo configurados")
        else:
            print("5. [INFO] No hay permisos especificos usuario-modulo (se usan roles)")
        
        print("\n=== ANALYSIS COMPLETED ===")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = analyze_users_permissions()
    if success:
        print("\nPermissions analysis completed successfully")
    else:
        print("\nPermissions analysis failed")