"""
Constantes para el módulo de Usuarios - Rexus.app

Centraliza strings, configuraciones y constantes para evitar 
duplicación y facilitar mantenimiento.
"""

class UsuariosConstants:
    """Constantes del módulo de usuarios."""

    # Títulos y etiquetas
    TITULO_MODULO = "👥 Gestión de Usuarios"
    
    # Botones
    BTN_NUEVO_USUARIO = "➕ Nuevo Usuario"
    BTN_EDITAR_USUARIO = "✏️ Editar"
    BTN_ELIMINAR_USUARIO = "🗑️ Eliminar"
    BTN_CAMBIAR_PASSWORD = "🔐 Cambiar Contraseña"
    BTN_BLOQUEAR_USUARIO = "🚫 Bloquear"
    BTN_DESBLOQUEAR_USUARIO = "✅ Desbloquear"
    BTN_EXPORTAR = "📤 Exportar"
    BTN_IMPORTAR = "📥 Importar"
    BTN_ACTUALIZAR = "🔄 Actualizar"
    
    # Headers de tabla
    HEADERS_USUARIOS = [
        "ID", "Usuario", "Nombre", "Email", "Rol", "Estado",
        "Último Acceso", "Intentos Fallidos", "Fecha Creación"
    ]
    
    # Roles de usuario
    ROLES = [
        "ADMINISTRADOR", "SUPERVISOR", "OPERADOR", 
        "CONSULTA", "INVITADO"
    ]
    
    # Estados de usuario
    ESTADOS_USUARIO = ["ACTIVO", "INACTIVO", "BLOQUEADO", "SUSPENDIDO"]
    
    # Niveles de permisos
    PERMISOS_LECTURA = "LECTURA"
    PERMISOS_ESCRITURA = "ESCRITURA"
    PERMISOS_ADMIN = "ADMINISTRADOR"
    PERMISOS_SUPER_ADMIN = "SUPER_ADMINISTRADOR"
    
    # Mensajes
    MSG_USUARIO_CREADO = "Usuario creado exitosamente"
    MSG_USUARIO_ACTUALIZADO = "Usuario actualizado exitosamente"
    MSG_USUARIO_ELIMINADO = "Usuario eliminado exitosamente"
    MSG_PASSWORD_CAMBIADO = "Contraseña cambiada exitosamente"
    MSG_USUARIO_BLOQUEADO = "Usuario bloqueado exitosamente"
    MSG_USUARIO_DESBLOQUEADO = "Usuario desbloqueado exitosamente"
    
    MSG_ERROR_CREAR_USUARIO = "Error al crear el usuario"
    MSG_ERROR_ACTUALIZAR_USUARIO = "Error al actualizar el usuario"
    MSG_ERROR_ELIMINAR_USUARIO = "Error al eliminar el usuario"
    MSG_ERROR_CAMBIAR_PASSWORD = "Error al cambiar la contraseña"
    
    MSG_SELECCIONAR_USUARIO = "Seleccione un usuario"
    MSG_CONFIRMAR_ELIMINACION = "¿Está seguro de eliminar este usuario?"
    MSG_CONFIRMAR_BLOQUEO = "¿Está seguro de bloquear este usuario?"
    
    # Validaciones de contraseña
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 128
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_NUMBERS = True
    REQUIRE_SPECIAL_CHARS = True
    
    # Validaciones de usuario
    MIN_USERNAME_LENGTH = 3
    MAX_USERNAME_LENGTH = 50
    MIN_NOMBRE_LENGTH = 2
    MAX_NOMBRE_LENGTH = 100
    
    # Configuraciones de seguridad
    MAX_INTENTOS_LOGIN = 5
    TIEMPO_BLOQUEO_MINUTOS = 30
    TIEMPO_SESION_MINUTOS = 480  # 8 horas
    DIAS_EXPIRACION_PASSWORD = 90
    
    # Placeholders
    PLACEHOLDER_USERNAME = "Nombre de usuario"
    PLACEHOLDER_EMAIL = "usuario@empresa.com"
    PLACEHOLDER_NOMBRE = "Nombre completo"
    PLACEHOLDER_PASSWORD = "Contraseña segura"
    PLACEHOLDER_CONFIRMAR_PASSWORD = "Confirmar contraseña"
    PLACEHOLDER_BUSCAR = "🔍 Buscar usuarios..."
    
    # Filtros
    FILTROS_ROL = ["Todos"] + ROLES
    FILTROS_ESTADO = ["Todos"] + ESTADOS_USUARIO
    FILTROS_ACTIVOS = ["Todos", "Solo Activos", "Solo Inactivos", "Solo Bloqueados"]
    
    # Configuraciones de tabla
    FILAS_POR_PAGINA = 25
    ANCHO_COLUMNA_USERNAME = 120
    ANCHO_COLUMNA_NOMBRE = 200
    ANCHO_COLUMNA_EMAIL = 200
    ANCHO_COLUMNA_ROL = 120
    ANCHO_COLUMNA_ESTADO = 100
    
    # Patrones de validación
    PATRON_EMAIL = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    PATRON_USERNAME = r'^[a-zA-Z0-9._-]{3,50}$'
    PATRON_PASSWORD_SEGURA = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    
    # Colores por estado
    COLOR_ACTIVO = "#4CAF50"     # Verde
    COLOR_INACTIVO = "#9E9E9E"   # Gris
    COLOR_BLOQUEADO = "#F44336"  # Rojo
    COLOR_SUSPENDIDO = "#FF9800" # Naranja
    
    # Configuraciones de auditoría
    EVENTOS_AUDITORIA = [
        "CREAR_USUARIO", "ACTUALIZAR_USUARIO", "ELIMINAR_USUARIO",
        "CAMBIAR_PASSWORD", "BLOQUEAR_USUARIO", "DESBLOQUEAR_USUARIO",
        "LOGIN_EXITOSO", "LOGIN_FALLIDO", "LOGOUT"
    ]
    
    # Configuraciones de exportación
    FORMATOS_EXPORTACION = ["Excel (.xlsx)", "CSV (.csv)", "PDF (.pdf)"]
    
    # Headers para exportación
    HEADERS_EXPORTACION = [
        "ID", "Usuario", "Nombre Completo", "Email", "Rol", 
        "Estado", "Fecha Creación", "Último Acceso"
    ]