"""
Constantes para el módulo de Usuarios - Rexus.app

Centraliza strings, configuraciones y constantes para evitar 
duplicación y facilitar mantenimiento.
"""

import logging
logger = logging.getLogger(__name__)


class UsuariosConstants:
    """Constantes para el módulo de usuarios."""
    
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
    
    # Estados de usuario
    ESTADO_ACTIVO = "ACTIVO"
    ESTADO_BLOQUEADO = "BLOQUEADO"
    ESTADO_INACTIVO = "INACTIVO"
    ESTADO_PENDIENTE = "PENDIENTE"
    
    # Roles disponibles
    ROL_ADMIN = "ADMINISTRADOR"
    ROL_USUARIO = "USUARIO"
    ROL_SUPERVISOR = "SUPERVISOR"
    ROL_AUDITOR = "AUDITOR"
    
    ROLES_DISPONIBLES = [ROL_ADMIN, ROL_SUPERVISOR, ROL_USUARIO, ROL_AUDITOR]
    
    # Configuraciones de seguridad
    MAX_INTENTOS_LOGIN = 3
    DURACION_BLOQUEO_MINUTOS = 30
    MIN_LONGITUD_PASSWORD = 8
    REQUERIR_MAYUSCULA = True
    REQUERIR_MINUSCULA = True
    REQUERIR_NUMERO = True
    REQUERIR_CARACTER_ESPECIAL = True
    
    # Mensajes de validación
    MSG_PASSWORD_MUY_CORTA = f"La contraseña debe tener al menos {MIN_LONGITUD_PASSWORD} caracteres"
    MSG_PASSWORD_FALTA_MAYUSCULA = "La contraseña debe contener al menos una letra mayúscula"
    MSG_PASSWORD_FALTA_MINUSCULA = "La contraseña debe contener al menos una letra minúscula"
    MSG_PASSWORD_FALTA_NUMERO = "La contraseña debe contener al menos un número"
    MSG_PASSWORD_FALTA_ESPECIAL = "La contraseña debe contener al menos un carácter especial"
    
    # Mensajes de error
    MSG_ERROR_USUARIO_EXISTENTE = "Ya existe un usuario con ese nombre"
    MSG_ERROR_EMAIL_EXISTENTE = "Ya existe un usuario con ese email"
    MSG_ERROR_CREDENCIALES_INVALIDAS = "Usuario o contraseña incorrectos"
    MSG_ERROR_USUARIO_BLOQUEADO = "Usuario temporalmente bloqueado por múltiples intentos fallidos"
    MSG_ERROR_PERMISOS_INSUFICIENTES = "No tiene permisos para realizar esta acción"
    
    # Mensajes de éxito
    MSG_USUARIO_CREADO = "Usuario creado exitosamente"
    MSG_USUARIO_ACTUALIZADO = "Usuario actualizado exitosamente"
    MSG_USUARIO_ELIMINADO = "Usuario eliminado exitosamente"
    MSG_PASSWORD_ACTUALIZADA = "Contraseña actualizada exitosamente"