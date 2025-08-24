"""
Controlador de Usuarios - Rexus.app v2.0.0

Maneja la lógica de negocio entre la vista y el modelo de usuarios.
Gestiona autenticación, autorización, permisos y sesiones de usuario.
"""

import logging
from typing import Dict, List, Any, Optional
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
    BaseController = object


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
            if self.view and hasattr(self.view, 'connect_signals'):
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
            
        except (AttributeError, TypeError) as e:
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
            usuario = self.model.validar_credenciales(username, password)
            
            if usuario:
                self.usuario_actual = usuario
                self.sesion_activa = True
                
                # Registrar inicio de sesión
                self.registrar_auditoria("LOGIN", "USUARIOS", {
                    "usuario": username,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Actualizar última conexión
                self.model.actualizar_ultima_conexion(usuario['id'])
                
                logger.info(f"Usuario '{username}' autenticado exitosamente")
                
                if self.view:
                    self.view.on_login_successful(usuario)
                
                return True
            else:
                logger.warning(f"Intento de login fallido para usuario '{username}'")
                
                # Registrar intento fallido
                self.registrar_auditoria("LOGIN_FAILED", "USUARIOS", {
                    "usuario": username,
                    "timestamp": datetime.now().isoformat()
                })
                
                if self.view:
                    self.view.mostrar_error("Credenciales incorrectas")
                
                return False
                
        except Exception as e:
            logger.error(f"Error autenticando usuario: {e}")
            if self.view:
                self.view.mostrar_error("Error de autenticación")
            return False
    
    def cerrar_sesion(self):
        """Cierra la sesión actual del usuario."""
        try:
            if self.usuario_actual:
                # Registrar cierre de sesión
                self.registrar_auditoria("LOGOUT", "USUARIOS", {
                    "usuario": self.usuario_actual.get('username'),
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.info(f"Sesión cerrada para usuario '{self.usuario_actual.get('username')}'")
                
                self.usuario_actual = None
                self.sesion_activa = False
                
                if self.view:
                    self.view.on_logout_successful()
                
        except Exception as e:
            logger.error(f"Error cerrando sesión: {e}")
    
    # MÉTODOS DE GESTIÓN DE USUARIOS
    
    def cargar_usuarios(self, filtros: Optional[Dict[str, Any]] = None):
        """
        Carga usuarios en la vista.
        
        Args:
            filtros: Filtros opcionales para la consulta
        """
        try:
            if not self.model or not self.view:
                return
            
            # Obtener usuarios del modelo
            if filtros:
                usuarios = self.model.obtener_usuarios_filtrados(filtros)
            else:
                usuarios = self.model.obtener_todos_usuarios()
            
            # Actualizar vista
            if hasattr(self.view, 'cargar_datos_en_tabla'):
                self.view.cargar_datos_en_tabla(usuarios)
            
            logger.debug(f"Cargados {len(usuarios)} usuarios")
            
        except Exception as e:
            logger.error(f"Error cargando usuarios: {e}")
    
    def buscar_usuarios(self, filtros: Dict[str, Any]):
        """
        Busca usuarios con filtros específicos.
        
        Args:
            filtros: Diccionario con filtros de búsqueda
        """
        try:
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
            if self.model.usuario_existe(datos_usuario.get('username')):
                logger.error("El nombre de usuario ya existe")
                if self.view:
                    self.view.mostrar_error("El nombre de usuario ya existe")
                return False
            
            # Crear usuario
            usuario_id = self.model.crear_usuario(datos_usuario)
            
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
                    self.view.mostrar_mensaje("Usuario creado exitosamente")
                
                return True
            else:
                logger.error("Error creando usuario")
                if self.view:
                    self.view.mostrar_error("Error creando usuario")
                return False
                
        except Exception as e:
            logger.error(f"Error creando usuario: {e}")
            if self.view:
                self.view.mostrar_error("Error creando usuario")
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
            if self.model.actualizar_usuario(usuario_id, datos_usuario):
                # Registrar auditoría
                self.registrar_auditoria("UPDATE_USER", "USUARIOS", {
                    "usuario_actualizado": datos_usuario.get('username'),
                    "por_usuario": self.usuario_actual.get('username') if self.usuario_actual else 'SISTEMA'
                })
                
                logger.info(f"Usuario ID {usuario_id} actualizado exitosamente")
                
                # Recargar lista de usuarios
                self.cargar_usuarios()
                
                if self.view:
                    self.view.mostrar_mensaje("Usuario actualizado exitosamente")
                
                return True
            else:
                logger.error("Error actualizando usuario")
                if self.view:
                    self.view.mostrar_error("Error actualizando usuario")
                return False
                
        except Exception as e:
            logger.error(f"Error actualizando usuario: {e}")
            if self.view:
                self.view.mostrar_error("Error actualizando usuario")
            return False
    
    def eliminar_usuario(self, usuario_id: int) -> bool:
        """
        Elimina un usuario.
        
        Args:
            usuario_id: ID del usuario a eliminar
            
        Returns:
            True si se eliminó exitosamente
        """
        try:
            if not self.model:
                logger.error("No hay modelo disponible para eliminar usuario")
                return False
            
            # Obtener datos del usuario antes de eliminar
            usuario = self.model.obtener_usuario_por_id(usuario_id)
            if not usuario:
                logger.error("Usuario no encontrado")
                return False
            
            # No permitir eliminar el usuario actual
            if self.usuario_actual and usuario.get('id') == self.usuario_actual.get('id'):
                logger.error("No se puede eliminar el usuario actualmente logueado")
                if self.view:
                    self.view.mostrar_error("No se puede eliminar el usuario actual")
                return False
            
            # Eliminar usuario
            if self.model.eliminar_usuario(usuario_id):
                # Registrar auditoría
                self.registrar_auditoria("DELETE_USER", "USUARIOS", {
                    "usuario_eliminado": usuario.get('username'),
                    "por_usuario": self.usuario_actual.get('username') if self.usuario_actual else 'SISTEMA'
                })
                
                logger.info(f"Usuario '{usuario.get('username')}' eliminado exitosamente")
                
                # Recargar lista de usuarios
                self.cargar_usuarios()
                
                if self.view:
                    self.view.mostrar_mensaje("Usuario eliminado exitosamente")
                
                return True
            else:
                logger.error("Error eliminando usuario")
                if self.view:
                    self.view.mostrar_error("Error eliminando usuario")
                return False
                
        except Exception as e:
            logger.error(f"Error eliminando usuario: {e}")
            if self.view:
                self.view.mostrar_error("Error eliminando usuario")
            return False
    
    # MÉTODOS DE PERMISOS
    
    def cambiar_permisos_usuario(self, usuario_id: int, permisos: Dict[str, bool]) -> bool:
        """
        Cambia los permisos de un usuario.
        
        Args:
            usuario_id: ID del usuario
            permisos: Diccionario con permisos
            
        Returns:
            True si se cambiaron exitosamente
        """
        try:
            if not self.model:
                logger.error("No hay modelo disponible para cambiar permisos")
                return False
            
            if self.model.actualizar_permisos_usuario(usuario_id, permisos):
                # Registrar auditoría
                usuario = self.model.obtener_usuario_por_id(usuario_id)
                self.registrar_auditoria("UPDATE_PERMISSIONS", "USUARIOS", {
                    "usuario": usuario.get('username') if usuario else usuario_id,
                    "permisos": permisos,
                    "por_usuario": self.usuario_actual.get('username') if self.usuario_actual else 'SISTEMA'
                })
                
                logger.info(f"Permisos actualizados para usuario ID {usuario_id}")
                
                if self.view:
                    self.view.mostrar_mensaje("Permisos actualizados exitosamente")
                
                return True
            else:
                logger.error("Error actualizando permisos")
                if self.view:
                    self.view.mostrar_error("Error actualizando permisos")
                return False
                
        except Exception as e:
            logger.error(f"Error actualizando permisos: {e}")
            if self.view:
                self.view.mostrar_error("Error actualizando permisos")
            return False
    
    # MÉTODOS AUXILIARES
    
    def cargar_estadisticas_usuarios(self):
        """Carga estadísticas de usuarios para el dashboard."""
        try:
            if not self.model or not self.view:
                return
            
            # Obtener estadísticas del modelo
            estadisticas = self.model.obtener_estadisticas_usuarios()
            
            # Actualizar vista
            if hasattr(self.view, 'actualizar_estadisticas'):
                self.view.actualizar_estadisticas(estadisticas)
            
            logger.debug("Estadísticas de usuarios actualizadas")
            
        except Exception as e:
            logger.error(f"Error cargando estadísticas de usuarios: {e}")
    
    def _validar_datos_usuario(self, datos: Dict[str, Any], es_actualizacion: bool = False) -> bool:
        """
        Valida los datos de un usuario.
        
        Args:
            datos: Datos del usuario a validar
            es_actualizacion: Si es una actualización
            
        Returns:
            True si los datos son válidos
        """
        try:
            # Validaciones básicas
            if not es_actualizacion:  # Para creación, username es obligatorio
                if not datos.get('username'):
                    logger.error("Nombre de usuario es requerido")
                    if self.view:
                        self.view.mostrar_error("Nombre de usuario es requerido")
                    return False
            
            if not datos.get('email'):
                logger.error("Email es requerido")
                if self.view:
                    self.view.mostrar_error("Email es requerido")
                return False
            
            # Validar formato de email
            if '@' not in datos.get('email', ''):
                logger.error("Formato de email inválido")
                if self.view:
                    self.view.mostrar_error("Formato de email inválido")
                return False
            
            # Si hay contraseña, validar longitud mínima
            password = datos.get('password')
            if password and len(password) < 6:
                logger.error("La contraseña debe tener al menos 6 caracteres")
                if self.view:
                    self.view.mostrar_error("La contraseña debe tener al menos 6 caracteres")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validando datos de usuario: {e}")
            return False
    
    def registrar_auditoria(self, accion: str, modulo: str, detalles: Dict[str, Any]):
        """
        Registra una acción en el log de auditoría.
        
        Args:
            accion: Tipo de acción realizada
            modulo: Módulo donde se realizó la acción
            detalles: Detalles adicionales de la acción
        """
        try:
            # Aquí se podría integrar con el módulo de auditoría
            logger.info(f"AUDITORIA: {accion} - {modulo} - {detalles}")
            
            # Si hay modelo de auditoría disponible, usarlo
            if hasattr(self, 'auditoria_model') and self.auditoria_model:
                self.auditoria_model.registrar_evento(
                    accion=accion,
                    modulo=modulo,
                    usuario=self.usuario_actual.get('username') if self.usuario_actual else 'SISTEMA',
                    detalles=detalles
                )
                
        except Exception as e:
            logger.error(f"Error registrando auditoría: {e}")
    
    def verificar_permisos(self, permiso_requerido: str) -> bool:
        """
        Verifica si el usuario actual tiene un permiso específico.
        
        Args:
            permiso_requerido: Permiso a verificar
            
        Returns:
            True si el usuario tiene el permiso
        """
        try:
            if not self.usuario_actual or not self.sesion_activa:
                return False
            
            if not self.model:
                return False
            
            return self.model.usuario_tiene_permiso(
                self.usuario_actual['id'], 
                permiso_requerido
            )
            
        except Exception as e:
            logger.error(f"Error verificando permisos: {e}")
            return False
    
    def obtener_usuario_actual(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene el usuario actualmente logueado.
        
        Returns:
            Datos del usuario actual o None
        """
        return self.usuario_actual if self.sesion_activa else None