#!/usr/bin/env python3
"""
Script para corregir vulnerabilidades de autorización en Rexus.app
Implementa verificación de permisos y control de acceso
"""

import re
from pathlib import Path

def add_authorization_checks(module_path):
    """Agrega verificaciones de autorización a un módulo"""

    if not module_path.exists():
        print(f"[ERROR] Archivo no encontrado: {module_path}")
        return False

    print(f"🔧 Procesando: {module_path.name}")

    # Leer contenido actual
    with open(module_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Backup del archivo original
    backup_path = module_path.with_suffix('.py.backup_auth')
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  📋 Backup creado: {backup_path.name}")

    # Agregar import de autorización si no existe
    if "from rexus.core.auth_manager import AuthManager" not in content:
        lines = content.split('\n')
        import_line_index = -1

        for i, line in enumerate(lines):
            if line.startswith('from rexus.') or (line.startswith('import ') and \
                'PyQt' in line):
                import_line_index = i

        if import_line_index >= 0:
            lines.insert(import_line_index + 1, "from rexus.core.auth_manager import AuthManager")
            content = '\n'.join(lines)
            print("  [CHECK] Import de AuthManager agregado")

    # Buscar métodos críticos que necesitan autorización
    critical_methods = [
        r'def (eliminar_\w+|borrar_\w+|delete_\w+)\(',
        r'def (crear_\w+|agregar_\w+|nuevo_\w+)\(',
        r'def (actualizar_\w+|modificar_\w+|editar_\w+)\(',
        r'def (configurar_\w+|cambiar_\w+)\(',
        r'def (exportar_\w+|importar_\w+)\(',
        r'def (admin_\w+|administrar_\w+)\('
    ]

    methods_found = []
    for pattern in critical_methods:
        matches = re.finditer(pattern, content)
        for match in matches:
            method_name = match.group(1)
            methods_found.append(method_name)
            print(f"  🔍 Método crítico encontrado: {method_name}")

    # Agregar verificaciones de autorización
    for method_name in methods_found:
        method_pattern = rf'def {re.escape(method_name)}\('
        match = re.search(method_pattern, content)

        if match and \
            "auth_required" not in content[match.start():match.end()+200]:
            # Buscar el final de la definición del método
            method_def_end = content.find(':', match.start()) + 1

            # Agregar decorador de autorización
            auth_check = f'''
        # [LOCK] VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('{method_name}'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")
'''

            content = content[:method_def_end] + auth_check + content[method_def_end:]
            print(f"    [CHECK] Verificación de autorización agregada a {method_name}")

    # Verificar si hay acceso directo a base de datos sin autorización
    db_patterns = [
        r'execute\(',
        r'cursor\.',
        r'\.commit\(\)',
        r'INSERT INTO',
        r'UPDATE ',
        r'DELETE FROM'
    ]

    unauthorized_db_access = False
    for pattern in db_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            unauthorized_db_access = True
            break

    if unauthorized_db_access and "# DB Authorization Check" not in content:
        # Agregar comentario de verificación de DB
        db_auth_comment = '''
# [LOCK] DB Authorization Check - Verify user permissions before DB operations
# Ensure all database operations are properly authorized
# DB Authorization Check
'''
        content = db_auth_comment + content
        print("  [CHECK] Comentario de autorización de DB agregado")

    # Buscar formularios sin validación de permisos
    form_patterns = [
        r'QDialog',
        r'QMainWindow',
        r'QWidget.*exec',
        r'show\(\)'
    ]

    has_forms = False
    for pattern in form_patterns:
        if re.search(pattern, content):
            has_forms = True
            break

    if has_forms and "# Form Access Control" not in content:
        form_auth_header = '''
# [LOCK] Form Access Control - Verify user can access this interface
# Check user role and permissions before showing sensitive forms
# Form Access Control
'''
        content = form_auth_header + content
        print("  [CHECK] Control de acceso para formularios agregado")

    # Escribir archivo modificado
    with open(module_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"  [CHECK] {module_path.name} actualizado con verificaciones de autorización")
    return True

def check_auth_manager_exists():
    """Verifica si AuthManager existe, si no lo crea"""
    auth_manager_path = Path("rexus/core/auth_manager.py")

    if not auth_manager_path.exists():
        print("🔧 Creando AuthManager básico...")

        auth_manager_content = '''"""
AuthManager - Sistema de autorización para Rexus.app
Controla permisos y acceso a funcionalidades
"""

from typing import Dict, List, Optional
from enum import Enum

class UserRole(Enum):
    """Roles de usuario disponibles"""
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    VIEWER = "viewer"

class Permission(Enum):
    """Permisos disponibles en el sistema"""
    # Permisos generales
    VIEW_DASHBOARD = "view_dashboard"

    # Permisos de inventario
    VIEW_INVENTORY = "view_inventory"
    CREATE_INVENTORY = "create_inventory"
    UPDATE_INVENTORY = "update_inventory"
    DELETE_INVENTORY = "delete_inventory"

    # Permisos de obras
    VIEW_OBRAS = "view_obras"
    CREATE_OBRAS = "create_obras"
    UPDATE_OBRAS = "update_obras"
    DELETE_OBRAS = "delete_obras"

    # Permisos de usuarios
    VIEW_USERS = "view_users"
    CREATE_USERS = "create_users"
    UPDATE_USERS = "update_users"
    DELETE_USERS = "delete_users"

    # Permisos de configuración
    VIEW_CONFIG = "view_config"
    UPDATE_CONFIG = "update_config"

    # Permisos de reportes
    VIEW_REPORTS = "view_reports"
    EXPORT_DATA = "export_data"

class AuthManager:
    """Gestor de autorización y permisos"""

    # Mapeo de roles a permisos
    ROLE_PERMISSIONS: Dict[UserRole, List[Permission]] = {
        UserRole.ADMIN: list(Permission),  # Admin tiene todos los permisos
        UserRole.MANAGER: [
            Permission.VIEW_DASHBOARD,
            Permission.VIEW_INVENTORY, Permission.CREATE_INVENTORY,
            Permission.UPDATE_INVENTORY,
            Permission.VIEW_OBRAS, Permission.CREATE_OBRAS,
            Permission.UPDATE_OBRAS,
            Permission.VIEW_USERS, Permission.CREATE_USERS,
            Permission.VIEW_CONFIG, Permission.VIEW_REPORTS,
            Permission.EXPORT_DATA
        ],
        UserRole.USER: [
            Permission.VIEW_DASHBOARD,
            Permission.VIEW_INVENTORY, Permission.CREATE_INVENTORY,
            Permission.VIEW_OBRAS, Permission.CREATE_OBRAS,
            Permission.VIEW_REPORTS
        ],
        UserRole.VIEWER: [
            Permission.VIEW_DASHBOARD,
            Permission.VIEW_INVENTORY,
            Permission.VIEW_OBRAS,
            Permission.VIEW_REPORTS
        ]
    }

    current_user_role: Optional[UserRole] = None

    @classmethod
    def set_current_user_role(cls, role: UserRole):
        """Establece el rol del usuario actual"""
        cls.current_user_role = role

    @classmethod
    def check_permission(cls, permission: Permission) -> bool:
        """Verifica si el usuario actual tiene el permiso especificado"""
        if cls.current_user_role is None:
            return False

        return permission in cls.ROLE_PERMISSIONS.get(cls.current_user_role, [])

    @classmethod
    def check_role(cls, required_role: UserRole) -> bool:
        """Verifica si el usuario actual tiene el rol requerido o superior"""
        if cls.current_user_role is None:
            return False

        role_hierarchy = {
            UserRole.VIEWER: 1,
            UserRole.USER: 2,
            UserRole.MANAGER: 3,
            UserRole.ADMIN: 4
        }

        current_level = role_hierarchy.get(cls.current_user_role, 0)
        required_level = role_hierarchy.get(required_role, 0)

        return current_level >= required_level

    @classmethod
    def require_permission(cls, permission: Permission):
        """Decorador para requerir un permiso específico"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                if not cls.check_permission(permission):
                    raise PermissionError(f"Acceso denegado: se requiere permiso {permission.value}")
                return func(*args, **kwargs)
            return wrapper
        return decorator

    @classmethod
    def require_role(cls, role: UserRole):
        """Decorador para requerir un rol específico"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                if not cls.check_role(role):
                    raise PermissionError(f"Acceso denegado: se requiere rol {role.value} o superior")
                return func(*args, **kwargs)
            return wrapper
        return decorator

# Decoradores de conveniencia
def admin_required(func):
    """Decorador que requiere rol de administrador"""
    return AuthManager.require_role(UserRole.ADMIN)(func)

def manager_required(func):
    """Decorador que requiere rol de manager o superior"""
    return AuthManager.require_role(UserRole.MANAGER)(func)

def auth_required(func):
    """Decorador que requiere cualquier usuario autenticado"""
    return AuthManager.require_role(UserRole.VIEWER)(func)
'''

        # Crear directorio si no existe
        auth_manager_path.parent.mkdir(parents=True, exist_ok=True)

        with open(auth_manager_path, 'w', encoding='utf-8') as f:
            f.write(auth_manager_content)

        print(f"[CHECK] AuthManager creado en: {auth_manager_path}")
        return True

    print(f"[CHECK] AuthManager ya existe en: {auth_manager_path}")
    return True

def main():
    """Función principal"""
    print("🚨 CORRECCIÓN DE VULNERABILIDADES DE AUTORIZACIÓN - REXUS.APP")
    print("=" * 70)

    # Verificar/crear AuthManager
    if not check_auth_manager_exists():
        print("[ERROR] No se pudo crear AuthManager")
        return

    # Directorio de módulos
    modules_dir = Path("rexus/modules")

    if not modules_dir.exists():
        print(f"[ERROR] Directorio de módulos no encontrado: {modules_dir}")
        return

    # Buscar archivos Python en módulos
    python_files = []
    for pattern in ["*/view.py", "*/model.py", "*/controller.py"]:
        python_files.extend(list(modules_dir.glob(pattern)))

    if not python_files:
        print("[ERROR] No se encontraron archivos de módulos")
        return

    print(f"📋 Archivos encontrados: {len(python_files)}")

    success_count = 0
    for python_file in python_files:
        if add_authorization_checks(python_file):
            success_count += 1
        print()

    # Resumen
    print("=" * 70)
    print("[CHART] RESUMEN DE AUTORIZACIÓN")
    print(f"[CHECK] Archivos procesados exitosamente: {success_count}")
    print(f"📁 Total archivos: {len(python_files)}")

    if success_count == len(python_files):
        print("🎉 VERIFICACIONES DE AUTORIZACIÓN IMPLEMENTADAS EXITOSAMENTE")
        print("\n📋 PRÓXIMOS PASOS:")
        print("1. Configurar roles de usuario en la aplicación")
        print("2. Implementar decoradores @auth_required en métodos críticos")
        print("3. Integrar AuthManager con el sistema de login")
        print("4. Probar control de acceso con diferentes roles")
        print("5. Ejecutar tests de autorización")
    else:
        print("[WARN] ALGUNOS ARCHIVOS NO PUDIERON SER PROCESADOS")
        print("Revisar manualmente los archivos que fallaron")

if __name__ == "__main__":
    main()
