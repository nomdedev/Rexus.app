"""
Modelo de Usuarios - Rexus.app v2.0.0

Gestiona la autenticación, permisos y CRUD completo de usuarios.
"""

import datetime
import hashlib
from typing import Any, Dict, List, Optional, Tuple


class UsuariosModel:
    """Modelo para gestión completa de usuarios y autenticación."""

    # Roles disponibles
    ROLES = {
        "ADMIN": "Administrador",
        "SUPERVISOR": "Supervisor",
        "OPERADOR": "Operador",
        "USUARIO": "Usuario",
        "INVITADO": "Invitado",
    }

    # Estados de usuario
    ESTADOS = {
        "ACTIVO": "Activo",
        "INACTIVO": "Inactivo",
        "SUSPENDIDO": "Suspendido",
        "BLOQUEADO": "Bloqueado",
    }

    # Módulos del sistema
    MODULOS_SISTEMA = [
        "Obras",
        "Inventario",
        "Herrajes",
        "Pedidos",
        "Compras",
        "Logística",
        "Vidrios",
        "Mantenimiento",
        "Contabilidad",
        "Auditoría",
        "Usuarios",
        "Configuración",
        "Dashboard",
    ]

    def __init__(self, db_connection=None):
        self.db_connection = db_connection
        self.tabla_usuarios = "usuarios"
        self.tabla_roles = "roles"
        self.tabla_permisos = "permisos_usuario"
        self.tabla_sesiones = "sesiones_usuario"
        # Las tablas deben existir previamente - no crear desde la aplicación

    def _crear_tablas_si_no_existen(self):
        """
        ELIMINADO: Las tablas deben existir previamente en la base de datos.
        No es responsabilidad de la aplicación crear el esquema de BD.

        Para crear las tablas, ejecutar el script: database/create_tables.sql
        """
        print("ℹ️  [USUARIOS] Las tablas deben existir previamente en la base de datos")
        print("   Para crear las tablas, ejecutar: database/create_tables.sql")
        return

    def crear_usuarios_iniciales(self):
        """ELIMINADO: RIESGO DE SEGURIDAD CRÍTICO - No crear usuarios por defecto"""
        print("❌ SEGURIDAD CRÍTICA: No se crean usuarios automáticamente")
        print(
            "   Los usuarios deben ser creados manualmente por el administrador del sistema"
        )
        print(
            "   Usar script create_admin_simple.py para crear usuario admin manualmente"
        )
        return

    def obtener_usuario_por_nombre(self, nombre_usuario):
        """Obtiene un usuario por su nombre."""
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.connection.cursor()
            sql_select = """
            SELECT id, usuario, password_hash, nombre_completo, email, telefono, rol, estado,
                   fecha_creacion, fecha_modificacion, ultimo_acceso, intentos_fallidos, bloqueado_hasta, avatar, configuracion_personal, activo
            FROM usuarios WHERE usuario = ?
            """
            cursor.execute(sql_select, (nombre_usuario,))
            row = cursor.fetchone()
            print(
                f"[DEBUG obtener_usuario_por_nombre] Buscando usuario: {nombre_usuario}"
            )
            print(f"[DEBUG obtener_usuario_por_nombre] Resultado row: {row}")
            if row:
                columns = [desc[0] for desc in cursor.description]
                usuario_dict = dict(zip(columns, row))
                # Definir todas las claves esperadas y asignar None si falta
                claves_esperadas = [
                    "id",
                    "usuario",
                    "password_hash",
                    "nombre_completo",
                    "email",
                    "telefono",
                    "rol",
                    "estado",
                    "fecha_creacion",
                    "fecha_modificacion",
                    "ultimo_acceso",
                    "intentos_fallidos",
                    "bloqueado_hasta",
                    "avatar",
                    "configuracion_personal",
                    "activo",
                ]
                for clave in claves_esperadas:
                    if clave not in usuario_dict:
                        usuario_dict[clave] = None
                print(
                    f"[DEBUG obtener_usuario_por_nombre] Usuario dict: {usuario_dict}"
                )
                return usuario_dict
            print("[DEBUG obtener_usuario_por_nombre] No se encontró el usuario.")
            return None
        except Exception as e:
            print(f"[ERROR USUARIOS] Error obteniendo usuario: {e}")
            # Si hay error, devolver un dict vacío con todas las claves esperadas en None
            claves_esperadas = [
                "id",
                "usuario",
                "password_hash",
                "nombre_completo",
                "email",
                "telefono",
                "rol",
                "estado",
                "fecha_creacion",
                "fecha_modificacion",
                "ultimo_acceso",
                "intentos_fallidos",
                "bloqueado_hasta",
                "avatar",
                "configuracion_personal",
                "activo",
            ]
            return {clave: None for clave in claves_esperadas}

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

    def crear_usuario(self, datos_usuario: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Crea un nuevo usuario en el sistema.

        Args:
            datos_usuario: Diccionario con los datos del usuario

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        if not self.db_connection:
            return False, "Sin conexión a la base de datos"

        try:
            cursor = self.db_connection.connection.cursor()

            # Verificar que el usuario no exista
            cursor.execute(
                "SELECT COUNT(*) FROM usuarios WHERE usuario = ?",
                (datos_usuario["usuario"],),
            )
            if cursor.fetchone()[0] > 0:
                return False, f"El usuario '{datos_usuario['usuario']}' ya existe"

            # Verificar que el email no exista
            if datos_usuario.get("email"):
                cursor.execute(
                    "SELECT COUNT(*) FROM usuarios WHERE email = ?",
                    (datos_usuario["email"],),
                )
                if cursor.fetchone()[0] > 0:
                    return (
                        False,
                        f"El email '{datos_usuario['email']}' ya está registrado",
                    )

            # Hashear la contraseña
            password_hash = self._hashear_password(datos_usuario["password"])

            # Insertar usuario
            cursor.execute(
                """
                INSERT INTO usuarios 
                (usuario, password_hash, nombre_completo, email, telefono, rol, estado)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    datos_usuario["usuario"],
                    password_hash,
                    datos_usuario["nombre_completo"],
                    datos_usuario.get("email", ""),
                    datos_usuario.get("telefono", ""),
                    datos_usuario.get("rol", "USUARIO"),
                    datos_usuario.get("estado", "ACTIVO"),
                ),
            )

            # Obtener ID del usuario creado
            cursor.execute("SELECT @@IDENTITY")
            usuario_id = cursor.fetchone()[0]

            # Asignar permisos por defecto
            permisos_defecto = datos_usuario.get("permisos", ["Configuración"])
            for modulo in permisos_defecto:
                cursor.execute(
                    """
                    INSERT INTO permisos_usuario (usuario_id, modulo, permisos)
                    VALUES (?, ?, ?)
                """,
                    (usuario_id, modulo, "leer"),
                )

            self.db_connection.connection.commit()
            print(
                f"[USUARIOS] Usuario '{datos_usuario['usuario']}' creado exitosamente"
            )
            return True, f"Usuario '{datos_usuario['usuario']}' creado exitosamente"

        except Exception as e:
            print(f"[ERROR USUARIOS] Error creando usuario: {e}")
            if self.db_connection:
                self.db_connection.connection.rollback()
            return False, f"Error creando usuario: {str(e)}"

    def obtener_todos_usuarios(self) -> List[Dict[str, Any]]:
        """Obtiene todos los usuarios del sistema."""
        if not self.db_connection:
            return self._get_usuarios_demo()

        try:
            cursor = self.db_connection.connection.cursor()
            cursor.execute("""
                SELECT id, usuario, nombre_completo, email, telefono, rol, estado,
                       fecha_creacion, ultimo_acceso, intentos_fallidos
                FROM usuarios
                WHERE activo = 1
                ORDER BY nombre_completo
            """)

            columns = [desc[0] for desc in cursor.description]
            usuarios = []

            for row in cursor.fetchall():
                usuario = dict(zip(columns, row))
                usuario["rol_texto"] = self.ROLES.get(usuario["rol"], usuario["rol"])
                usuario["estado_texto"] = self.ESTADOS.get(
                    usuario["estado"], usuario["estado"]
                )

                # Obtener permisos
                usuario["permisos"] = self.obtener_permisos_usuario(usuario["id"])
                usuarios.append(usuario)

            return usuarios

        except Exception as e:
            print(f"[ERROR USUARIOS] Error obteniendo usuarios: {e}")
            return self._get_usuarios_demo()

    def obtener_usuario_por_id(self, usuario_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un usuario por su ID."""
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.connection.cursor()
            cursor.execute(
                """
                SELECT id, usuario, nombre_completo, email, telefono, rol, estado,
                       fecha_creacion, fecha_modificacion, ultimo_acceso, intentos_fallidos,
                       bloqueado_hasta, avatar, configuracion_personal
                FROM usuarios
                WHERE id = ? AND activo = 1
            """,
                (usuario_id,),
            )

            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                usuario = dict(zip(columns, row))
                usuario["permisos"] = self.obtener_permisos_usuario(usuario_id)
                return usuario

            return None

        except Exception as e:
            print(f"[ERROR USUARIOS] Error obteniendo usuario por ID: {e}")
            return None

    def actualizar_usuario(
        self, usuario_id: int, datos_usuario: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Actualiza los datos de un usuario.

        Args:
            usuario_id: ID del usuario a actualizar
            datos_usuario: Nuevos datos del usuario

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        if not self.db_connection:
            return False, "Sin conexión a la base de datos"

        try:
            cursor = self.db_connection.connection.cursor()

            # Verificar que el usuario exista
            cursor.execute(
                "SELECT COUNT(*) FROM usuarios WHERE id = ?",
                (usuario_id,),
            )
            if cursor.fetchone()[0] == 0:
                return False, "Usuario no encontrado"

            # Actualizar datos básicos
            cursor.execute(
                """
                UPDATE usuarios
                SET nombre_completo = ?, email = ?, telefono = ?, rol = ?, estado = ?,
                    fecha_modificacion = GETDATE()
                WHERE id = ?
            """,
                (
                    datos_usuario["nombre_completo"],
                    datos_usuario.get("email", ""),
                    datos_usuario.get("telefono", ""),
                    datos_usuario.get("rol", "USUARIO"),
                    datos_usuario.get("estado", "ACTIVO"),
                    usuario_id,
                ),
            )

            # Actualizar contraseña si se proporciona
            if datos_usuario.get("password"):
                password_hash = self._hashear_password(datos_usuario["password"])
                cursor.execute(
                    """
                    UPDATE usuarios
                    SET password_hash = ?, intentos_fallidos = 0, bloqueado_hasta = NULL
                    WHERE id = ?
                """,
                    (password_hash, usuario_id),
                )

            # Actualizar permisos
            if "permisos" in datos_usuario:
                cursor.execute(
                    "DELETE FROM permisos_usuario WHERE usuario_id = ?",
                    (usuario_id,),
                )

                for modulo in datos_usuario["permisos"]:
                    cursor.execute(
                        """
                        INSERT INTO permisos_usuario (usuario_id, modulo, permisos)
                        VALUES (?, ?, ?)
                    """,
                        (usuario_id, modulo, "leer,escribir"),
                    )

            self.db_connection.connection.commit()
            return True, "Usuario actualizado exitosamente"

        except Exception as e:
            print(f"[ERROR USUARIOS] Error actualizando usuario: {e}")
            if self.db_connection:
                self.db_connection.connection.rollback()
            return False, f"Error actualizando usuario: {str(e)}"

    def eliminar_usuario(self, usuario_id: int) -> Tuple[bool, str]:
        """
        Elimina un usuario del sistema (eliminación lógica).

        Args:
            usuario_id: ID del usuario a eliminar

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        if not self.db_connection:
            return False, "Sin conexión a la base de datos"

        try:
            cursor = self.db_connection.connection.cursor()

            # Verificar que el usuario exista
            cursor.execute("SELECT usuario FROM usuarios WHERE id = ?", (usuario_id,))
            row = cursor.fetchone()
            if not row:
                return False, "Usuario no encontrado"

            nombre_usuario = row[0]

            # No permitir eliminar el usuario admin
            if nombre_usuario == "admin":
                return False, "No se puede eliminar el usuario administrador"

            # Eliminación lógica
            cursor.execute(
                """
                UPDATE usuarios
                SET activo = 0, estado = 'INACTIVO', fecha_modificacion = GETDATE()
                WHERE id = ?
            """,
                (usuario_id,),
            )

            # Cerrar sesiones activas
            cursor.execute(
                """
                UPDATE sesiones_usuario
                SET activa = 0, fecha_fin = GETDATE()
                WHERE usuario_id = ? AND activa = 1
            """,
                (usuario_id,),
            )

            self.db_connection.connection.commit()
            return True, f"Usuario '{nombre_usuario}' eliminado exitosamente"

        except Exception as e:
            print(f"[ERROR USUARIOS] Error eliminando usuario: {e}")
            if self.db_connection:
                self.db_connection.connection.rollback()
            return False, f"Error eliminando usuario: {str(e)}"

    def obtener_permisos_usuario(self, usuario_id: int) -> List[str]:
        """Obtiene los permisos de un usuario."""
        if not self.db_connection:
            return ["Configuración"]

        try:
            cursor = self.db_connection.connection.cursor()
            cursor.execute(
                """
                SELECT modulo FROM permisos_usuario
                WHERE usuario_id = ?
            """,
                (usuario_id,),
            )

            return [row[0] for row in cursor.fetchall()]

        except Exception as e:
            print(f"[ERROR USUARIOS] Error obteniendo permisos: {e}")
            return ["Configuración"]

    def cambiar_password(
        self, usuario_id: int, password_actual: str, password_nueva: str
    ) -> Tuple[bool, str]:
        """
        Cambia la contraseña de un usuario.

        Args:
            usuario_id: ID del usuario
            password_actual: Contraseña actual
            password_nueva: Nueva contraseña

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        if not self.db_connection:
            return False, "Sin conexión a la base de datos"

        try:
            cursor = self.db_connection.connection.cursor()

            # Verificar contraseña actual
            cursor.execute(
                "SELECT password_hash FROM usuarios WHERE id = ?",
                (usuario_id,),
            )
            row = cursor.fetchone()
            if not row:
                return False, "Usuario no encontrado"

            if not self._verificar_password(password_actual, row[0]):
                return False, "Contraseña actual incorrecta"

            # Actualizar contraseña
            nueva_hash = self._hashear_password(password_nueva)
            cursor.execute(
                """
                UPDATE usuarios
                SET password_hash = ?, intentos_fallidos = 0, bloqueado_hasta = NULL,
                    fecha_modificacion = GETDATE()
                WHERE id = ?
            """,
                (nueva_hash, usuario_id),
            )

            self.db_connection.connection.commit()
            return True, "Contraseña cambiada exitosamente"

        except Exception as e:
            print(f"[ERROR USUARIOS] Error cambiando contraseña: {e}")
            if self.db_connection:
                self.db_connection.connection.rollback()
            return False, f"Error cambiando contraseña: {str(e)}"

    def obtener_estadisticas_usuarios(self) -> Dict[str, Any]:
        """Obtiene estadísticas de usuarios."""
        if not self.db_connection:
            return self._get_estadisticas_demo()

        try:
            cursor = self.db_connection.connection.cursor()

            stats = {}

            # Total de usuarios
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE activo = 1")
            stats["total_usuarios"] = cursor.fetchone()[0]

            # Usuarios por estado
            cursor.execute("""
                SELECT estado, COUNT(*) 
                FROM usuarios 
                WHERE activo = 1
                GROUP BY estado
            """)
            stats["por_estado"] = {row[0]: row[1] for row in cursor.fetchall()}

            # Usuarios por rol
            cursor.execute("""
                SELECT rol, COUNT(*) 
                FROM usuarios 
                WHERE activo = 1
                GROUP BY rol
            """)
            stats["por_rol"] = {row[0]: row[1] for row in cursor.fetchall()}

            # Usuarios activos en el último mes
            cursor.execute("""
                SELECT COUNT(*) FROM usuarios
                WHERE activo = 1 AND ultimo_acceso >= DATEADD(MONTH, -1, GETDATE())
            """)
            stats["activos_mes"] = cursor.fetchone()[0]

            # Usuarios creados este mes
            cursor.execute("""
                SELECT COUNT(*) FROM usuarios
                WHERE activo = 1 AND MONTH(fecha_creacion) = MONTH(GETDATE()) 
                AND YEAR(fecha_creacion) = YEAR(GETDATE())
            """)
            stats["creados_mes"] = cursor.fetchone()[0]

            return stats

        except Exception as e:
            print(f"[ERROR USUARIOS] Error obteniendo estadísticas: {e}")
            return self._get_estadisticas_demo()

    def _hashear_password(self, password: str) -> str:
        """Hashea una contraseña."""
        return hashlib.sha256(password.encode()).hexdigest()

    def _verificar_password(self, password: str, hash_almacenado: str) -> bool:
        """Verifica una contraseña contra su hash."""
        return self._hashear_password(password) == hash_almacenado

    def _get_usuarios_demo(self) -> List[Dict[str, Any]]:
        """Datos demo cuando no hay conexión a BD."""
        return [
            {
                "id": 1,
                "usuario": "admin",
                "nombre_completo": "Administrador Sistema",
                "email": "admin@rexus.app",
                "telefono": "+1234567890",
                "rol": "ADMIN",
                "rol_texto": "Administrador",
                "estado": "ACTIVO",
                "estado_texto": "Activo",
                "fecha_creacion": "2025-01-01",
                "ultimo_acceso": "2025-01-15",
                "intentos_fallidos": 0,
                "permisos": self.MODULOS_SISTEMA,
            },
            {
                "id": 2,
                "usuario": "supervisor",
                "nombre_completo": "Supervisor General",
                "email": "supervisor@rexus.app",
                "telefono": "+1234567891",
                "rol": "SUPERVISOR",
                "rol_texto": "Supervisor",
                "estado": "ACTIVO",
                "estado_texto": "Activo",
                "fecha_creacion": "2025-01-02",
                "ultimo_acceso": "2025-01-14",
                "intentos_fallidos": 0,
                "permisos": ["Obras", "Inventario", "Pedidos", "Dashboard"],
            },
        ]

    def _get_estadisticas_demo(self) -> Dict[str, Any]:
        """Estadísticas demo cuando no hay conexión a BD."""
        return {
            "total_usuarios": 12,
            "por_estado": {
                "ACTIVO": 10,
                "INACTIVO": 2,
                "SUSPENDIDO": 0,
                "BLOQUEADO": 0,
            },
            "por_rol": {"ADMIN": 1, "SUPERVISOR": 2, "OPERADOR": 5, "USUARIO": 4},
            "activos_mes": 8,
            "creados_mes": 2,
        }
