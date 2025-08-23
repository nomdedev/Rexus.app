"""
Submódulo de Autenticación de Usuarios - Rexus.app

Gestiona autenticación, validación de contraseñas y seguridad de acceso.
Responsabilidades:
- Autenticación segura de usuarios
- Validación de fortaleza de contraseñas
- Control de intentos fallidos y bloqueos
- Gestión de sesiones y tokens
"""

import datetime
import hashlib
            
            # Verificar si la cuenta está bloqueada
            if self.verificar_cuenta_bloqueada(username_safe):
                return {
                    "success": False,
                    "error": "Cuenta bloqueada por múltiples intentos fallidos",
                }

            cursor = self.db_connection.cursor()

            # Obtener datos del usuario
            query = self.sql_manager.get_query(
                self.sql_path, "obtener_usuario_autenticacion"
            )
            cursor.execute(query, (username_safe,))

            usuario = cursor.fetchone()
            if not usuario:
                self.registrar_intento_login(username_safe, exitoso=False)
                return {"success": False, "error": "Usuario no encontrado"}

            # Verificar contraseña
            password_hash = self._hash_password(password, usuario[2])  # salt
            if password_hash != usuario[1]:  # password_hash
                self.registrar_intento_login(username_safe, exitoso=False)
                return {"success": False, "error": "Contraseña incorrecta"}

            # Autenticación exitosa
            self.reset_intentos_login(username_safe)
            self.registrar_intento_login(username_safe, exitoso=True)

            # Construir datos del usuario autenticado
            columns = [desc[0] for desc in cursor.description]
            usuario_data = dict(zip(columns, usuario))

            return {
                "success": True,
                "usuario": {
                    "id": usuario_data.get("id"),
                    "username": usuario_data.get("username"),
                    "email": usuario_data.get("email"),
                    "rol": usuario_data.get("rol", "usuario"),
                    "activo": usuario_data.get("activo", True),
                    "ultimo_acceso": datetime.datetime.now(),
                },
            }

        except Exception as e:
            self.
    def registrar_intento_login(self, username: str, exitoso: bool = False) -> None:
        """Registra un intento de login en el sistema."""
        if not self.db_connection:
            return

        try:
            username_safe = sanitize_string(username)
            cursor = self.db_connection.cursor()

            query = self.sql_manager.get_query(self.sql_path, "registrar_intento_login")
            cursor.execute(
                query,
                (
                    username_safe,
                    exitoso,
                    datetime.datetime.now(),
                    self._obtener_ip_cliente(),
                ),
            )

            self.db_connection.commit()

            # Si falló, incrementar contador
            if not exitoso:
                self._incrementar_intentos_fallidos(username_safe)

        except Exception as e:
            self.
    def validar_fortaleza_password(self, password: str) -> Dict[str, Any]:
        """
        Valida la fortaleza de una contraseña según criterios de seguridad.

        Args:
            password: Contraseña a validar

        Returns:
            Dict con resultado de validación y criterios evaluados
        """
        if not password:
            return {
                "valida": False,
                "puntuacion": 0,
                "criterios": {},
                "mensaje": "Contraseña requerida",
            }

        criterios = {
            "longitud_minima": len(password) >= 8,
            "tiene_mayuscula": any(c.isupper() for c in password),
            "tiene_minuscula": any(c.islower() for c in password),
            "tiene_numero": any(c.isdigit() for c in password),
            "tiene_simbolo": any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password),
            "no_muy_corta": len(password) >= 6,
            "no_muy_larga": len(password) <= 128,
        }

        criterios_cumplidos = sum(criterios.values())
        total_criterios = len(criterios)

        puntuacion = (criterios_cumplidos / total_criterios) * 100

        # Determinar nivel de fortaleza
        if puntuacion >= 85:
            nivel = "Muy fuerte"
        elif puntuacion >= 70:
            nivel = "Fuerte"
        elif puntuacion >= 50:
            nivel = "Moderada"
        else:
            nivel = "Débil"

        valida = criterios_cumplidos >= 5  # Al menos 5 criterios

        return {
            "valida": valida,
            "puntuacion": round(puntuacion, 1),
            "nivel": nivel,
            "criterios": criterios,
            "criterios_cumplidos": criterios_cumplidos,
            "total_criterios": total_criterios,
            "mensaje": self._generar_mensaje_password(criterios, valida),
        }

    def cambiar_password_usuario(
        self, usuario_id: int, password_actual: str, password_nueva: str
    ) -> Dict[str, Any]:
        """Cambia la contraseña de un usuario con validaciones."""
        if not self.db_connection:
            return {"success": False, "error": "Sin conexión a base de datos"}

        try:
            # Validar fortaleza de nueva contraseña
            validacion = self.validar_fortaleza_password(password_nueva)
            if not validacion["valida"]:
                return {
                    "success": False,
                    "error": f"Contraseña no cumple criterios: {validacion['mensaje']}",
                }

            cursor = self.db_connection.cursor()

            # Verificar contraseña actual
            query_verificar = self.sql_manager.get_query(
                self.sql_path, "verificar_password_actual"
            )
            cursor.execute(query_verificar, (usuario_id,))

            usuario = cursor.fetchone()
            if not usuario:
                return {"success": False, "error": "Usuario no encontrado"}

            password_hash_actual = self._hash_password(
                password_actual, usuario[1]
            )  # salt
            if password_hash_actual != usuario[0]:  # password_hash
                return {"success": False, "error": "Contraseña actual incorrecta"}

            # Generar nuevo hash y salt
            nuevo_salt = self._generar_salt()
            nuevo_hash = self._hash_password(password_nueva, nuevo_salt)

            # Actualizar contraseña
            query_actualizar = self.sql_manager.get_query(
                self.sql_path, "actualizar_password"
            )
            cursor.execute(query_actualizar,
(nuevo_hash,
                nuevo_salt,
                usuario_id))

            self.db_connection.commit()

            return {"success": True, "mensaje": "Contraseña actualizada exitosamente"}

        except Exception as e:
            if self.db_connection:
                self.db_connection.rollback()
            self.    def _bloquear_usuario(self, username: str) -> None:
        """Bloquea temporalmente un usuario."""
        try:
            cursor = self.db_connection.cursor()

            query = self.sql_manager.get_query(self.sql_path, "bloquear_usuario")
            cursor.execute(
                query,
                (
                    username,
                    datetime.datetime.now(),
                    datetime.datetime.now()
                    + datetime.timedelta(minutes=self.tiempo_bloqueo_minutos),
                ),
            )

        except Exception as e:
    def _hash_password(self, password: str, salt: str) -> str:
        """Genera hash de contraseña con salt."""
        return hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
        ).hex()

    def _generar_salt(self) -> str:
        """Genera un salt aleatorio."""
        import secrets

        return secrets.token_hex(32)

    def _obtener_ip_cliente(self) -> str:
        """Obtiene la IP del cliente (simplificado)."""
        return "127.0.0.1"  # Placeholder

    def _generar_mensaje_password(
        self, criterios: Dict[str, bool], valida: bool
    ) -> str:
        """Genera mensaje descriptivo sobre validación de contraseña."""
        if valida:
            return "Contraseña cumple los criterios de seguridad"

        faltantes = []
        if not criterios.get("longitud_minima"):
            faltantes.append("mínimo 8 caracteres")
        if not criterios.get("tiene_mayuscula"):
            faltantes.append("al menos una mayúscula")
        if not criterios.get("tiene_minuscula"):
            faltantes.append("al menos una minúscula")
        if not criterios.get("tiene_numero"):
            faltantes.append("al menos un número")
        if not criterios.get("tiene_simbolo"):
            faltantes.append("al menos un símbolo")

        return f"Faltan: {', '.join(faltantes)}"
