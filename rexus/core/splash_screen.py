"""
Splash Screen para la aplicación
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QSplashScreen


class SplashScreen(QSplashScreen):
    """Pantalla de carga de la aplicación"""

    def __init__(self):
        # Crear un pixmap básico si no hay imagen
        pixmap = QPixmap(400, 300)
        pixmap.fill(Qt.GlobalColor.white)

        super().__init__(pixmap)
        self.setWindowFlags(
            Qt.WindowType.SplashScreen | Qt.WindowType.WindowStaysOnTopHint
        )

        # Configurar mensaje
        self.showMessage(
            "Cargando Stock.app...",
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom,
            Qt.GlobalColor.black,
        )

    def update_message(self, message: str):
        """Actualiza el mensaje mostrado"""
        self.showMessage(
            message,
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom,
            Qt.GlobalColor.black,
        )


def show_splash():
    """Muestra la pantalla de carga"""
    splash = SplashScreen()
    splash.show()
    return splash
