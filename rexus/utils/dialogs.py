"""
Sistema de Diálogos para Rexus.app

Proporciona funciones de utilidad para mostrar diálogos
de información, advertencias y errores de forma consistente.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

try:
    from PyQt6.QtWidgets import (
        QMessageBox, QInputDialog, QFileDialog, QColorDialog,
        QWidget, QProgressDialog
    )
    from PyQt6.QtGui import QColor
    from PyQt6.QtCore import Qt
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False


def show_info(title: str, message: str, parent: Optional[QWidget] = None) -> None:
    """
    Muestra un diálogo de información.

    Args:
        title: Título del diálogo
        message: Mensaje a mostrar
        parent: Widget padre (opcional)
    """
    if not PYQT_AVAILABLE:
        logger.info(f"{title}: {message}")
        return

    try:
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
    except Exception as e:
        logger.error(f"Error mostrando diálogo de información: {e}")


def show_warning(title: str, message: str, parent: Optional[QWidget] = None) -> None:
    """
    Muestra un diálogo de advertencia.

    Args:
        title: Título del diálogo
        message: Mensaje a mostrar
        parent: Widget padre (opcional)
    """
    if not PYQT_AVAILABLE:
        logger.warning(f"{title}: {message}")
        return

    try:
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
    except Exception as e:
        logger.error(f"Error mostrando diálogo de advertencia: {e}")


def show_error(title: str, message: str, parent: Optional[QWidget] = None) -> None:
    """
    Muestra un diálogo de error.

    Args:
        title: Título del diálogo
        message: Mensaje a mostrar
        parent: Widget padre (opcional)
    """
    if not PYQT_AVAILABLE:
        logger.error(f"{title}: {message}")
        return

    try:
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
    except Exception as e:
        logger.error(f"Error mostrando diálogo de error: {e}")


def show_confirm(title: str, message: str, parent: Optional[QWidget] = None) -> bool:
    """
    Muestra un diálogo de confirmación.

    Args:
        title: Título del diálogo
        message: Mensaje a mostrar
        parent: Widget padre (opcional)

    Returns:
        True si el usuario confirma, False en caso contrario
    """
    if not PYQT_AVAILABLE:
        response = input(f"{title}: {message} (y/N): ").lower().strip()
        return response in ['y', 'yes']

    try:
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)

        result = msg_box.exec()
        return result == QMessageBox.StandardButton.Yes
    except Exception as e:
        logger.error(f"Error mostrando diálogo de confirmación: {e}")
        return False


def get_text_input(
    title: str,
    label: str,
    default_text: str = "",
    parent: Optional[QWidget] = None
) -> Optional[str]:
    """
    Muestra un diálogo para entrada de texto.

    Args:
        title: Título del diálogo
        label: Etiqueta del campo de entrada
        default_text: Texto por defecto
        parent: Widget padre (opcional)

    Returns:
        Texto ingresado por el usuario o None si se cancela
    """
    if not PYQT_AVAILABLE:
        return input(f"{label} (default: {default_text}): ").strip() or default_text

    try:
        text, ok = QInputDialog.getText(parent, title, label, text=default_text)
        return text if ok else None
    except Exception as e:
        logger.error(f"Error obteniendo entrada de texto: {e}")
        return None


def get_file_path(
    title: str = "Seleccionar Archivo",
    filter_str: str = "Todos los archivos (*.*)",
    parent: Optional[QWidget] = None,
    save_mode: bool = False
) -> Optional[str]:
    """
    Muestra un diálogo para selección de archivo.

    Args:
        title: Título del diálogo
        filter_str: Filtro de archivos
        parent: Widget padre (opcional)
        save_mode: True para guardar, False para abrir

    Returns:
        Ruta del archivo seleccionado o None si se cancela
    """
    if not PYQT_AVAILABLE:
        return input(f"{title}: ").strip()

    try:
        if save_mode:
            file_path, _ = QFileDialog.getSaveFileName(
                parent, title, "", filter_str
            )
        else:
            file_path, _ = QFileDialog.getOpenFileName(
                parent, title, "", filter_str
            )

        return file_path if file_path else None
    except Exception as e:
        logger.error(f"Error seleccionando archivo: {e}")
        return None


def get_directory_path(
    title: str = "Seleccionar Directorio",
    parent: Optional[QWidget] = None
) -> Optional[str]:
    """
    Muestra un diálogo para selección de directorio.

    Args:
        title: Título del diálogo
        parent: Widget padre (opcional)

    Returns:
        Ruta del directorio seleccionado o None si se cancela
    """
    if not PYQT_AVAILABLE:
        return input(f"{title}: ").strip()

    try:
        dir_path = QFileDialog.getExistingDirectory(parent, title)
        return dir_path if dir_path else None
    except Exception as e:
        logger.error(f"Error seleccionando directorio: {e}")
        return None


def get_color(
    initial_color: Optional[QColor] = None,
    parent: Optional[QWidget] = None
) -> Optional[QColor]:
    """
    Muestra un diálogo para selección de color.

    Args:
        initial_color: Color inicial (opcional)
        parent: Widget padre (opcional)

    Returns:
        Color seleccionado o None si se cancela
    """
    if not PYQT_AVAILABLE:
        logger.warning("Selección de color no disponible sin PyQt6")
        return None

    try:
        color = QColorDialog.getColor(initial_color or QColor(), parent)
        return color if color.isValid() else None
    except Exception as e:
        logger.error(f"Error seleccionando color: {e}")
        return None


def show_progress_dialog(
    title: str,
    message: str,
    maximum: int = 100,
    parent: Optional[QWidget] = None
) -> Optional[QProgressDialog]:
    """
    Crea un diálogo de progreso.

    Args:
        title: Título del diálogo
        message: Mensaje a mostrar
        maximum: Valor máximo del progreso
        parent: Widget padre (opcional)

    Returns:
        Diálogo de progreso o None si PyQt6 no está disponible
    """
    if not PYQT_AVAILABLE:
        logger.info(f"Progreso: {title} - {message}")
        return None

    try:
        from PyQt6.QtWidgets import QProgressDialog

        progress = QProgressDialog(message, "Cancelar", 0, maximum, parent)
        progress.setWindowTitle(title)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)

        return progress
    except Exception as e:
        logger.error(f"Error creando diálogo de progreso: {e}")
        return None
