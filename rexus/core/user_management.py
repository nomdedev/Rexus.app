#!/usr/bin/env python3
"""
Sistema de Gestión de Usuarios Completo - Rexus.app
Incluye autenticación, autorización, gestión de roles y edge cases
"""

import hashlib
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from rexus.core.auth_manager import Permission, UserRole
from rexus.core.database import get_users_connection


class UserManagementSystem:
    """Sistema completo de gestión de usuarios con todas las validaciones"""

    # Configuración de seguridad
    MIN_PASSWORD_LENGTH = 8
    MAX_LOGIN_ATTEMPTS = 3
    LOCKOUT_DURATION_MINUTES = 15
    PASSWORD_EXPIRY_DAYS = 90

    # Roles protegidos que no se pueden cambiar
    PROTECTED_USERS = ["admin"]

    @staticmethod
    def validate_password(password: str) -> Tuple[bool, List[str]]:
        """Valida que la contraseña cumpla con los requisitos de seguridad"""
        errors = []

        if len(password) < UserManagementSystem.MIN_PASSWORD_LENGTH:
            errors.append(
                f"La contraseña debe tener al menos {UserManagementSystem.MIN_PASSWORD_LENGTH} caracteres"
            )

        if not re.search(r"[A-Z]", password):
            errors.append("La contraseña debe contener al menos una letra mayúscula")

        if not re.search(r"[a-z]", password):
            errors.append("La contraseña debe contener al menos una letra minúscula")

        if not re.search(r"[0-9]", password):
            errors.append("La contraseña debe contener al menos un número")

        if not re.search(r"[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]", password):
            errors.append("La contraseña debe contener al menos un carácter especial")

        return len(errors) == 0, errors

    @staticmethod
    def validate_username(username: str) -> Tuple[bool, List[str]]:
        """Valida que el nombre de usuario cumpla con los requisitos"""
        errors = []

        if not username or len(username.strip()) == 0:
            errors.append("El nombre de usuario es obligatorio")

        if len(username) < 3:
            errors.append("El nombre de usuario debe tener al menos 3 caracteres")

        if len(username) > 50:
            errors.append("El nombre de usuario no puede exceder 50 caracteres")

        if not re.match(r"^[a-zA-Z0-9_]+$", username):
            errors.append(
                "El nombre de usuario solo puede contener letras, números y guiones bajos"
            )

        return len(errors) == 0, errors

    @staticmethod
    def validate_email(email: str) -> Tuple[bool, List[str]]:
        """Valida que el email tenga formato correcto"""
        errors = []

        if not email or len(email.strip()) == 0:
            errors.append("El email es obligatorio")
            return False, errors

        # Validar longitud máxima (RFC 5321 especifica 320 caracteres como máximo)
        if len(email) > 320:
            errors.append("El email no puede exceder 320 caracteres")

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            errors.append("El formato del email no es válido")

        return len(errors) == 0, errors

    @staticmethod
    def hash_password(password: str) -> str:
        """Genera hash seguro de la contraseña"""
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    @staticmethod
    def create_user(
        username: str, password: str, email: str, nombre: str, apellido: str, rol: str
    ) -> Tuple[bool, str]:
        """Crea un nuevo usuario con todas las validaciones"""
        try:
            # Validaciones
            valid_user, user_errors = UserManagementSystem.validate_username(username)
            if not valid_user:
                return False, f"Error en nombre de usuario: {', '.join(user_errors)}"

            valid_pass, pass_errors = UserManagementSystem.validate_password(password)
            if not valid_pass:
                return False, f"Error en contraseña: {', '.join(pass_errors)}"

            valid_email, email_errors = UserManagementSystem.validate_email(email)
            if not valid_email:
                return False, f"Error en email: {', '.join(email_errors)}"

            # Validar rol
            valid_roles = ["ADMIN", "MANAGER", "USER", "VIEWER"]
            if rol.upper() not in valid_roles:
                return False, f"Rol inválido. Roles válidos: {', '.join(valid_roles)}"

            # Conectar a base de datos
            db = get_users_connection()
            if not db.connection:
                return False, "Error: No se pudo conectar a la base de datos"

            # Verificar que no exista el usuario
            existing = db.execute_query(
                """
                SELECT COUNT(*) FROM usuarios 
                WHERE usuario = ? OR email = ?
            """,
                (username, email),
            )

            if existing and existing[0][0] > 0:
                return False, "Ya existe un usuario con ese nombre o email"

            # Crear usuario
            password_hash = UserManagementSystem.hash_password(password)

            result = db.execute_non_query(
                """
                INSERT INTO usuarios (usuario, password_hash, email, nombre, apellido, rol, estado, fecha_creacion)
                VALUES (?, ?, ?, ?, ?, ?, 'activo', GETDATE())
            """,
                (username, password_hash, email, nombre, apellido, rol.upper()),
            )

            if result:
                return True, f"Usuario '{username}' creado exitosamente"
            else:
                return False, "Error al crear el usuario en la base de datos"

        except Exception as e:
            return False, f"Error interno: {str(e)}"

    @staticmethod
    def update_user(username: str, data: Dict, current_user: str) -> Tuple[bool, str]:
        """Actualiza un usuario con validaciones de seguridad"""
        try:
            # Verificar que el usuario admin no puede ser modificado por otros
            if username.lower() == "admin" and current_user.lower() != "admin":
                return False, "Solo el administrador puede modificar la cuenta admin"

            # Si se está cambiando el rol del admin, debe ser solo por el mismo admin
            if (
                username.lower() == "admin"
                and "rol" in data
                and current_user.lower() != "admin"
            ):
                return False, "El rol del administrador no puede ser cambiado"

            # Conectar a base de datos
            db = get_users_connection()
            if not db.connection:
                return False, "Error: No se pudo conectar a la base de datos"

            # Verificar que el usuario existe
            user_check = db.execute_query(
                """
                SELECT usuario, rol FROM usuarios WHERE usuario = ?
            """,
                (username,),
            )

            if not user_check:
                return False, f"Usuario '{username}' no encontrado"

            current_role = user_check[0][1]

            # Construir query de actualización
            updates = []
            params = []

            if "email" in data:
                valid_email, email_errors = UserManagementSystem.validate_email(
                    data["email"]
                )
                if not valid_email:
                    return False, f"Error en email: {', '.join(email_errors)}"
                updates.append("email = ?")
                params.append(data["email"])

            if "nombre" in data:
                if not data["nombre"] or len(data["nombre"].strip()) == 0:
                    return False, "El nombre es obligatorio"
                updates.append("nombre = ?")
                params.append(data["nombre"])

            if "apellido" in data:
                updates.append("apellido = ?")
                params.append(data["apellido"])

            if "rol" in data:
                # Validación especial para rol de admin
                if username.lower() == "admin" and data["rol"].upper() != "ADMIN":
                    return False, "El rol del usuario admin no puede ser cambiado"

                valid_roles = ["ADMIN", "MANAGER", "USER", "VIEWER"]
                if data["rol"].upper() not in valid_roles:
                    return (
                        False,
                        f"Rol inválido. Roles válidos: {', '.join(valid_roles)}",
                    )

                updates.append("rol = ?")
                params.append(data["rol"].upper())

            if "estado" in data:
                # El admin no puede ser desactivado
                if username.lower() == "admin" and data["estado"].lower() != "activo":
                    return False, "El usuario admin no puede ser desactivado"

                valid_states = ["activo", "inactivo", "suspendido"]
                if data["estado"].lower() not in valid_states:
                    return (
                        False,
                        f"Estado inválido. Estados válidos: {', '.join(valid_states)}",
                    )

                updates.append("estado = ?")
                params.append(data["estado"].lower())

            if not updates:
                return False, "No hay datos para actualizar"

            # Ejecutar actualización
            params.append(username)
            query = f"UPDATE usuarios SET {', '.join(updates)} WHERE usuario = ?"

            result = db.execute_non_query(query, params)

            if result:
                return True, f"Usuario '{username}' actualizado exitosamente"
            else:
                return False, "Error al actualizar el usuario"

        except Exception as e:
            return False, f"Error interno: {str(e)}"

    @staticmethod
    def change_password(
        username: str, old_password: str, new_password: str, current_user: str
    ) -> Tuple[bool, str]:
        """Cambia la contraseña de un usuario con validaciones"""
        try:
            # Solo el mismo usuario o admin puede cambiar contraseñas
            if username != current_user and current_user.lower() != "admin":
                return False, "Solo puedes cambiar tu propia contraseña"

            # Validar nueva contraseña
            valid_pass, pass_errors = UserManagementSystem.validate_password(
                new_password
            )
            if not valid_pass:
                return False, f"Error en nueva contraseña: {', '.join(pass_errors)}"

            # Conectar a base de datos
            db = get_users_connection()
            if not db.connection:
                return False, "Error: No se pudo conectar a la base de datos"

            # Si no es admin, verificar contraseña actual
            if current_user.lower() != "admin":
                user_data = db.execute_query(
                    """
                    SELECT password_hash FROM usuarios WHERE usuario = ?
                """,
                    (username,),
                )

                if not user_data:
                    return False, "Usuario no encontrado"

                old_hash = UserManagementSystem.hash_password(old_password)
                if old_hash != user_data[0][0]:
                    return False, "Contraseña actual incorrecta"

            # Actualizar contraseña
            new_hash = UserManagementSystem.hash_password(new_password)

            result = db.execute_non_query(
                """
                UPDATE usuarios 
                SET password_hash = ?, fecha_cambio_password = GETDATE()
                WHERE usuario = ?
            """,
                (new_hash, username),
            )

            if result:
                return True, f"Contraseña de '{username}' actualizada exitosamente"
            else:
                return False, "Error al actualizar la contraseña"

        except Exception as e:
            return False, f"Error interno: {str(e)}"

    @staticmethod
    def delete_user(username: str, current_user: str) -> Tuple[bool, str]:
        """Elimina un usuario (soft delete) con validaciones"""
        try:
            # El usuario admin no puede ser eliminado
            if username.lower() == "admin":
                return False, "El usuario admin no puede ser eliminado"

            # Solo admin puede eliminar usuarios
            if current_user.lower() != "admin":
                return False, "Solo el administrador puede eliminar usuarios"

            # Conectar a base de datos
            db = get_users_connection()
            if not db.connection:
                return False, "Error: No se pudo conectar a la base de datos"

            # Verificar que el usuario existe
            user_check = db.execute_query(
                """
                SELECT usuario FROM usuarios WHERE usuario = ?
            """,
                (username,),
            )

            if not user_check:
                return False, f"Usuario '{username}' no encontrado"

            # Soft delete (cambiar estado a eliminado)
            result = db.execute_non_query(
                """
                UPDATE usuarios 
                SET estado = 'eliminado', fecha_eliminacion = GETDATE()
                WHERE usuario = ?
            """,
                (username,),
            )

            if result:
                return True, f"Usuario '{username}' eliminado exitosamente"
            else:
                return False, "Error al eliminar el usuario"

        except Exception as e:
            return False, f"Error interno: {str(e)}"

    @staticmethod
    def list_users(include_inactive: bool = False) -> List[Dict]:
        """Lista todos los usuarios del sistema"""
        try:
            db = get_users_connection()
            if not db.connection:
                return []

            where_clause = "WHERE estado != 'eliminado'"
            if not include_inactive:
                where_clause += " AND estado = 'activo'"

            users = db.execute_query(f"""
                SELECT usuario, email, nombre, apellido, rol, estado, 
                       fecha_creacion, ultima_conexion
                FROM usuarios
                {where_clause}
                ORDER BY fecha_creacion DESC
            """)

            return [
                {
                    "usuario": user[0],
                    "email": user[1],
                    "nombre": user[2],
                    "apellido": user[3],
                    "rol": user[4],
                    "estado": user[5],
                    "fecha_creacion": user[6],
                    "ultima_conexion": user[7],
                }
                for user in (users or [])
            ]

        except Exception as e:
            print(f"Error listando usuarios: {e}")
            return []


if __name__ == "__main__":
    print("Sistema de Gestión de Usuarios - Rexus.app")
    print("Este módulo contiene todas las funciones de gestión de usuarios")
