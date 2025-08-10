"""
MIT License

Copyright (c) 2024 Rexus.app

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

"""
Sistema de Diálogos para Rexus.app

Proporciona funciones de utilidad para mostrar diálogos
de información, advertencias y errores de forma consistente.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMessageBox, QWidget


def show_info(title: str, message: str, parent: QWidget = None):
    """Muestra un diálogo de información."""
    try:
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
    except Exception as e:
        print(f"Error mostrando diálogo de información: {e}")
        print(f"Título: {title}")
        print(f"Mensaje: {message}")


def show_warning(title: str, message: str, parent: QWidget = None):
    """Muestra un diálogo de advertencia."""
    try:
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
    except Exception as e:
        print(f"Error mostrando diálogo de advertencia: {e}")
        print(f"Título: {title}")
        print(f"Mensaje: {message}")


def show_error(title: str, message: str, parent: QWidget = None):
    """Muestra un diálogo de error."""
    try:
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
    except Exception as e:
        print(f"Error mostrando diálogo de error: {e}")
        print(f"Título: {title}")
        print(f"Mensaje: {message}")


def show_question(title: str, message: str, parent: QWidget = None) -> bool:
    """Muestra un diálogo de pregunta y retorna True si el usuario acepta."""
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
        print(f"Error mostrando diálogo de pregunta: {e}")
        print(f"Título: {title}")
        print(f"Mensaje: {message}")
        return False


def show_confirm(title: str, message: str, parent: QWidget = None) -> bool:
    """Muestra un diálogo de confirmación y retorna True si el usuario acepta."""
    return show_question(title, message, parent)


# Funciones de conveniencia con títulos predeterminados
def info(message: str, parent: QWidget = None):
    """Muestra información con título predeterminado."""
    show_info("Información", message, parent)


def warning(message: str, parent: QWidget = None):
    """Muestra advertencia con título predeterminado."""
    show_warning("Advertencia", message, parent)


def error(message: str, parent: QWidget = None):
    """Muestra error con título predeterminado."""
    show_error("Error", message, parent)


def question(message: str, parent: QWidget = None) -> bool:
    """Muestra pregunta con título predeterminado."""
    return show_question("Pregunta", message, parent)


def confirm(message: str, parent: QWidget = None) -> bool:
    """Muestra confirmación con título predeterminado."""
    return show_confirm("Confirmar", message, parent)
