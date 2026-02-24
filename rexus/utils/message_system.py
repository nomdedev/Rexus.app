"""
Sistema de mensajes unificado para Rexus.app
Centraliza las funciones de diálogo para mantener consistencia en toda la aplicación.
"""

from PyQt6.QtWidgets import QMessageBox, QWidget
from typing import Optional


def show_success(parent: Optional[QWidget], title: str, message: str):
    """Muestra un diálogo de éxito."""
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Information)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    if parent:
        msg_box.exec(parent)
    else:
        msg_box.exec()


def show_error(parent: Optional[QWidget], title: str, message: str):
    """Muestra un diálogo de error."""
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Critical)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    if parent:
        msg_box.exec(parent)
    else:
        msg_box.exec()


def show_warning(parent: Optional[QWidget], title: str, message: str):
    """Muestra un diálogo de advertencia."""
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Warning)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    if parent:
        msg_box.exec(parent)
    else:
        msg_box.exec()


def show_info(parent: Optional[QWidget], title: str, message: str):
    """Muestra un diálogo informativo."""
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Information)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    if parent:
        msg_box.exec(parent)
    else:
        msg_box.exec()


def ask_question(parent: Optional[QWidget], title: str, message: str) -> bool:
    """
    Muestra un diálogo de pregunta y retorna True si el usuario responde "Sí".
    
    Args:
        parent: Widget padre del diálogo
        title: Título del diálogo
        message: Mensaje a mostrar
        
    Returns:
        True si el usuario hace clic en "Sí", False si hace clic en "No"
    """
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Question)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setStandardButtons(
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    msg_box.setDefaultButton(QMessageBox.StandardButton.No)
    
    if parent:
        response = msg_box.exec(parent)
    else:
        response = msg_box.exec()
    
    return response == QMessageBox.StandardButton.Yes