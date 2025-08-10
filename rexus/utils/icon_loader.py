"""
Cargador de iconos básico
"""

from pathlib import Path

from PyQt6.QtGui import QIcon, QPixmap


def get_icon(icon_name: str, size: int = 24) -> QIcon:
    """
    Carga un icono por nombre
    """
    icon_path = Path("icons") / f"{icon_name}.svg"
    if icon_path.exists():
        pixmap = QPixmap(str(icon_path))
        if size and size != 24:
            pixmap = pixmap.scaled(size, size)
        return QIcon(pixmap)

    # Devolver icono por defecto si no se encuentra
    return QIcon()
