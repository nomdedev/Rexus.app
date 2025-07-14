"""
Modelo de Usuarios - Gestiona la autenticación y permisos de usuarios.
"""

import hashlib
from typing import Any, Dict, List


class UsuariosModel:
    """Modelo para gestión de usuarios y autenticación."""

    def __init__(self, db_connection=None):
        self.db_connection = db_connection
        self.tabla_usuarios = "usuarios"
        self._crear_tabla_si_no_existe()

    def _crear_tabla_si_no_existe(self):
        """Verifica que la tabla de usuarios exista en la base de datos."""
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.connection.cursor()

            # Verificar si la tabla de usuarios existe
            cursor.execute(
                f"SELECT * FROM sysobjects WHERE name='{self.tabla_usuarios}' AND xtype='U'"
            )
            if cursor.fetchone():
                print(
                    f"[USUARIOS] Tabla '{self.tabla_usuarios}' verificada correctamente."
                )

                # Mostrar la estructura de la tabla
                cursor.execute(
                    f"SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{self.tabla_usuarios}'"
                )
                columnas = cursor.fetchall()
                print(f"[USUARIOS] Estructura de tabla '{self.tabla_usuarios}':")
                for columna in columnas:
                    print(f"  - {columna[0]}: {columna[1]}")
            else:
                print(
                    f"[ADVERTENCIA] La tabla '{self.tabla_usuarios}' no existe en la base de datos."
                )

        except Exception as e:
            print(f"[ERROR USUARIOS] Error verificando tabla: {e}")

    def crear_usuarios_iniciales(self):
        """Crea usuarios iniciales del sistema."""
        if not self.db_connection:
            return

        try:
            # Verificar si ya existen usuarios
            cursor = self.db_connection.connection.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {self.tabla_usuarios}")
            count = cursor.fetchone()[0]

            if count == 0:
                # Crear usuario admin por defecto
                admin_password = hashlib.sha256("admin123".encode()).hexdigest()
                test_password = hashlib.sha256("test".encode()).hexdigest()

                usuarios_iniciales = [
                    {
                        "usuario": "admin",
                        "password_hash": admin_password,
                        "nombre": "Administrador",
                        "email": "admin@stockapp.com",
                        "rol": "admin",
                        "permisos_modulos": "ALL",
                    },
                    {
                        "usuario": "TEST_USER",
                        "password_hash": test_password,
                        "nombre": "Usuario de Prueba",
                        "email": "test@stockapp.com",
                        "rol": "TEST_USER",
                        "permisos_modulos": "Configuración,Inventario",
                    },
                ]

                for usuario_data in usuarios_iniciales:
                    sql_insert = f"""
                    INSERT INTO {self.tabla_usuarios}
                    (usuario, password_hash, nombre, email, rol, permisos_modulos)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """
                    cursor.execute(
                        sql_insert,
                        (
                            usuario_data["usuario"],
                            usuario_data["password_hash"],
                            usuario_data["nombre"],
                            usuario_data["email"],
                            usuario_data["rol"],
                            usuario_data["permisos_modulos"],
                        ),
                    )

                self.db_connection.connection.commit()
                print("[USUARIOS] Usuarios iniciales creados")

        except Exception as e:
            print(f"[ERROR USUARIOS] Error creando usuarios iniciales: {e}")

    def obtener_usuario_por_nombre(self, nombre_usuario):
        """Obtiene un usuario por su nombre."""
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.connection.cursor()
            sql_select = f"""
            SELECT id, usuario, password_hash, nombre, email, rol, estado,
                   permisos_modulos, fecha_creacion, ultimo_acceso
            FROM {self.tabla_usuarios} WHERE usuario = ?
            """
            cursor.execute(sql_select, (nombre_usuario,))
            row = cursor.fetchone()

            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None

        except Exception as e:
            print(f"[ERROR USUARIOS] Error obteniendo usuario: {e}")
            return None

    def obtener_modulos_permitidos(self, usuario_data):
        """Obtiene los módulos permitidos para un usuario."""
        if not usuario_data or not isinstance(usuario_data, dict):
            return ["Configuración"]

        permisos = usuario_data.get("permisos_modulos", "")

        if permisos == "ALL":
            return [
                "Obras",
                "Inventario",
                "Herrajes",
                "Compras / Pedidos",
                "Logística",
                "Vidrios",
                "Mantenimiento",
                "Producción",
                "Contabilidad",
                "Auditoría",
                "Usuarios",
                "Configuración",
            ]
        elif permisos:
            return [m.strip() for m in permisos.split(",")]
        else:
            return ["Configuración"]
