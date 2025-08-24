#!/usr/bin/env python3
"""
Script para corregir completamente el controller de usuarios
"""

def fix_usuarios_controller():
    """Corrige todos los problemas del controller de usuarios"""
    
    content = '''"""
Controlador de Usuarios - Rexus.app v2.0.0

Maneja la lógica de negocio entre la vista y el modelo de usuarios.
Gestiona autenticación, autorización, permisos y sesiones de usuario.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

# Importar logging
try:
    from ...utils.app_logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

# Importar componentes base
try:
    from ...ui.base.base_controller import BaseController
except ImportError:
    logger.warning("No se pudo importar BaseController")
    
    class BaseController:
        """Clase base para controllers cuando no está disponible la importación."""
        def __init__(self, *args, **kwargs):
            pass
        
        def mostrar_error(self, titulo: str, mensaje: str) -> None:
            """Mostrar mensaje de error."""
            logger.error(f"{titulo}: {mensaje}")
        
        def mostrar_exito(self, mensaje: str) -> None:
            """Mostrar mensaje de éxito.""" 
            logger.info(mensaje)
        
        def mostrar_advertencia(self, mensaje: str) -> None:
            """Mostrar mensaje de advertencia."""
            logger.warning(mensaje)

# Constantes para mensajes de error
MSG_ERROR_CREANDO = "Error creando usuario"
MSG_ERROR_ACTUALIZANDO = "Error actualizando usuario" 
MSG_ERROR_ELIMINANDO = "Error eliminando usuario"
MSG_ERROR_PERMISOS = "Error actualizando permisos"


class UsuariosController(BaseController):
    """Controlador del módulo de usuarios."""
    
    def __init__(self, model=None, view=None, db_connection=None):
        """
        Inicializar controlador de usuarios.
        
        Args:
            model: Modelo de usuarios
            view: Vista de usuarios
            db_connection: Conexión a la base de datos
        """
        super().__init__()
        self.model = model
        self.view = view
        self.db_connection = db_connection
        self.usuario_actual = None
        self.sesion_activa = False
        
        self.conectar_senales()
        logger.info("UsuariosController inicializado")
    
    def conectar_senales(self):
        """Conecta las señales de la vista con los métodos del controlador."""
        try:
            if not self.view:
                return
                
            # Señales de autenticación
            if hasattr(self.view, 'login_signal'):
                self.view.login_signal.connect(self.autenticar_usuario)
            
            if hasattr(self.view, 'logout_signal'):
                self.view.logout_signal.connect(self.cerrar_sesion)
            
            # Señales de gestión de usuarios
            if hasattr(self.view, 'crear_usuario_signal'):
                self.view.crear_usuario_signal.connect(self.crear_usuario)
            
            if hasattr(self.view, 'actualizar_usuario_signal'):
                self.view.actualizar_usuario_signal.connect(self.actualizar_usuario)
            
            if hasattr(self.view, 'eliminar_usuario_signal'):
                self.view.eliminar_usuario_signal.connect(self.eliminar_usuario)
            
            if hasattr(self.view, 'buscar_usuarios_signal'):
                self.view.buscar_usuarios_signal.connect(self.buscar_usuarios)
            
            # Señales de permisos
            if hasattr(self.view, 'cambiar_permisos_signal'):
                self.view.cambiar_permisos_signal.connect(self.cambiar_permisos_usuario)
            
            logger.debug("Señales de usuarios conectadas")
            
        except Exception as e:
            logger.error(f"Error conectando señales de usuarios: {e}")
    
    def cargar_datos_iniciales(self):
        """Carga datos iniciales del módulo de usuarios."""
        try:
            if not self.model:
                logger.warning("No hay modelo de usuarios disponible")
                return
            
            # Cargar lista de usuarios
            self.cargar_usuarios()
            
            # Cargar estadísticas de usuarios
            self.cargar_estadisticas_usuarios()
            
            logger.debug("Datos iniciales de usuarios cargados")
            
        except Exception as e:
            logger.error(f"Error cargando datos iniciales de usuarios: {e}")
    
    # MÉTODOS DE AUTENTICACIÓN
    
    def autenticar_usuario(self, username: str, password: str) -> bool:
        """
        Autentica un usuario en el sistema.
        
        Args:
            username: Nombre de usuario
            password: Contraseña
            
        Returns:
            True si la autenticación es exitosa
        """
        try:
            if not self.model:
                logger.error("No hay modelo disponible para autenticación")
                return False
            
            # Validar credenciales
            if hasattr(self.model, 'validar_credenciales'):
                usuario = self.model.validar_credenciales(username, password)
            else:
                logger.error("Método validar_credenciales no disponible en modelo")
                return False
            
            if usuario:
                self.usuario_actual = usuario
                self.sesion_activa = True
                
                # Registrar auditoría de login
                self.registrar_auditoria("LOGIN", "USUARIOS", {
                    "usuario": username,
                    "fecha_login": datetime.now().isoformat()
                })
                
                logger.info(f"Usuario '{username}' autenticado exitosamente")
                return True
            else:
                logger.warning(f"Credenciales inválidas para usuario '{username}'")
                return False
                
        except Exception as e:
            logger.error(f"Error en autenticación: {e}")
            return False
    
    def cerrar_sesion(self) -> bool:
        """
        Cierra la sesión del usuario actual.
        
        Returns:
            True si se cerró exitosamente
        """
        try:
            if self.usuario_actual:
                # Registrar auditoría de logout
                self.registrar_auditoria("LOGOUT", "USUARIOS", {
                    "usuario": self.usuario_actual.get('username', 'DESCONOCIDO'),
                    "fecha_logout": datetime.now().isoformat()
                })
                
                logger.info(f"Sesión cerrada para usuario '{self.usuario_actual.get('username')}'")
                
            self.usuario_actual = None
            self.sesion_activa = False
            return True
            
        except Exception as e:
            logger.error(f"Error cerrando sesión: {e}")
            return False
    
    # MÉTODOS DE GESTIÓN DE USUARIOS
    
    def cargar_usuarios(self, filtros: Optional[Dict[str, Any]] = None):
        """
        Carga la lista de usuarios en la vista.
        
        Args:
            filtros: Filtros opcionales para la búsqueda
        """
        try:
            if not self.model:
                logger.warning("No hay modelo disponible para cargar usuarios")
                return
            
            if hasattr(self.model, 'obtener_usuarios'):
                usuarios = self.model.obtener_usuarios(filtros) if filtros else self.model.obtener_usuarios()
            else:
                logger.error("Método obtener_usuarios no disponible en modelo")
                usuarios = []
            
            if usuarios is not None:
                logger.debug(f"Cargados {len(usuarios)} usuarios")
                
                if self.view and hasattr(self.view, 'cargar_usuarios'):
                    self.view.cargar_usuarios(usuarios)
            else:
                logger.warning("No se pudieron obtener usuarios del modelo")
                
        except Exception as e:
            logger.error(f"Error cargando usuarios: {e}")
    
    def buscar_usuarios(self, filtros: Dict[str, Any]):
        """
        Busca usuarios con los filtros especificados.
        
        Args:
            filtros: Criterios de búsqueda
        """
        try:
            logger.debug(f"Buscando usuarios con filtros: {filtros}")
            self.cargar_usuarios(filtros)
        except Exception as e:
            logger.error(f"Error buscando usuarios: {e}")
    
    def crear_usuario(self, datos_usuario: Dict[str, Any]) -> bool:
        """
        Crea un nuevo usuario.
        
        Args:
            datos_usuario: Datos del usuario a crear
            
        Returns:
            True si se creó exitosamente
        """
        try:
            if not self.model:
                logger.error("No hay modelo disponible para crear usuario")
                return False
            
            # Validar datos del usuario
            if not self._validar_datos_usuario(datos_usuario):
                return False
            
            # Verificar si el username ya existe
            if hasattr(self.model, 'usuario_existe'):
                if self.model.usuario_existe(datos_usuario.get('username')):
                    logger.error("El nombre de usuario ya existe")
                    if self.view:
                        self.mostrar_error("Error", "El nombre de usuario ya existe")
                    return False
            
            # Crear usuario
            if hasattr(self.model, 'crear_usuario'):
                usuario_id = self.model.crear_usuario(datos_usuario)
            else:
                logger.error("Método crear_usuario no disponible en modelo")
                return False
            
            if usuario_id:
                # Registrar auditoría
                self.registrar_auditoria("CREATE_USER", "USUARIOS", {
                    "usuario_creado": datos_usuario.get('username'),
                    "por_usuario": self.usuario_actual.get('username') if self.usuario_actual else 'SISTEMA'
                })
                
                logger.info(f"Usuario '{datos_usuario.get('username')}' creado exitosamente")
                
                # Recargar lista de usuarios
                self.cargar_usuarios()
                
                if self.view:
                    self.mostrar_exito("Usuario creado exitosamente")
                
                return True
            else:
                logger.error(MSG_ERROR_CREANDO)
                if self.view:
                    self.mostrar_error("Error", MSG_ERROR_CREANDO)
                return False
                
        except Exception as e:
            logger.error(f"{MSG_ERROR_CREANDO}: {e}")
            if self.view:
                self.mostrar_error("Error", MSG_ERROR_CREANDO)
            return False
    
    def actualizar_usuario(self, usuario_id: int, datos_usuario: Dict[str, Any]) -> bool:
        """
        Actualiza un usuario existente.
        
        Args:
            usuario_id: ID del usuario
            datos_usuario: Nuevos datos del usuario
            
        Returns:
            True si se actualizó exitosamente
        """
        try:
            if not self.model:
                logger.error("No hay modelo disponible para actualizar usuario")
                return False
            
            # Validar datos del usuario
            if not self._validar_datos_usuario(datos_usuario, es_actualizacion=True):
                return False
            
            # Actualizar usuario
            if hasattr(self.model, 'actualizar_usuario'):
                exito = self.model.actualizar_usuario(usuario_id, datos_usuario)
            else:
                logger.error("Método actualizar_usuario no disponible en modelo")
                return False
            
            if exito:
                # Registrar auditoría
                self.registrar_auditoria("UPDATE_USER", "USUARIOS", {
                    "usuario_id": usuario_id,
                    "cambios": datos_usuario,
                    "por_usuario": self.usuario_actual.get('username') if self.usuario_actual else 'SISTEMA'
                })
                
                logger.info(f"Usuario ID {usuario_id} actualizado exitosamente")
                
                # Recargar lista de usuarios
                self.cargar_usuarios()
                
                if self.view:
                    self.mostrar_exito("Usuario actualizado exitosamente")
                
                return True
            else:
                logger.error(MSG_ERROR_ACTUALIZANDO)
                if self.view:
                    self.mostrar_error("Error", MSG_ERROR_ACTUALIZANDO)
                return False
                
        except Exception as e:
            logger.error(f"{MSG_ERROR_ACTUALIZANDO}: {e}")
            if self.view:
                self.mostrar_error("Error", MSG_ERROR_ACTUALIZANDO)
            return False
    
    def eliminar_usuario(self, usuario_id: int) -> bool:
        """
        Elimina un usuario del sistema.
        
        Args:
            usuario_id: ID del usuario a eliminar
            
        Returns:
            True si se eliminó exitosamente
        """
        try:
            if not self.model:
                logger.error("No hay modelo disponible para eliminar usuario")
                return False
            
            # Verificar que no se elimine el usuario actual
            if (self.usuario_actual and 
                self.usuario_actual.get('id') == usuario_id):
                logger.error("No se puede eliminar el usuario actual")
                if self.view:
                    self.mostrar_error("Error", "No se puede eliminar el usuario actual")
                return False
            
            # Eliminar usuario
            if hasattr(self.model, 'eliminar_usuario'):
                exito = self.model.eliminar_usuario(usuario_id)
            else:
                logger.error("Método eliminar_usuario no disponible en modelo")
                return False
            
            if exito:
                # Registrar auditoría
                self.registrar_auditoria("DELETE_USER", "USUARIOS", {
                    "usuario_id": usuario_id,
                    "por_usuario": self.usuario_actual.get('username') if self.usuario_actual else 'SISTEMA'
                })
                
                logger.info(f"Usuario ID {usuario_id} eliminado exitosamente")
                
                # Recargar lista de usuarios
                self.cargar_usuarios()
                
                if self.view:
                    self.mostrar_exito("Usuario eliminado exitosamente")
                
                return True
            else:
                logger.error(MSG_ERROR_ELIMINANDO)
                if self.view:
                    self.mostrar_error("Error", MSG_ERROR_ELIMINANDO)
                return False
                
        except Exception as e:
            logger.error(f"{MSG_ERROR_ELIMINANDO}: {e}")
            if self.view:
                self.mostrar_error("Error", MSG_ERROR_ELIMINANDO)
            return False
    
    # MÉTODOS DE PERMISOS
    
    def cambiar_permisos_usuario(self, usuario_id: int, permisos: Dict[str, bool]) -> bool:
        """
        Cambia los permisos de un usuario.
        
        Args:
            usuario_id: ID del usuario
            permisos: Diccionario con los permisos
            
        Returns:
            True si se actualizaron exitosamente
        """
        try:
            if not self.model:
                logger.error("No hay modelo disponible para cambiar permisos")
                return False
            
            # Actualizar permisos
            if hasattr(self.model, 'actualizar_permisos_usuario'):
                exito = self.model.actualizar_permisos_usuario(usuario_id, permisos)
            else:
                logger.error("Método actualizar_permisos_usuario no disponible en modelo")
                return False
            
            if exito:
                # Registrar auditoría
                self.registrar_auditoria("UPDATE_PERMISSIONS", "USUARIOS", {
                    "usuario_id": usuario_id,
                    "permisos": permisos,
                    "por_usuario": self.usuario_actual.get('username') if self.usuario_actual else 'SISTEMA'
                })
                
                logger.info(f"Permisos actualizados para usuario ID {usuario_id}")
                
                if self.view:
                    self.mostrar_exito("Permisos actualizados exitosamente")
                
                return True
            else:
                logger.error(MSG_ERROR_PERMISOS)
                if self.view:
                    self.mostrar_error("Error", MSG_ERROR_PERMISOS)
                return False
                
        except Exception as e:
            logger.error(f"{MSG_ERROR_PERMISOS}: {e}")
            if self.view:
                self.mostrar_error("Error", MSG_ERROR_PERMISOS)
            return False
    
    # MÉTODOS DE ESTADÍSTICAS
    
    def cargar_estadisticas_usuarios(self):
        """Carga estadísticas de usuarios en la vista."""
        try:
            if not self.model:
                logger.warning("No hay modelo disponible para estadísticas")
                return
            
            if hasattr(self.model, 'obtener_estadisticas_usuarios'):
                estadisticas = self.model.obtener_estadisticas_usuarios()
            else:
                logger.warning("Método obtener_estadisticas_usuarios no disponible")
                estadisticas = {}
            
            if estadisticas and self.view and hasattr(self.view, 'actualizar_estadisticas'):
                self.view.actualizar_estadisticas(estadisticas)
                
        except Exception as e:
            logger.error(f"Error cargando estadísticas de usuarios: {e}")
    
    # MÉTODOS DE VALIDACIÓN
    
    def _validar_datos_usuario(self, datos: Dict[str, Any], es_actualizacion: bool = False) -> bool:
        """
        Valida los datos de un usuario.
        
        Args:
            datos: Datos del usuario a validar
            es_actualizacion: Si es una actualización o creación
            
        Returns:
            True si los datos son válidos
        """
        try:
            # Validaciones básicas
            if not es_actualizacion:
                if not datos.get('username'):
                    logger.error("El nombre de usuario es requerido")
                    if self.view:
                        self.mostrar_error("Error", "El nombre de usuario es requerido")
                    return False
                
                if not datos.get('password'):
                    logger.error("La contraseña es requerida")
                    if self.view:
                        self.mostrar_error("Error", "La contraseña es requerida")
                    return False
            
            if not datos.get('email'):
                logger.error("El email es requerido")
                if self.view:
                    self.mostrar_error("Error", "El email es requerido")
                return False
            
            # Validar formato de email
            email = datos.get('email', '')
            if email and '@' not in email:
                logger.error("El formato del email es inválido")
                if self.view:
                    self.mostrar_error("Error", "El formato del email es inválido")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validando datos de usuario: {e}")
            return False
    
    # MÉTODOS DE AUDITORÍA
    
    def registrar_auditoria(self, accion: str, tabla: str, datos: Dict[str, Any]):
        """
        Registra una acción de auditoría.
        
        Args:
            accion: Tipo de acción realizada
            tabla: Tabla afectada
            datos: Datos de la auditoría
        """
        try:
            if self.model and hasattr(self.model, 'registrar_auditoria'):
                self.model.registrar_auditoria(accion, tabla, datos)
            else:
                logger.debug(f"Auditoría no disponible: {accion} en {tabla}")
                
        except Exception as e:
            logger.error(f"Error registrando auditoría: {e}")
    
    # MÉTODOS PÚBLICOS
    
    def obtener_usuario_actual(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene el usuario actualmente autenticado.
        
        Returns:
            Datos del usuario actual o None si no hay sesión activa
        """
        return self.usuario_actual if self.sesion_activa else None
    
    def verificar_permisos(self, permiso: str) -> bool:
        """
        Verifica si el usuario actual tiene un permiso específico.
        
        Args:
            permiso: Nombre del permiso a verificar
            
        Returns:
            True si tiene el permiso
        """
        try:
            if not self.usuario_actual or not self.sesion_activa:
                return False
            
            permisos = self.usuario_actual.get('permisos', {})
            return permisos.get(permiso, False)
            
        except Exception as e:
            logger.error(f"Error verificando permisos: {e}")
            return False
    
    def es_admin(self) -> bool:
        """
        Verifica si el usuario actual es administrador.
        
        Returns:
            True si es administrador
        """
        try:
            if not self.usuario_actual or not self.sesion_activa:
                return False
            
            return self.usuario_actual.get('es_admin', False)
            
        except Exception as e:
            logger.error(f"Error verificando si es admin: {e}")
            return False
'''
    
    # Escribir archivo corregido
    with open('rexus/modules/usuarios/controller.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Controller de usuarios corregido completamente")

if __name__ == '__main__':
    fix_usuarios_controller()
