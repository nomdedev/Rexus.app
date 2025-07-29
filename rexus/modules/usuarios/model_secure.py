"""
Modelo de Usuarios SEGURO - Rexus.app v2.0.0

VERSION CORREGIDA: Sin vulnerabilidades SQL injection, con validación de contraseñas
y control de intentos fallidos de login.

CORRECCIONES DE SEGURIDAD:
- ❌ ELIMINADO: Creación automática de usuarios (RIESGO CRÍTICO)
- ✅ CORREGIDO: SQL injection - Usar solo queries parametrizadas 
- ✅ AÑADIDO: Control de intentos fallidos de login
- ✅ AÑADIDO: Validación de contraseñas fuertes
- ✅ AÑADIDO: Bloqueo temporal de cuentas tras múltiples intentos
- ✅ CORREGIDO: Nombres de tabla hardcodeados (no usar f-strings)
"""

import datetime
import hashlib
import re
from typing import Any, Dict, List, Optional, Tuple


class UsuariosModelSecure:
    """Modelo SEGURO para gestión completa de usuarios y autenticación."""

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

    # Configuración de seguridad
    MAX_INTENTOS_LOGIN = 3
    BLOQUEO_TEMPORAL_MINUTOS = 15
    MIN_PASSWORD_LENGTH = 8
    REQUIRE_COMPLEX_PASSWORD = True

    def __init__(self, db_connection=None):
        self.db_connection = db_connection
        # SEGURIDAD: Nombres de tabla hardcodeados (no usar variables dinámicas)
        self.tabla_usuarios = "usuarios"
        self.tabla_roles = "roles"
        self.tabla_permisos = "permisos_usuario"
        self.tabla_sesiones = "sesiones_usuario"
        self._crear_tablas_si_no_existen()

    def _crear_tablas_si_no_existen(self):
        """Crea las tablas necesarias para el sistema de usuarios."""
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.connection.cursor()

            # SEGURIDAD: Usar nombres de tabla hardcodeados (NO f-strings)
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='usuarios' AND xtype='U')
                CREATE TABLE usuarios (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    usuario NVARCHAR(50) UNIQUE NOT NULL,
                    password_hash NVARCHAR(255) NOT NULL,
                    nombre_completo NVARCHAR(100) NOT NULL,
                    email NVARCHAR(100) UNIQUE,
                    telefono NVARCHAR(20),
                    rol NVARCHAR(50) NOT NULL DEFAULT 'USUARIO',
                    estado NVARCHAR(20) NOT NULL DEFAULT 'ACTIVO',
                    fecha_creacion DATETIME NOT NULL DEFAULT GETDATE(),
                    fecha_modificacion DATETIME NOT NULL DEFAULT GETDATE(),
                    ultimo_acceso DATETIME,
                    intentos_fallidos INT DEFAULT 0,
                    bloqueado_hasta DATETIME,
                    avatar NVARCHAR(255),
                    configuracion_personal NTEXT,
                    activo BIT NOT NULL DEFAULT 1
                )
            """)

            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='roles' AND xtype='U')
                CREATE TABLE roles (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    nombre NVARCHAR(50) UNIQUE NOT NULL,
                    descripcion NVARCHAR(255),
                    permisos_json NTEXT,
                    fecha_creacion DATETIME NOT NULL DEFAULT GETDATE(),
                    activo BIT NOT NULL DEFAULT 1
                )
            """)

            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='permisos_usuario' AND xtype='U')
                CREATE TABLE permisos_usuario (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    usuario_id INT NOT NULL,
                    modulo NVARCHAR(50) NOT NULL,
                    permisos NVARCHAR(255) NOT NULL,
                    fecha_asignacion DATETIME NOT NULL DEFAULT GETDATE(),
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
                )
            """)

            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='sesiones_usuario' AND xtype='U')
                CREATE TABLE sesiones_usuario (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    usuario_id INT NOT NULL,
                    token_sesion NVARCHAR(255) NOT NULL,
                    ip_address NVARCHAR(45),
                    user_agent NVARCHAR(255),
                    fecha_inicio DATETIME NOT NULL DEFAULT GETDATE(),
                    fecha_fin DATETIME,
                    activa BIT NOT NULL DEFAULT 1,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
                )
            """)

            # Crear índices
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_usuarios_usuario ON usuarios(usuario)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_usuarios_estado ON usuarios(estado)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_permisos_usuario ON permisos_usuario(usuario_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sesiones_usuario ON sesiones_usuario(usuario_id)")

            self.db_connection.connection.commit()
            print("✅ [USUARIOS SEGURO] Tablas del sistema de usuarios creadas/verificadas")

        except Exception as e:
            print(f"❌ [ERROR USUARIOS SEGURO] Error creando tablas: {e}")
            if self.db_connection:
                self.db_connection.connection.rollback()

    def validar_password_compleja(self, password: str) -> Tuple[bool, str]:
        """
        Valida que la contraseña sea suficientemente fuerte.
        
        Returns:
            Tuple[bool, str]: (es_válida, mensaje_error)
        """
        if len(password) < self.MIN_PASSWORD_LENGTH:
            return False, f"La contraseña debe tener al menos {self.MIN_PASSWORD_LENGTH} caracteres"
        
        if not self.REQUIRE_COMPLEX_PASSWORD:
            return True, ""
        
        # Verificar complejidad
        tiene_mayuscula = bool(re.search(r'[A-Z]', password))
        tiene_minuscula = bool(re.search(r'[a-z]', password))
        tiene_numero = bool(re.search(r'[0-9]', password))
        tiene_simbolo = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        
        requisitos_cumplidos = sum([tiene_mayuscula, tiene_minuscula, tiene_numero, tiene_simbolo])
        
        if requisitos_cumplidos < 3:
            return False, "La contraseña debe contener al menos 3 de: mayúsculas, minúsculas, números, símbolos"
        
        # Verificar que no sea muy común
        passwords_comunes = [
            "password", "123456", "admin", "qwerty", "password123", 
            "admin123", "12345678", "test", "usuario"
        ]
        if password.lower() in passwords_comunes:
            return False, "La contraseña es demasiado común"
        
        return True, ""

    def verificar_bloqueo_usuario(self, nombre_usuario: str) -> Tuple[bool, str]:
        """
        Verifica si un usuario está bloqueado por intentos fallidos.
        
        Returns:
            Tuple[bool, str]: (está_bloqueado, mensaje)
        """
        if not self.db_connection:
            return False, ""

        try:
            cursor = self.db_connection.connection.cursor()
            
            # SEGURIDAD: Query parametrizada, no f-strings
            cursor.execute("""
                SELECT intentos_fallidos, bloqueado_hasta 
                FROM usuarios 
                WHERE usuario = ?
            """, (nombre_usuario,))
            
            row = cursor.fetchone()
            if not row:
                return False, "Usuario no encontrado"
            
            intentos_fallidos, bloqueado_hasta = row
            
            # Verificar si está bloqueado temporalmente
            if bloqueado_hasta and bloqueado_hasta > datetime.datetime.now():
                tiempo_restante = bloqueado_hasta - datetime.datetime.now()
                minutos = int(tiempo_restante.total_seconds() / 60)
                return True, f"Cuenta bloqueada por {minutos} minutos más debido a múltiples intentos fallidos"
            
            # Si el bloqueo expiró, resetear intentos
            if bloqueado_hasta and bloqueado_hasta <= datetime.datetime.now():
                cursor.execute("""
                    UPDATE usuarios 
                    SET intentos_fallidos = 0, bloqueado_hasta = NULL 
                    WHERE usuario = ?
                """, (nombre_usuario,))
                self.db_connection.connection.commit()
            
            return False, ""
            
        except Exception as e:
            print(f"❌ Error verificando bloqueo: {e}")
            return False, ""

    def registrar_intento_fallido(self, nombre_usuario: str):
        """Registra un intento de login fallido y bloquea si es necesario."""
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.connection.cursor()
            
            # Incrementar intentos fallidos
            cursor.execute("""
                UPDATE usuarios 
                SET intentos_fallidos = intentos_fallidos + 1,
                    fecha_modificacion = GETDATE()
                WHERE usuario = ?
            """, (nombre_usuario,))
            
            # Verificar si debe bloquearse
            cursor.execute("""
                SELECT intentos_fallidos 
                FROM usuarios 
                WHERE usuario = ?
            """, (nombre_usuario,))
            
            row = cursor.fetchone()
            if row and row[0] >= self.MAX_INTENTOS_LOGIN:
                # Bloquear temporalmente
                bloqueo_hasta = datetime.datetime.now() + datetime.timedelta(minutes=self.BLOQUEO_TEMPORAL_MINUTOS)
                cursor.execute("""
                    UPDATE usuarios 
                    SET bloqueado_hasta = ?, estado = 'BLOQUEADO'
                    WHERE usuario = ?
                """, (bloqueo_hasta, nombre_usuario))
                
                print(f"⚠️ Usuario {nombre_usuario} bloqueado por {self.BLOQUEO_TEMPORAL_MINUTOS} minutos")
            
            self.db_connection.connection.commit()
            
        except Exception as e:
            print(f"❌ Error registrando intento fallido: {e}")

    def resetear_intentos_fallidos(self, nombre_usuario: str):
        """Resetea los intentos fallidos tras login exitoso."""
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.connection.cursor()
            cursor.execute("""
                UPDATE usuarios 
                SET intentos_fallidos = 0, bloqueado_hasta = NULL, 
                    ultimo_acceso = GETDATE(), estado = 'ACTIVO'
                WHERE usuario = ?
            """, (nombre_usuario,))
            self.db_connection.connection.commit()
            
        except Exception as e:
            print(f"❌ Error reseteando intentos fallidos: {e}")

    def obtener_usuario_por_nombre(self, nombre_usuario: str) -> Optional[Dict]:
        """Obtiene un usuario por su nombre (SEGURO - query parametrizada)."""
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.connection.cursor()
            
            # SEGURIDAD: Query completamente parametrizada
            cursor.execute("""
                SELECT id, usuario, password_hash, nombre_completo, email, telefono, rol, estado,
                       fecha_creacion, fecha_modificacion, ultimo_acceso, intentos_fallidos, 
                       bloqueado_hasta, avatar, configuracion_personal, activo
                FROM usuarios 
                WHERE usuario = ? AND activo = 1
            """, (nombre_usuario,))
            
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                usuario_dict = dict(zip(columns, row))
                return usuario_dict
            
            return None

        except Exception as e:
            print(f"❌ [ERROR USUARIOS SEGURO] Error obteniendo usuario: {e}")
            return None

    def crear_usuario(self, datos_usuario: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Crea un nuevo usuario con validaciones de seguridad.
        
        SEGURIDAD:
        - Validación de contraseña fuerte
        - Queries parametrizadas
        - Verificación de duplicados
        """
        if not self.db_connection:
            return False, "Sin conexión a la base de datos"

        try:
            # Validar contraseña
            password_valida, error_password = self.validar_password_compleja(datos_usuario.get("password", ""))
            if not password_valida:
                return False, f"Contraseña inválida: {error_password}"

            cursor = self.db_connection.connection.cursor()

            # Verificar usuario único
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE usuario = ?", (datos_usuario["usuario"],))
            if cursor.fetchone()[0] > 0:
                return False, f"El usuario '{datos_usuario['usuario']}' ya existe"

            # Verificar email único
            if datos_usuario.get("email"):
                cursor.execute("SELECT COUNT(*) FROM usuarios WHERE email = ?", (datos_usuario["email"],))
                if cursor.fetchone()[0] > 0:
                    return False, f"El email '{datos_usuario['email']}' ya está registrado"

            # Hash de contraseña
            password_hash = self._hashear_password(datos_usuario["password"])

            # SEGURIDAD: Query completamente parametrizada
            cursor.execute("""
                INSERT INTO usuarios 
                (usuario, password_hash, nombre_completo, email, telefono, rol, estado)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                datos_usuario["usuario"],
                password_hash,
                datos_usuario["nombre_completo"],
                datos_usuario.get("email", ""),
                datos_usuario.get("telefono", ""),
                datos_usuario.get("rol", "USUARIO"),
                datos_usuario.get("estado", "ACTIVO"),
            ))

            # Obtener ID del usuario creado
            cursor.execute("SELECT @@IDENTITY")
            usuario_id = cursor.fetchone()[0]

            # Asignar permisos por defecto
            permisos_defecto = datos_usuario.get("permisos", ["Configuración"])
            for modulo in permisos_defecto:
                cursor.execute("""
                    INSERT INTO permisos_usuario (usuario_id, modulo, permisos)
                    VALUES (?, ?, ?)
                """, (usuario_id, modulo, "leer"))

            self.db_connection.connection.commit()
            print(f"✅ [USUARIOS SEGURO] Usuario '{datos_usuario['usuario']}' creado exitosamente")
            return True, f"Usuario '{datos_usuario['usuario']}' creado exitosamente"

        except Exception as e:
            print(f"❌ [ERROR USUARIOS SEGURO] Error creando usuario: {e}")
            if self.db_connection:
                self.db_connection.connection.rollback()
            return False, f"Error creando usuario: {str(e)}"

    def _hashear_password(self, password: str) -> str:
        """Hashea una contraseña usando SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def _verificar_password(self, password: str, hash_almacenado: str) -> bool:
        """Verifica una contraseña contra su hash."""
        return self._hashear_password(password) == hash_almacenado

    def autenticar_usuario_seguro(self, nombre_usuario: str, password: str) -> Optional[Dict]:
        """
        Autentica un usuario con controles de seguridad completos.
        
        SEGURIDAD:
        - Control de intentos fallidos
        - Bloqueo temporal tras múltiples intentos
        - Logging de eventos de seguridad
        """
        # Verificar bloqueo
        bloqueado, mensaje_bloqueo = self.verificar_bloqueo_usuario(nombre_usuario)
        if bloqueado:
            print(f"🔒 Intento de login en cuenta bloqueada: {nombre_usuario}")
            return None

        # Obtener usuario
        usuario = self.obtener_usuario_por_nombre(nombre_usuario)
        if not usuario:
            print(f"❌ Usuario no encontrado: {nombre_usuario}")
            return None

        # Verificar contraseña
        if not self._verificar_password(password, usuario["password_hash"]):
            print(f"❌ Contraseña incorrecta para usuario: {nombre_usuario}")
            self.registrar_intento_fallido(nombre_usuario)
            return None

        # Verificar estado del usuario
        if usuario["estado"] != "ACTIVO":
            print(f"❌ Usuario inactivo: {nombre_usuario}")
            return None

        # Login exitoso
        self.resetear_intentos_fallidos(nombre_usuario)
        print(f"✅ Login exitoso: {nombre_usuario}")
        
        return usuario

    def obtener_todos_usuarios(self) -> List[Dict[str, Any]]:
        """Obtiene todos los usuarios (SEGURO - query parametrizada)."""
        if not self.db_connection:
            return []

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
                usuario["estado_texto"] = self.ESTADOS.get(usuario["estado"], usuario["estado"])
                usuarios.append(usuario)

            return usuarios

        except Exception as e:
            print(f"❌ [ERROR USUARIOS SEGURO] Error obteniendo usuarios: {e}")
            return []

    def __del__(self):
        """Destructor - Documentar que NO se crean usuarios automáticamente."""
        print("ℹ️ [USUARIOS SEGURO] Modelo destruido - NO SE CREAN USUARIOS AUTOMÁTICAMENTE")
        print("   Para crear el usuario admin inicial, usar: python create_admin_simple.py")