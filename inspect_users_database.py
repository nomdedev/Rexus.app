#!/usr/bin/env python3
"""
Inspección de la base de datos 'users' para revisar tablas y permisos
"""

import sys
import os

# Add rexus to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rexus'))

def inspect_users_database():
    """Inspect the users database structure and permissions"""
    print("=== INSPECCION DE BASE DE DATOS 'USERS' ===\n")
    
    try:
        from core.database import UsersDatabaseConnection
        
        print("1. Conectando a la base de datos 'users'...")
        db = UsersDatabaseConnection()
        if not db.connect():
            print("   ERROR: No se pudo conectar a la base de datos")
            return False
        
        print("   Conexion exitosa a la BD 'users'")
        cursor = db.cursor()
        
        print("\n2. Listando todas las tablas...")
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE' 
            ORDER BY TABLE_NAME
        """)
        
        tables = cursor.fetchall()
        print(f"   Tablas encontradas: {len(tables)}")
        
        for table in tables:
            table_name = table[0]
            print(f"   - {table_name}")
        
        print("\n3. Inspeccionando estructura de cada tabla...")
        
        for table in tables:
            table_name = table[0]
            print(f"\n--- TABLA: {table_name} ---")
            
            # Get table structure
            cursor.execute(f"""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = '{table_name}'
                ORDER BY ORDINAL_POSITION
            """)
            
            columns = cursor.fetchall()
            print("   Estructura:")
            for col in columns:
                col_name, data_type, nullable, default = col
                nullable_str = "NULL" if nullable == "YES" else "NOT NULL"
                default_str = f" DEFAULT {default}" if default else ""
                print(f"     {col_name:<20} {data_type:<15} {nullable_str}{default_str}")
            
            # Get row count
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"   Registros: {count}")
                
                # Show sample data for important tables
                if table_name.lower() in ['usuarios', 'roles', 'permisos'] and count > 0:
                    cursor.execute(f"SELECT TOP 5 * FROM {table_name}")
                    rows = cursor.fetchall()
                    col_names = [desc[0] for desc in cursor.description]
                    
                    print("   Datos de ejemplo:")
                    for row in rows:
                        row_data = dict(zip(col_names, row))
                        # Hide password hashes
                        if 'password' in row_data:
                            row_data['password'] = '[HASH_OCULTO]'
                        print(f"     {row_data}")
                        
            except Exception as e:
                print(f"   Error obteniendo datos: {e}")
        
        print("\n4. Analizando sistema de permisos...")
        
        # Check if permissions tables exist
        permission_tables = ['roles', 'permisos', 'rol_permisos']
        existing_perm_tables = [t[0] for t in tables if t[0].lower() in permission_tables]
        
        if existing_perm_tables:
            print(f"   Tablas de permisos encontradas: {existing_perm_tables}")
            
            # Analyze roles
            if 'roles' in [t.lower() for t in existing_perm_tables]:
                print("\n   --- ROLES DISPONIBLES ---")
                cursor.execute("SELECT nombre, descripcion, activo FROM roles ORDER BY nombre")
                roles = cursor.fetchall()
                for role in roles:
                    nombre, desc, activo = role
                    status = "ACTIVO" if activo else "INACTIVO"
                    print(f"     {nombre:<15} | {desc or 'Sin descripcion':<40} | {status}")
            
            # Analyze permissions
            if 'permisos' in [t.lower() for t in existing_perm_tables]:
                print("\n   --- PERMISOS DISPONIBLES ---")
                cursor.execute("SELECT nombre, modulo, descripcion FROM permisos ORDER BY modulo, nombre")
                permisos = cursor.fetchall()
                
                current_module = None
                for perm in permisos:
                    nombre, modulo, desc = perm
                    if modulo != current_module:
                        print(f"\n     MODULO: {modulo}")
                        current_module = modulo
                    print(f"       - {nombre:<25} | {desc or 'Sin descripcion'}")
            
            # Analyze role-permission assignments
            if 'rol_permisos' in [t.lower() for t in existing_perm_tables]:
                print("\n   --- ASIGNACION DE PERMISOS POR ROL ---")
                cursor.execute("""
                    SELECT r.nombre as rol, COUNT(rp.permiso_id) as total_permisos
                    FROM roles r
                    LEFT JOIN rol_permisos rp ON r.id = rp.rol_id
                    GROUP BY r.nombre
                    ORDER BY total_permisos DESC
                """)
                
                role_perms = cursor.fetchall()
                for role_perm in role_perms:
                    rol, total = role_perm
                    print(f"     {rol:<15} | {total} permisos asignados")
        else:
            print("   No se encontraron tablas de permisos configuradas")
        
        print("\n5. Analizando usuarios...")
        if 'usuarios' in [t[0].lower() for t in tables]:
            cursor.execute("""
                SELECT username, rol, activo, ultimo_login, fecha_creacion
                FROM usuarios 
                ORDER BY fecha_creacion DESC
            """)
            
            usuarios = cursor.fetchall()
            print(f"   Total de usuarios: {len(usuarios)}")
            print("\n   Lista de usuarios:")
            print("   Username         | Rol           | Estado   | Ultimo Login")
            print("   " + "-" * 60)
            
            for user in usuarios:
                username, rol, activo, ultimo_login, fecha_creacion = user
                status = "ACTIVO" if activo else "INACTIVO" 
                ultimo_str = str(ultimo_login)[:19] if ultimo_login else "Nunca"
                print(f"   {username:<15} | {rol:<12} | {status:<8} | {ultimo_str}")
        
        db.disconnect()
        print("\n=== INSPECCION COMPLETADA ===")
        return True
        
    except Exception as e:
        print(f"ERROR durante la inspeccion: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = inspect_users_database()
    if success:
        print("\nInspeccion de base de datos completada exitosamente")
    else:
        print("\nHubo errores durante la inspeccion")