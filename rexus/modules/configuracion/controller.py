"""
Controlador de Configuración - Rexus.app v2.0.0

Maneja la lógica de negocio para la configuración del sistema.
"""

from typing import Any, Dict, List, Optional
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox, QFileDialog
from rexus.core.auth_decorators import auth_required, admin_required, permission_required
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric

from .model import ConfiguracionModel

class ConfiguracionController(QObject):
    """Controlador para la gestión de configuraciones del sistema."""
    
    # Señales para comunicación
    configuracion_actualizada = pyqtSignal(str, str)  # clave, valor
    configuracion_restaurada = pyqtSignal(str)  # clave
    configuracion_exportada = pyqtSignal(str)  # archivo
    configuracion_importada = pyqtSignal(str)  # archivo
    
    def __init__(self, model=None, view=None, db_connection=None, usuario_actual=None):
        super().__init__()
        
        # Si model es pasado como primer parámetro (patrón MVC estándar)
        if model is not None:
            self.model = model
            self.view = view
        else:
            # Compatibilidad hacia atrás: view como primer parámetro
            self.view = model  # En este caso, 'model' es realmente 'view'
            self.model = ConfiguracionModel(db_connection)
            
        self.db_connection = db_connection
        self.usuario_actual = usuario_actual or {"id": 1, "nombre": "SISTEMA"}
        
        # Conectar señales si hay vista
        if self.view:
            self.conectar_señales()
            self.cargar_configuraciones()
    
    def conectar_señales(self):
        """Conecta las señales entre vista y controlador."""
        if not self.view:
            return
            
        # Conectar señales de la vista
        if hasattr(self.view, 'solicitud_actualizar_configuracion'):
            self.view.solicitud_actualizar_configuracion.connect(self.actualizar_configuracion)
        if hasattr(self.view, 'solicitud_restaurar_configuracion'):
            self.view.solicitud_restaurar_configuracion.connect(self.restaurar_configuracion)
        if hasattr(self.view, 'solicitud_exportar_configuracion'):
            self.view.solicitud_exportar_configuracion.connect(self.exportar_configuracion)
        if hasattr(self.view, 'solicitud_importar_configuracion'):
            self.view.solicitud_importar_configuracion.connect(self.importar_configuracion)
        if hasattr(self.view, 'solicitud_probar_conexion_bd'):
            self.view.solicitud_probar_conexion_bd.connect(self.probar_conexion_bd)
        
        # Establecer controlador en la vista (si tiene este método)
        if hasattr(self.view, 'set_controller'):
            self.view.set_controller(self)
    
    def cargar_configuraciones(self):
        """Carga todas las configuraciones en la vista."""
        try:
            configuraciones = self.model.obtener_todas_configuraciones()
            
            if self.view and hasattr(self.view, 'cargar_configuraciones'):
                self.view.cargar_configuraciones(configuraciones)
            
            print(f"[CONFIGURACION CONTROLLER] Cargadas {len(configuraciones)} configuraciones")
            
        except Exception as e:
            print(f"[ERROR CONFIGURACION CONTROLLER] Error cargando configuraciones: {e}")
            self.mostrar_error(f"Error cargando configuraciones: {str(e)}")
    
    def cargar_configuracion_por_categoria(self, categoria: str):
        """Carga configuraciones de una categoría específica."""
        try:
            configuraciones = self.model.obtener_configuracion_por_categoria(categoria)
            
            if self.view and hasattr(self.view, 'cargar_configuraciones_categoria'):
                self.view.cargar_configuraciones_categoria(categoria, configuraciones)
            
            print(f"[CONFIGURACION CONTROLLER] Cargadas configuraciones de categoría {categoria}")
            
        except Exception as e:
            print(f"[ERROR CONFIGURACION CONTROLLER] Error cargando configuraciones por categoría: {e}")
            self.mostrar_error(f"Error cargando configuraciones: {str(e)}")
    
    @admin_required
    def actualizar_configuracion(self, clave:str, valor: Any):
        """Actualiza una configuración."""
        try:
            usuario = self.usuario_actual.get("nombre", "SISTEMA")
            exito, mensaje = self.model.establecer_valor(clave, valor, usuario)
            
            if exito:
                self.mostrar_exito(mensaje)
                self.configuracion_actualizada.emit(clave, str(valor))
                
                # Recargar configuraciones
                self.cargar_configuraciones()
                
                # Aplicar cambios específicos
                self._aplicar_cambio_configuracion(clave, valor)
                
            else:
                self.mostrar_error(mensaje)
                
        except Exception as e:
            print(f"[ERROR CONFIGURACION CONTROLLER] Error actualizando configuración: {e}")
            self.mostrar_error(f"Error actualizando configuración: {str(e)}")
    
    def restaurar_configuracion(self, clave: str):
        """Restaura una configuración a su valor por defecto."""
        try:
            # Confirmar restauración
            if self.view:
                respuesta = QMessageBox.question(
                    self.view,
                    "Confirmar restauración",
                    f"¿Está seguro de restaurar la configuración '{clave}' a su valor por defecto?\n\n"
                    "Esta acción no se puede deshacer.",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                
                if respuesta == QMessageBox.StandardButton.Yes:
                    usuario = self.usuario_actual.get("nombre", "SISTEMA")
                    exito, mensaje = self.model.restaurar_configuracion_defecto(clave, usuario)
                    
                    if exito:
                        self.mostrar_exito(mensaje)
                        self.configuracion_restaurada.emit(clave)
                        self.cargar_configuraciones()
                    else:
                        self.mostrar_error(mensaje)
                
        except Exception as e:
            print(f"[ERROR CONFIGURACION CONTROLLER] Error restaurando configuración: {e}")
            self.mostrar_error(f"Error restaurando configuración: {str(e)}")
    
    def exportar_configuracion(self):
        """Exporta la configuración actual a un archivo."""
        try:
            if self.view:
                archivo, _ = QFileDialog.getSaveFileName(
                    self.view,
                    "Exportar Configuración",
                    "rexus_config.json",
                    "JSON Files (*.json);;All Files (*)"
                )
                
                if archivo:
                    exito, mensaje = self.model.exportar_configuracion(archivo)
                    
                    if exito:
                        self.mostrar_exito(mensaje)
                        self.configuracion_exportada.emit(archivo)
                    else:
                        self.mostrar_error(mensaje)
                
        except Exception as e:
            print(f"[ERROR CONFIGURACION CONTROLLER] Error exportando configuración: {e}")
            self.mostrar_error(f"Error exportando configuración: {str(e)}")
    
    def importar_configuracion(self):
        """Importa configuración desde un archivo."""
        try:
            if self.view:
                archivo, _ = QFileDialog.getOpenFileName(
                    self.view,
                    "Importar Configuración",
                    "",
                    "JSON Files (*.json);;All Files (*)"
                )
                
                if archivo:
                    # Confirmar importación
                    respuesta = QMessageBox.question(
                        self.view,
                        "Confirmar importación",
                        f"¿Está seguro de importar configuración desde '{archivo}'?\n\n"
                        "Esto sobrescribirá las configuraciones existentes.",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No
                    )
                    
                    if respuesta == QMessageBox.StandardButton.Yes:
                        usuario = self.usuario_actual.get("nombre", "SISTEMA")
                        exito, mensaje = self.model.importar_configuracion(archivo, usuario)
                        
                        if exito:
                            self.mostrar_exito(mensaje)
                            self.configuracion_importada.emit(archivo)
                            self.cargar_configuraciones()
                        else:
                            self.mostrar_error(mensaje)
                
        except Exception as e:
            print(f"[ERROR CONFIGURACION CONTROLLER] Error importando configuración: {e}")
            self.mostrar_error(f"Error importando configuración: {str(e)}")
    
    def probar_conexion_bd(self):
        """Prueba la conexión a la base de datos con la configuración actual."""
        try:
            # Obtener configuración de BD
            db_config = {
                'server': self.model.obtener_valor('db_server', 'localhost'),
                'port': self.model.obtener_valor('db_port', '1433'),
                'database': self.model.obtener_valor('db_name', 'rexus_db'),
                'username': self.model.obtener_valor('db_user', 'sa'),
                'timeout': self.model.obtener_valor('db_timeout', '30')
            }
            
            # Aquí implementarías la lógica de prueba de conexión
            # Por ahora, mostrar la configuración
            mensaje = f"""Configuración de Base de Datos:
            
Servidor: {db_config['server']}
Puerto: {db_config['port']}
Base de datos: {db_config['database']}
Usuario: {db_config['username']}
Timeout: {db_config['timeout']}s

Estado: Configuración cargada correctamente"""
            
            self.mostrar_info(mensaje)
            
        except Exception as e:
            print(f"[ERROR CONFIGURACION CONTROLLER] Error probando conexión BD: {e}")
            self.mostrar_error(f"Error probando conexión: {str(e)}")
    
    def obtener_valor_configuracion(self, clave: str, valor_por_defecto: Any = None) -> Any:
        """Obtiene un valor de configuración."""
        try:
            return self.model.obtener_valor(clave, valor_por_defecto)
        except Exception as e:
            print(f"[ERROR CONFIGURACION CONTROLLER] Error obteniendo valor: {e}")
            return valor_por_defecto
    
    def obtener_configuracion_empresa(self) -> Dict[str, Any]:
        """Obtiene la configuración de la empresa."""
        try:
            return self.model.obtener_configuracion_por_categoria('EMPRESA')
        except Exception as e:
            print(f"[ERROR CONFIGURACION CONTROLLER] Error obteniendo configuración empresa: {e}")
            return {}
    
    def obtener_configuracion_sistema(self) -> Dict[str, Any]:
        """Obtiene la configuración del sistema."""
        try:
            return self.model.obtener_configuracion_por_categoria('SISTEMA')
        except Exception as e:
            print(f"[ERROR CONFIGURACION CONTROLLER] Error obteniendo configuración sistema: {e}")
            return {}
    
    def obtener_configuracion_tema(self) -> Dict[str, Any]:
        """Obtiene la configuración del tema."""
        try:
            return self.model.obtener_configuracion_por_categoria('TEMA')
        except Exception as e:
            print(f"[ERROR CONFIGURACION CONTROLLER] Error obteniendo configuración tema: {e}")
            return {}
    
    def _aplicar_cambio_configuracion(self, clave: str, valor: Any):
        """Aplica cambios específicos según la configuración modificada."""
        try:
            # Aplicar cambios de tema
            if clave.startswith('tema_'):
                self._aplicar_cambio_tema(clave, valor)
            
            # Aplicar cambios de sistema
            elif clave.startswith('sistema_'):
                self._aplicar_cambio_sistema(clave, valor)
            
            # Aplicar cambios de usuarios
            elif clave.startswith('usuarios_'):
                self._aplicar_cambio_usuarios(clave, valor)
                
        except Exception as e:
            print(f"[ERROR CONFIGURACION CONTROLLER] Error aplicando cambio: {e}")
    
    def _aplicar_cambio_tema(self, clave: str, valor: Any):
        """Aplica cambios de tema."""
        try:
            if self.view and hasattr(self.view, 'aplicar_cambio_tema'):
                self.view.aplicar_cambio_tema(clave, valor)
        except Exception as e:
            print(f"[ERROR CONFIGURACION CONTROLLER] Error aplicando cambio tema: {e}")
    
    def _aplicar_cambio_sistema(self, clave: str, valor: Any):
        """Aplica cambios de sistema."""
        try:
            if clave == 'sistema_idioma':
                # Cambiar idioma de la aplicación
                print(f"[CONFIGURACION] Cambiando idioma a: {valor}")
            elif clave == 'sistema_modo_debug':
                # Cambiar modo debug
                print(f"[CONFIGURACION] Cambiando modo debug a: {valor}")
        except Exception as e:
            print(f"[ERROR CONFIGURACION CONTROLLER] Error aplicando cambio sistema: {e}")
    
    def _aplicar_cambio_usuarios(self, clave: str, valor: Any):
        """Aplica cambios de configuración de usuarios."""
        try:
            if clave == 'usuarios_session_timeout':
                # Actualizar timeout de sesión
                print(f"[CONFIGURACION] Cambiando timeout de sesión a: {valor}")
            elif clave == 'usuarios_password_min_length':
                # Actualizar política de contraseñas
                print(f"[CONFIGURACION] Cambiando longitud mínima de contraseña a: {valor}")
        except Exception as e:
            print(f"[ERROR CONFIGURACION CONTROLLER] Error aplicando cambio usuarios: {e}")
    
    def obtener_categorias_configuracion(self) -> List[str]:
        """Obtiene las categorías de configuración disponibles."""
        return list(self.model.TIPOS_CONFIG.keys())
    
    def set_usuario_actual(self, usuario: Dict[str, Any]):
        """Establece el usuario actual."""
        self.usuario_actual = usuario
        print(f"[CONFIGURACION CONTROLLER] Usuario actual: {usuario.get('nombre', 'Desconocido')}")
    
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
            print("[CONFIGURACION CONTROLLER] Limpiando recursos...")
            # Desconectar señales si es necesario
            # Cerrar conexiones, etc.
        except Exception as e:
            print(f"[ERROR CONFIGURACION CONTROLLER] Error en cleanup: {e}")
