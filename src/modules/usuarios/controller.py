"""
Controlador de Usuarios - Rexus.app v2.0.0

Maneja la lógica de negocio entre la vista y el modelo de usuarios.
"""

from typing import Any, Dict, List, Optional
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox

from .model import UsuariosModel


class UsuariosController(QObject):
    """Controlador para el módulo de usuarios."""
    
    # Señales para comunicación con otros módulos
    usuario_creado = pyqtSignal(dict)
    usuario_actualizado = pyqtSignal(dict)
    usuario_eliminado = pyqtSignal(str)
    sesion_iniciada = pyqtSignal(dict)
    sesion_terminada = pyqtSignal(str)
    
    def __init__(self, view=None, db_connection=None, usuario_actual=None):
        super().__init__()
        self.view = view
        self.db_connection = db_connection
        self.usuario_actual = usuario_actual or {"id": 1, "nombre": "SISTEMA"}
        
        # Inicializar modelo
        self.model = UsuariosModel(db_connection)
        
        # Conectar señales si hay vista
        if self.view:
            self.conectar_señales()
            self.cargar_usuarios()
    
    def conectar_señales(self):
        """Conecta las señales entre vista y controlador."""
        if not self.view:
            return
            
        # Señales de la vista
        if hasattr(self.view, 'solicitud_crear_usuario'):
            self.view.solicitud_crear_usuario.connect(self.crear_usuario)
        if hasattr(self.view, 'solicitud_actualizar_usuario'):
            self.view.solicitud_actualizar_usuario.connect(self.actualizar_usuario)
        if hasattr(self.view, 'solicitud_eliminar_usuario'):
            self.view.solicitud_eliminar_usuario.connect(self.eliminar_usuario)
        
        # Establecer controlador en la vista
        self.view.set_controller(self)
    
    def cargar_usuarios(self):
        """Carga los usuarios desde el modelo."""
        try:
            usuarios = self.model.obtener_todos_usuarios()
            
            if self.view and hasattr(self.view, 'cargar_usuarios_en_tabla'):
                self.view.cargar_usuarios_en_tabla(usuarios)
            
            print(f"[USUARIOS CONTROLLER] Cargados {len(usuarios)} usuarios")
            
        except Exception as e:
            print(f"[ERROR USUARIOS CONTROLLER] Error cargando usuarios: {e}")
            self.mostrar_error(f"Error cargando usuarios: {str(e)}")
    
    def crear_usuario(self, datos_usuario: Dict[str, Any]):
        """Crea un nuevo usuario."""
        try:
            # Validar datos
            if not self.validar_datos_usuario(datos_usuario):
                return
                
            # Crear usuario
            exito, mensaje = self.model.crear_usuario(datos_usuario)
            
            if exito:
                self.mostrar_exito(mensaje)
                self.cargar_usuarios()
                
                # Emitir señal
                usuario_creado = self.model.obtener_usuario_por_nombre(datos_usuario["username"])
                if usuario_creado:
                    self.usuario_creado.emit(usuario_creado)
            else:
                self.mostrar_error(mensaje)
                
        except Exception as e:
            print(f"[ERROR USUARIOS CONTROLLER] Error creando usuario: {e}")
            self.mostrar_error(f"Error creando usuario: {str(e)}")
    
    def actualizar_usuario(self, datos_usuario: Dict[str, Any]):
        """Actualiza un usuario existente."""
        try:
            if not datos_usuario.get("id"):
                self.mostrar_error("ID de usuario requerido para actualización")
                return
                
            # Validar datos
            if not self.validar_datos_usuario(datos_usuario, es_actualizacion=True):
                return
                
            # Actualizar usuario
            exito, mensaje = self.model.actualizar_usuario(datos_usuario["id"], datos_usuario)
            
            if exito:
                self.mostrar_exito(mensaje)
                self.cargar_usuarios()
                
                # Emitir señal
                usuario_actualizado = self.model.obtener_usuario_por_id(datos_usuario["id"])
                if usuario_actualizado:
                    self.usuario_actualizado.emit(usuario_actualizado)
            else:
                self.mostrar_error(mensaje)
                
        except Exception as e:
            print(f"[ERROR USUARIOS CONTROLLER] Error actualizando usuario: {e}")
            self.mostrar_error(f"Error actualizando usuario: {str(e)}")
    
    def eliminar_usuario(self, usuario_id: str):
        """Elimina un usuario."""
        try:
            # Confirmar eliminación
            if self.view:
                respuesta = QMessageBox.question(
                    self.view,
                    "Confirmar eliminación",
                    f"¿Está seguro de eliminar el usuario con ID {usuario_id}?\n\n"
                    "Esta acción no se puede deshacer.",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                
                if respuesta == QMessageBox.StandardButton.Yes:
                    # Eliminar usuario
                    exito, mensaje = self.model.eliminar_usuario(int(usuario_id))
                    
                    if exito:
                        self.mostrar_exito(mensaje)
                        self.cargar_usuarios()
                        self.usuario_eliminado.emit(usuario_id)
                    else:
                        self.mostrar_error(mensaje)
                
        except Exception as e:
            print(f"[ERROR USUARIOS CONTROLLER] Error eliminando usuario: {e}")
            self.mostrar_error(f"Error eliminando usuario: {str(e)}")
    
    def cambiar_password(self, usuario_id: int, password_actual: str, password_nueva: str):
        """Cambia la contraseña de un usuario."""
        try:
            exito, mensaje = self.model.cambiar_password(usuario_id, password_actual, password_nueva)
            
            if exito:
                self.mostrar_exito(mensaje)
            else:
                self.mostrar_error(mensaje)
                
        except Exception as e:
            print(f"[ERROR USUARIOS CONTROLLER] Error cambiando contraseña: {e}")
            self.mostrar_error(f"Error cambiando contraseña: {str(e)}")
    
    def resetear_password(self, usuario_id: int, nueva_password: str):
        """Resetea la contraseña de un usuario (para administradores)."""
        try:
            datos_actualizacion = {"password": nueva_password}
            exito, mensaje = self.model.actualizar_usuario(usuario_id, datos_actualizacion)
            
            if exito:
                self.mostrar_exito("Contraseña reseteada exitosamente")
                # Registrar en auditoría
                self.registrar_auditoria(
                    f"Reset de contraseña para usuario ID {usuario_id}",
                    "usuarios",
                    {"admin_id": self.usuario_actual.get("id"), "target_user": usuario_id}
                )
            else:
                self.mostrar_error(mensaje)
                
        except Exception as e:
            print(f"[ERROR USUARIOS CONTROLLER] Error reseteando contraseña: {e}")
            self.mostrar_error(f"Error reseteando contraseña: {str(e)}")
    
    def obtener_estadisticas_usuarios(self) -> Dict[str, Any]:
        """Obtiene estadísticas de usuarios."""
        try:
            return self.model.obtener_estadisticas_usuarios()
        except Exception as e:
            print(f"[ERROR USUARIOS CONTROLLER] Error obteniendo estadísticas: {e}")
            return {}
    
    def obtener_usuario_por_id(self, usuario_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un usuario por su ID."""
        try:
            return self.model.obtener_usuario_por_id(usuario_id)
        except Exception as e:
            print(f"[ERROR USUARIOS CONTROLLER] Error obteniendo usuario: {e}")
            return None
    
    def obtener_permisos_usuario(self, usuario_id: int) -> List[str]:
        """Obtiene los permisos de un usuario."""
        try:
            return self.model.obtener_permisos_usuario(usuario_id)
        except Exception as e:
            print(f"[ERROR USUARIOS CONTROLLER] Error obteniendo permisos: {e}")
            return []
    
    def validar_datos_usuario(self, datos: Dict[str, Any], es_actualizacion: bool = False) -> bool:
        """Valida los datos del usuario."""
        errores = []
        
        # Validaciones básicas
        if not datos.get("username"):
            errores.append("Nombre de usuario es obligatorio")
        elif len(datos["username"]) < 3:
            errores.append("Nombre de usuario debe tener al menos 3 caracteres")
            
        if not datos.get("nombre_completo"):
            errores.append("Nombre completo es obligatorio")
            
        # Validar contraseña solo si se proporciona
        if datos.get("password"):
            password = datos["password"]
            if len(password) < 6:
                errores.append("La contraseña debe tener al menos 6 caracteres")
            if not any(c.isdigit() for c in password):
                errores.append("La contraseña debe contener al menos un número")
        elif not es_actualizacion:
            errores.append("Contraseña es obligatoria para usuarios nuevos")
        
        # Validar email si se proporciona
        if datos.get("email"):
            email = datos["email"]
            if "@" not in email or "." not in email:
                errores.append("Formato de email inválido")
        
        # Validar rol
        if not datos.get("rol"):
            errores.append("Rol es obligatorio")
        elif datos["rol"] not in self.model.ROLES:
            errores.append(f"Rol inválido. Debe ser uno de: {', '.join(self.model.ROLES.keys())}")
        
        # Validar estado
        if datos.get("estado") and datos["estado"] not in self.model.ESTADOS:
            errores.append(f"Estado inválido. Debe ser uno de: {', '.join(self.model.ESTADOS.keys())}")
        
        # Validar permisos
        if datos.get("permisos"):
            permisos = datos["permisos"]
            if not isinstance(permisos, list):
                errores.append("Permisos debe ser una lista")
            else:
                for permiso in permisos:
                    if permiso not in self.model.MODULOS_SISTEMA:
                        errores.append(f"Permiso inválido: {permiso}")
        
        if errores:
            mensaje_error = "Errores de validación:\n\n" + "\n".join(
                f"• {error}" for error in errores
            )
            self.mostrar_error(mensaje_error)
            return False
            
        return True
    
    def autenticar_usuario(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Autentica un usuario y devuelve sus datos."""
        try:
            usuario = self.model.obtener_usuario_por_nombre(username)
            
            if not usuario:
                return None
                
            # Verificar contraseña
            if not self.model._verificar_password(password, usuario["password_hash"]):
                return None
                
            # Actualizar último acceso
            self.model.actualizar_usuario(usuario["id"], {"ultimo_acceso": "NOW()"})
            
            # Registrar auditoría
            self.registrar_auditoria(
                f"Inicio de sesión exitoso",
                "usuarios",
                {"usuario_id": usuario["id"], "username": username}
            )
            
            return usuario
            
        except Exception as e:
            print(f"[ERROR USUARIOS CONTROLLER] Error autenticando usuario: {e}")
            return None
    
    def registrar_auditoria(self, accion: str, modulo: str, detalles: Dict[str, Any]):
        """Registra una acción en el log de auditoría."""
        try:
            # Aquí se podría integrar con el módulo de auditoría
            print(f"[AUDITORIA] {accion} - {modulo} - {detalles}")
        except Exception as e:
            print(f"[ERROR USUARIOS CONTROLLER] Error registrando auditoría: {e}")
    
    def obtener_roles_disponibles(self) -> List[str]:
        """Obtiene la lista de roles disponibles."""
        return list(self.model.ROLES.keys())
    
    def obtener_estados_disponibles(self) -> List[str]:
        """Obtiene la lista de estados disponibles."""
        return list(self.model.ESTADOS.keys())
    
    def obtener_modulos_sistema(self) -> List[str]:
        """Obtiene la lista de módulos del sistema."""
        return self.model.MODULOS_SISTEMA
    
    def set_usuario_actual(self, usuario: Dict[str, Any]):
        """Establece el usuario actual."""
        self.usuario_actual = usuario
        print(f"[USUARIOS CONTROLLER] Usuario actual: {usuario.get('nombre_completo', 'Desconocido')}")
    
    def mostrar_exito(self, mensaje: str):
        """Muestra un mensaje de éxito."""
        if self.view:
            QMessageBox.information(self.view, "Éxito", mensaje)
    
    def mostrar_error(self, mensaje: str):
        """Muestra un mensaje de error."""
        if self.view:
            QMessageBox.critical(self.view, "Error", mensaje)
    
    def mostrar_advertencia(self, mensaje: str):
        """Muestra un mensaje de advertencia."""
        if self.view:
            QMessageBox.warning(self.view, "Advertencia", mensaje)
    
    def mostrar_info(self, mensaje: str):
        """Muestra un mensaje informativo."""
        if self.view:
            QMessageBox.information(self.view, "Información", mensaje)
    
    def get_view(self):
        """Retorna la vista del módulo."""
        return self.view
    
    def cleanup(self):
        """Limpia recursos al cerrar el módulo."""
        try:
            print("[USUARIOS CONTROLLER] Limpiando recursos...")
            # Desconectar señales si es necesario
            # Cerrar conexiones, etc.
        except Exception as e:
            print(f"[ERROR USUARIOS CONTROLLER] Error en cleanup: {e}")
    
    def inicializar_vista(self):
        """Inicializa la vista de usuarios."""
        print("[USUARIOS] Vista inicializada")
