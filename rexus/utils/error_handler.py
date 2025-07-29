"""
Sistema unificado de manejo de errores para Rexus.app

Este módulo proporciona utilidades para manejar errores de manera consistente
a través de toda la aplicación, con feedback visual apropiado para el usuario.
"""

import logging
import traceback
from datetime import datetime
from typing import Optional, Callable

from PyQt6.QtWidgets import QMessageBox, QWidget


class ErrorHandler:
    """Manejador centralizado de errores para la aplicación."""
    
    @staticmethod
    def configurar_logging():
        """Configura el sistema de logging para errores."""
        logging.basicConfig(
            level=logging.ERROR,
            format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/errores.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    
    @staticmethod
    def mostrar_error_critico(parent: Optional[QWidget], mensaje: str, detalle: Optional[str] = None):
        """
        Muestra un error crítico con QMessageBox.
        
        Args:
            parent: Widget padre para el diálogo
            mensaje: Mensaje principal del error
            detalle: Detalle técnico opcional del error
        """
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("Error Crítico - Rexus.app")
        msg_box.setText(mensaje)
        
        if detalle:
            msg_box.setDetailedText(detalle)
        
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
    
    @staticmethod
    def mostrar_error_operacion(parent: Optional[QWidget], operacion: str, error: Exception):
        """
        Muestra un error de operación con contexto.
        
        Args:
            parent: Widget padre para el diálogo
            operacion: Descripción de la operación que falló
            error: Excepción capturada
        """
        mensaje = f"Error al {operacion}"
        detalle = f"Error técnico: {str(error)}"
        
        ErrorHandler.mostrar_error_critico(parent, mensaje, detalle)
        ErrorHandler.log_error(f"Error en {operacion}", error)
    
    @staticmethod
    def mostrar_advertencia(parent: Optional[QWidget], titulo: str, mensaje: str):
        """
        Muestra una advertencia al usuario.
        
        Args:
            parent: Widget padre para el diálogo
            titulo: Título de la advertencia
            mensaje: Mensaje de la advertencia
        """
        QMessageBox.warning(parent, f"Advertencia - {titulo}", mensaje)
    
    @staticmethod
    def mostrar_informacion(parent: Optional[QWidget], titulo: str, mensaje: str):
        """
        Muestra información al usuario.
        
        Args:
            parent: Widget padre para el diálogo
            titulo: Título del mensaje
            mensaje: Mensaje informativo
        """
        QMessageBox.information(parent, f"Información - {titulo}", mensaje)
    
    @staticmethod
    def confirmar_accion(parent: Optional[QWidget], titulo: str, mensaje: str) -> bool:
        """
        Solicita confirmación al usuario.
        
        Args:
            parent: Widget padre para el diálogo
            titulo: Título del diálogo
            mensaje: Mensaje de confirmación
            
        Returns:
            True si el usuario confirma, False en caso contrario
        """
        respuesta = QMessageBox.question(
            parent,
            f"Confirmación - {titulo}",
            mensaje,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        return respuesta == QMessageBox.StandardButton.Yes
    
    @staticmethod
    def log_error(contexto: str, error: Exception):
        """
        Registra un error en el log.
        
        Args:
            contexto: Contexto donde ocurrió el error
            error: Excepción capturada
        """
        error_msg = f"{contexto}: {str(error)}"
        error_detail = traceback.format_exc()
        
        logging.error(f"{error_msg}\n{error_detail}")
        print(f"[ERROR] {datetime.now().isoformat()} - {error_msg}")
    
    @staticmethod
    def manejar_error_base_datos(parent: Optional[QWidget], operacion: str, error: Exception):
        """
        Maneja específicamente errores de base de datos.
        
        Args:
            parent: Widget padre para el diálogo
            operacion: Operación que falló
            error: Excepción de base de datos
        """
        mensaje = f"Error de base de datos al {operacion}"
        
        # Determinar el tipo de error específico
        error_str = str(error).lower()
        if "connection" in error_str or "login" in error_str:
            detalle = "No se pudo conectar a la base de datos. Verifique la conexión y credenciales."
        elif "timeout" in error_str:
            detalle = "La operación tardó demasiado tiempo. Intente nuevamente."
        elif "duplicate" in error_str or "unique" in error_str:
            detalle = "El registro ya existe. Verifique los datos e intente con valores únicos."
        elif "foreign key" in error_str:
            detalle = "Error de integridad: el registro está relacionado con otros datos."
        else:
            detalle = f"Error técnico: {str(error)}"
        
        ErrorHandler.mostrar_error_critico(parent, mensaje, detalle)
        ErrorHandler.log_error(f"Error BD - {operacion}", error)


def safe_execute(func: Callable, parent: Optional[QWidget] = None, 
                operacion: str = "ejecutar operación", 
                default_return=None):
    """
    Decorador/función para ejecutar operaciones de manera segura.
    
    Args:
        func: Función a ejecutar
        parent: Widget padre para mostrar errores
        operacion: Descripción de la operación
        default_return: Valor por defecto si hay error
        
    Returns:
        Resultado de la función o default_return si hay error
    """
    try:
        return func()
    except Exception as e:
        ErrorHandler.mostrar_error_operacion(parent, operacion, e)
        return default_return


def safe_method_decorator(operacion: str = "ejecutar método"):
    """
    Decorador para métodos que maneja errores automáticamente.
    
    Args:
        operacion: Descripción de la operación
    """
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                parent = getattr(self, 'view', None) or getattr(self, 'parent', None)
                ErrorHandler.mostrar_error_operacion(parent, operacion, e)
                return None
        return wrapper
    return decorator