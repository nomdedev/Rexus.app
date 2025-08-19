"""
Constantes para el módulo de Usuarios - Rexus.app

Centraliza strings, configuraciones y constantes para evitar 
duplicación y facilitar mantenimiento.
"""

class UsuariosConstants:
    """Constantes del módulo de usuarios."""

    # Títulos y etiquetas
    TITULO_MODULO = "[USERS] Gestión de Usuarios"
    
    # Botones
    BTN_NUEVO_USUARIO = "➕ Nuevo Usuario"
    BTN_EDITAR_USUARIO = "✏️ Editar"
    BTN_ELIMINAR_USUARIO = "🗑️ Eliminar"
    BTN_CAMBIAR_PASSWORD = "🔐 Cambiar Contraseña"
    BTN_BLOQUEAR_USUARIO = "🚫 Bloquear"
    BTN_DESBLOQUEAR_USUARIO = "[CHECK] Desbloquear"
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
    
    # Mensajes de éxito
    MSG_USUARIO_CREADO = "Usuario creado exitosamente"
    MSG_USUARIO_ACTUALIZADO = "Usuario actualizado exitosamente"
    MSG_USUARIO_ELIMINADO = "Usuario eliminado exitosamente"
    MSG_PASSWORD_CAMBIADO = "Contraseña cambiada exitosamente"
    MSG_USUARIO_BLOQUEADO = "Usuario bloqueado exitosamente"
    MSG_USUARIO_DESBLOQUEADO = "Usuario desbloqueado exitosamente"
    
    # Mensajes de error generales
    MSG_ERROR_CREAR_USUARIO = "Error al crear el usuario"
    MSG_ERROR_ACTUALIZAR_USUARIO = "Error al actualizar el usuario"
    MSG_ERROR_ELIMINAR_USUARIO = "Error al eliminar el usuario"
    MSG_ERROR_CAMBIAR_PASSWORD = "Error al cambiar la contraseña"
    MSG_ERROR_CARGAR_USUARIOS = "Error cargando usuarios"
    MSG_ERROR_BUSCAR_USUARIOS = "Error al buscar usuarios"
    MSG_ERROR_AUTENTICAR = "Error autenticando usuario"
    MSG_ERROR_BLOQUEAR = "Error bloqueando usuario"
    MSG_ERROR_DESBLOQUEAR = "Error desbloqueando usuario"
    MSG_ERROR_OBTENER_PERMISOS = "Error obteniendo permisos"
    MSG_ERROR_OBTENER_ESTADISTICAS = "Error obteniendo estadísticas"
    
    # Mensajes de error específicos de base de datos
    MSG_ERROR_BD_CONEXION = "Error de conexión a la base de datos"
    MSG_ERROR_BD_CONSULTA = "Error ejecutando consulta de base de datos"
    MSG_ERROR_BD_TRANSACCION = "Error en transacción de base de datos"
    
    # Mensajes de error de seguridad
    MSG_ERROR_SEGURIDAD_CRITICA = "Error crítico de seguridad"
    MSG_ERROR_SEGURIDAD_INPUT = "Input malicioso detectado"
    MSG_ERROR_SEGURIDAD_AUTH = "Error de autenticación"
    MSG_ERROR_SEGURIDAD_PERMISOS = "Error de permisos"
    
    # Mensajes de error de 2FA
    MSG_ERROR_2FA_GENERAR = "Error generando 2FA"
    MSG_ERROR_2FA_VERIFICAR = "Error verificando 2FA"
    MSG_ERROR_2FA_DESHABILITAR = "Error deshabilitando 2FA"
    MSG_ERROR_2FA_CODIGO_INVALIDO = "Código incorrecto. Verifique e intente nuevamente"
    MSG_ERROR_2FA_CODIGO_FORMATO = "Ingrese un código de 6 dígitos"
    
    # Mensajes de validación
    MSG_ERROR_PASSWORD_ACTUAL = "Ingrese su contraseña actual"
    MSG_ERROR_PASSWORD_NO_COINCIDEN = "Las contraseñas no coinciden"
    MSG_ERROR_PASSWORD_INCORRECTA = "Contraseña actual incorrecta"
    
    # Mensajes de UI
    MSG_SELECCIONAR_USUARIO = "Seleccione un usuario"
    MSG_CONFIRMAR_ELIMINACION = "¿Está seguro de eliminar este usuario?"
    MSG_CONFIRMAR_BLOQUEO = "¿Está seguro de bloquear este usuario?"
    
    # Títulos de ventanas de error
    TITULO_ERROR = "Error"
    TITULO_ADVERTENCIA = "Advertencia"
    TITULO_CONFIRMACION = "Confirmación"
    TITULO_EXITO = "Éxito"
    
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
    PLACEHOLDER_BUSCAR = "[SEARCH] Buscar usuarios..."
    
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