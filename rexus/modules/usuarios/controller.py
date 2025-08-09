"""
Controlador de Usuarios - Rexus.app v2.0.0

Maneja la lógica de negocio entre la vista y el modelo de usuarios.
"""

from typing import Any, Dict, List, Optional
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox

from .model import UsuariosModel
from rexus.utils.error_handler import RexusErrorHandler as ErrorHandler, error_boundary as safe_method_decorator
from rexus.utils.message_system import show_success, show_error
from rexus.utils.security import SecurityUtils
from rexus.core.auth_manager import AuthManager
from rexus.core.auth_decorators import auth_required, admin_required, permission_required
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric

class UsuariosController(QObject):
    """Controlador para el módulo de usuarios."""
    
    # Señales para comunicación con otros módulos
    usuario_creado = pyqtSignal(dict)
    usuario_actualizado = pyqtSignal(dict)
    usuario_eliminado = pyqtSignal(str)
    sesion_iniciada = pyqtSignal(dict)
    sesion_terminada = pyqtSignal(str)
    
    def __init__(self, model, view, db_connection=None, usuario_actual=None):
        super().__init__()
        self.model = model
        self.view = view
        self.db_connection = db_connection or getattr(model, 'db_connection', None)
        self.usuario_actual = usuario_actual or {"id": 1, "nombre": "SISTEMA"}
        
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
    
    def sanitizar_datos_usuario(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitiza los datos del usuario antes de la validación."""
        datos_sanitizados = {}
        
        # Campos de texto que necesitan sanitización SQL y XSS
        campos_texto = ['username', 'nombre_completo', 'email', 'telefono', 'direccion', 'notas']
        
        for campo in campos_texto:
            if campo in datos and datos[campo]:
                valor = str(datos[campo])
                
                # Verificar si el input es seguro
                if not SecurityUtils.is_safe_input(valor):
                    print(f"⚠️ [SECURITY] Input malicioso detectado en campo '{campo}': {valor}")
                    # Sanitizar tanto SQL como XSS
                    valor = SecurityUtils.sanitize_sql_input(valor)
                    valor = SecurityUtils.sanitize_html_input(valor)
                    print(f"✅ [SECURITY] Valor sanitizado para '{campo}': {valor}")
                
                datos_sanitizados[campo] = valor
            else:
                datos_sanitizados[campo] = datos.get(campo)
        
        # Campos que no necesitan sanitización (pero sí validación)
        campos_seguros = ['id', 'password', 'rol', 'estado', 'permisos', 'fecha_creacion', 'ultimo_acceso']
        
        for campo in campos_seguros:
            if campo in datos:
                datos_sanitizados[campo] = datos[campo]
        
        # Validación especial para email
        if 'email' in datos_sanitizados and datos_sanitizados['email']:
            email = datos_sanitizados['email']
            # Remover espacios y convertir a minúsculas
            email = email.strip().lower()
            # Validación básica de formato
            if '@' in email and '.' in email:
                datos_sanitizados['email'] = email
            else:
                print(f"⚠️ [SECURITY] Email con formato inválido: {email}")
        
        # Log de sanitización exitosa
        print(f"✅ [SECURITY] Datos de usuario sanitizados correctamente")
        
        return datos_sanitizados
    
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
    
    def buscar_usuarios(self, termino_busqueda: str) -> Optional[List[Dict]]:
        """
        Busca usuarios por nombre, username o email.
        
        Args:
            termino_busqueda: Término a buscar
            
        Returns:
            Lista de usuarios encontrados o None en caso de error
        """
        try:
            # Sanitizar término de búsqueda
            termino_sanitizado = SecurityUtils.sanitize_sql_input(str(termino_busqueda))
            termino_sanitizado = SecurityUtils.sanitize_html_input(termino_sanitizado)
            
            if not SecurityUtils.is_safe_input(termino_sanitizado):
                print(f"⚠️ [SECURITY] Término de búsqueda malicioso: {termino_busqueda}")
                return None
            
            # Buscar usuarios usando el modelo
            usuarios = self.model.buscar_usuarios(termino_sanitizado)
            
            print(f"[USUARIOS CONTROLLER] Búsqueda '{termino_sanitizado}': {len(usuarios)} resultados")
            
            return usuarios
            
        except Exception as e:
            print(f"[ERROR USUARIOS CONTROLLER] Error buscando usuarios: {e}")
            self.mostrar_error(f"Error buscando usuarios: {str(e)}")
            return None
    
    @auth_required
    @admin_required
    def crear_usuario(self, datos_usuario:Dict[str, Any]):
        """Crea un nuevo usuario."""
        try:
            # Sanitizar datos antes de validar
            datos_sanitizados = self.sanitizar_datos_usuario(datos_usuario)
            
            # Validar datos sanitizados
            if not self.validar_datos_usuario(datos_sanitizados):
                return
                
            # Crear usuario con datos sanitizados
            exito, mensaje = self.model.crear_usuario(datos_sanitizados)
            
            if exito:
                self.mostrar_exito(mensaje)
                self.cargar_usuarios()
                
                # Emitir señal
                usuario_creado = self.model.obtener_usuario_por_nombre(datos_sanitizados["username"])
                if usuario_creado:
                    self.usuario_creado.emit(usuario_creado)
            else:
                self.mostrar_error(mensaje)
                
        except Exception as e:
            print(f"[ERROR USUARIOS CONTROLLER] Error creando usuario: {e}")
            self.mostrar_error(f"Error creando usuario: {str(e)}")
    
    @auth_required
    @auth_required
    def actualizar_usuario(self, datos_usuario:Dict[str, Any]):
        """Actualiza un usuario existente."""
        try:
            if not datos_usuario.get("id"):
                self.mostrar_error("ID de usuario requerido para actualización")
                return
            
            # Sanitizar datos antes de validar
            datos_sanitizados = self.sanitizar_datos_usuario(datos_usuario)
                
            # Validar datos sanitizados
            if not self.validar_datos_usuario(datos_sanitizados, es_actualizacion=True):
                return
                
            # Actualizar usuario con datos sanitizados
            exito, mensaje = self.model.actualizar_usuario(datos_sanitizados["id"], datos_sanitizados)
            
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
    
    @admin_required
    @admin_required
    def eliminar_usuario(self, usuario_id:str):
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
    
    def cambiar_password(self, usuario_id:int, password_actual: str, password_nueva: str):
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
    
    @admin_required
    def validar_datos_usuario(self, datos: Dict[str, Any], es_actualizacion: bool = False) -> bool:
        """Valida los datos del usuario."""
        errores = []
        
        # Validaciones básicas
        if not datos.get("username"):
            errores.append("Nombre de usuario es obligatorio")
        elif len(datos["username"]) < 3:
            errores.append("Nombre de usuario debe tener al menos 3 caracteres")
        else:
            # Validar unicidad del nombre de usuario
            usuario_id_excluir = datos.get("id") if es_actualizacion else None
            if self.model.verificar_unicidad_username(datos["username"], usuario_id_excluir):
                errores.append("El nombre de usuario ya está en uso")
            
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
            else:
                # Validar unicidad del email
                usuario_id_excluir = datos.get("id") if es_actualizacion else None
                if self.model.verificar_unicidad_email(email, usuario_id_excluir):
                    errores.append("El email ya está registrado en el sistema")
        
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
        """Autentica un usuario y devuelve sus datos con control de intentos fallidos."""
        try:
            # Sanitizar inputs de autenticación
            username_sanitizado = SecurityUtils.sanitize_sql_input(str(username))
            username_sanitizado = SecurityUtils.sanitize_html_input(username_sanitizado)
            
            # Verificar que el input sanitizado sea seguro
            if not SecurityUtils.is_safe_input(username_sanitizado):
                print(f"⚠️ [SECURITY] Intento de login con username malicioso: {username}")
                return None
            
            # 🔒 VERIFICAR SI EL USUARIO ESTÁ BLOQUEADO
            bloqueado, tiempo_restante = self.model.verificar_usuario_bloqueado(username_sanitizado)
            if bloqueado:
                mensaje_bloqueo = f"Usuario bloqueado por exceso de intentos fallidos. "
                if tiempo_restante > 0:
                    mensaje_bloqueo += f"Intente nuevamente en {tiempo_restante} minutos."
                else:
                    mensaje_bloqueo += "Contacte al administrador."
                
                self.mostrar_error(mensaje_bloqueo)
                
                # Registrar intento de acceso en usuario bloqueado
                self.registrar_auditoria(
                    f"Intento de acceso a usuario bloqueado",
                    "usuarios",
                    {"username": username_sanitizado, "tiempo_restante": tiempo_restante}
                )
                
                return None
            
            # Obtener datos del usuario
            usuario = self.model.obtener_usuario_por_nombre(username_sanitizado)
            
            if not usuario:
                # Usuario no existe - también incrementar contador para prevenir ataques de enumeración
                print(f"⚠️ [SECURITY] Intento de login con usuario inexistente: {username}")
                
                # Registrar intento malicioso
                self.registrar_auditoria(
                    f"Intento de acceso con usuario inexistente",
                    "usuarios", 
                    {"username": username_sanitizado}
                )
                
                return None
                
            # Verificar contraseña
            if not self.model._verificar_password(password, usuario["password_hash"]):
                # 🔒 CONTRASEÑA INCORRECTA - INCREMENTAR INTENTOS FALLIDOS
                bloqueado, intentos, tiempo_bloqueo = self.model.incrementar_intentos_fallidos(username_sanitizado)
                
                if bloqueado:
                    mensaje_error = f"Contraseña incorrecta. Usuario BLOQUEADO por {tiempo_bloqueo} minutos después de {intentos} intentos fallidos."
                    self.mostrar_error(mensaje_error)
                    
                    # Registrar bloqueo de usuario
                    self.registrar_auditoria(
                        f"Usuario bloqueado por {intentos} intentos fallidos",
                        "usuarios",
                        {"usuario_id": usuario["id"], "username": username_sanitizado, "intentos": intentos, "tiempo_bloqueo": tiempo_bloqueo}
                    )
                else:
                    intentos_restantes = 3 - intentos  # Máximo configurado en el modelo
                    mensaje_error = f"Contraseña incorrecta. Intento {intentos} de 3. Quedan {intentos_restantes} intentos antes del bloqueo."
                    self.mostrar_error(mensaje_error)
                    
                    # Registrar intento fallido
                    self.registrar_auditoria(
                        f"Intento de login fallido #{intentos}",
                        "usuarios",
                        {"usuario_id": usuario["id"], "username": username_sanitizado, "intentos": intentos}
                    )
                
                return None
                
            # 🎉 LOGIN EXITOSO
            
            # Limpiar intentos fallidos
            self.model.limpiar_intentos_fallidos(username_sanitizado)
            
            # Actualizar último acceso
            self.model.actualizar_usuario(usuario["id"], {"ultimo_acceso": "NOW()"})
            
            # Registrar auditoría de éxito
            self.registrar_auditoria(
                f"Inicio de sesión exitoso",
                "usuarios",
                {"usuario_id": usuario["id"], "username": username_sanitizado}
            )
            
            print(f"✅ [SECURITY] Login exitoso para usuario '{username_sanitizado}'")
            
            return usuario
            
        except Exception as e:
            print(f"[ERROR USUARIOS CONTROLLER] Error autenticando usuario: {e}")
            
            # En caso de error, registrar para auditoría
            self.registrar_auditoria(
                f"Error en proceso de autenticación",
                "usuarios",
                {"username": username, "error": str(e)}
            )
            
            return None
    
    def desbloquear_usuario(self, username: str) -> bool:
        """
        Desbloquea un usuario manualmente (solo para administradores).
        
        Args:
            username: Nombre de usuario a desbloquear
            
        Returns:
            bool: True si se desbloqueó exitosamente
        """
        try:
            # Verificar que el usuario actual tenga permisos de administrador
            # (esto se podría integrar con el sistema de permisos)
            
            # Sanitizar input
            username_sanitizado = SecurityUtils.sanitize_sql_input(str(username))
            username_sanitizado = SecurityUtils.sanitize_html_input(username_sanitizado)
            
            if not SecurityUtils.is_safe_input(username_sanitizado):
                print(f"⚠️ [SECURITY] Intento de desbloqueo con username malicioso: {username}")
                return False
            
            # Desbloquear usuario
            self.model.limpiar_intentos_fallidos(username_sanitizado)
            
            # Registrar acción de administrador
            self.registrar_auditoria(
                f"Usuario desbloqueado manualmente por administrador",
                "usuarios",
                {"username_desbloqueado": username_sanitizado, "admin_user": self.usuario_actual}
            )
            
            self.mostrar_exito(f"Usuario '{username}' desbloqueado exitosamente")
            print(f"✅ [ADMIN] Usuario '{username}' desbloqueado manualmente")
            
            return True
            
        except Exception as e:
            print(f"[ERROR USUARIOS CONTROLLER] Error desbloqueando usuario: {e}")
            self.mostrar_error(f"Error desbloqueando usuario: {str(e)}")
            return False
    
    def obtener_estado_bloqueo_usuario(self, username: str) -> Dict[str, Any]:
        """
        Obtiene el estado de bloqueo de un usuario.
        
        Args:
            username: Nombre de usuario
            
        Returns:
            dict: Estado del bloqueo del usuario
        """
        try:
            # Sanitizar input
            username_sanitizado = SecurityUtils.sanitize_sql_input(str(username))
            username_sanitizado = SecurityUtils.sanitize_html_input(username_sanitizado)
            
            if not SecurityUtils.is_safe_input(username_sanitizado):
                return {"error": "Username inválido"}
            
            # Verificar estado de bloqueo
            bloqueado, tiempo_restante = self.model.verificar_usuario_bloqueado(username_sanitizado)
            
            # Obtener usuario para contar intentos actuales
            usuario = self.model.obtener_usuario_por_nombre(username_sanitizado)
            intentos_fallidos = 0
            if usuario:
                intentos_fallidos = usuario.get("intentos_fallidos", 0)
            
            estado = {
                "username": username,
                "bloqueado": bloqueado,
                "tiempo_restante_minutos": tiempo_restante,
                "intentos_fallidos": intentos_fallidos,
                "max_intentos": 3  # Configurado en el modelo
            }
            
            return estado
            
        except Exception as e:
            print(f"[ERROR USUARIOS CONTROLLER] Error obteniendo estado de bloqueo: {e}")
            return {"error": str(e)}
    
    @admin_required
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
        """Muestra un mensaje de éxito con el sistema mejorado."""
        if self.view:
            show_success(self.view, "Éxito", mensaje)
    
    
    def cargar_pagina(self, pagina, registros_por_pagina=50):
        """Carga una página específica de datos"""
        try:
            if self.model:
                offset = (pagina - 1) * registros_por_pagina
                
                # Obtener datos paginados
                datos, total_registros = self.model.obtener_datos_paginados(
                    offset=offset, 
                    limit=registros_por_pagina
                )
                
                if self.view:
                    # Cargar datos en la tabla
                    if hasattr(self.view, 'cargar_en_tabla'):
                        self.view.cargar_en_tabla(datos)
                    
                    # Actualizar controles de paginación
                    total_paginas = (total_registros + registros_por_pagina - 1) // registros_por_pagina
                    if hasattr(self.view, 'actualizar_controles_paginacion'):
                        self.view.actualizar_controles_paginacion(
                            pagina, total_paginas, total_registros, len(datos)
                        )
        
        except Exception as e:
            print(f"[ERROR] Error cargando página: {e}")
            if hasattr(self, 'mostrar_error'):
                self.mostrar_error("Error", f"Error cargando página: {str(e)}")
    
    def cambiar_registros_por_pagina(self, registros):
        """Cambia la cantidad de registros por página y recarga"""
        self.registros_por_pagina = registros
        self.cargar_pagina(1, registros)
    
    def obtener_total_registros(self):
        """Obtiene el total de registros disponibles"""
        try:
            if self.model:
                return self.model.obtener_total_registros()
            return 0
        except Exception as e:
            print(f"[ERROR] Error obteniendo total de registros: {e}")
            return 0

    def mostrar_error(self, mensaje: str):
        """Muestra un mensaje de error con el sistema mejorado."""
        if self.view:
            show_error(self.view, "Error", mensaje)
    
    def mostrar_advertencia(self, mensaje: str):
        """Muestra un mensaje de advertencia con el sistema mejorado."""
        if self.view:
            from rexus.utils.message_system import show_warning
            show_warning(self.view, "Advertencia", mensaje)
    
    def mostrar_info(self, mensaje: str):
        """Muestra un mensaje informativo con el sistema mejorado."""
        if self.view:
            from rexus.utils.message_system import show_info
            show_info(self.view, "Información", mensaje)
    
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
