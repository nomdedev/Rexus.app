"""
Widget de Ayuda de Atajos de Teclado - Rexus.app
Muestra una ventana emergente con todos los atajos disponibles
"""

from typing import Dict

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
)


class ShortcutHelpDialog(QDialog):
    """Diálogo de ayuda para atajos de teclado."""

    def __init__(self, shortcuts: Dict[str, str], parent=None):
        super().__init__(parent)
        self.shortcuts = shortcuts
        self.setup_ui()
        self.load_shortcuts()

    def setup_ui(self):
        """Configura la interfaz de usuario."""
        self.setWindowTitle("Atajos de Teclado - Rexus.app")
        self.setWindowIcon(QIcon("resources/icons/keyboard.png"))
        self.resize(600, 500)
        self.setModal(True)

        # Layout principal
        layout = QVBoxLayout(self)

        # Título
        title_label = QLabel("Atajos de Teclado Disponibles")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Tabla de atajos
        self.shortcuts_table = QTableWidget()
        self.shortcuts_table.setColumnCount(2)
        self.shortcuts_table.setHorizontalHeaderLabels(["Acción", "Atajo"])

        # Configurar header
        header = self.shortcuts_table.horizontalHeader()
        if header:
            header.setStretchLastSection(True)

        self.shortcuts_table.setAlternatingRowColors(True)
        self.shortcuts_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        layout.addWidget(self.shortcuts_table)

        # Información adicional
        info_group = QGroupBox("Información")
        info_layout = QVBoxLayout(info_group)

        info_text = QTextEdit()
        info_text.setMaximumHeight(100)
        info_text.setReadOnly(True)
        info_text.setHtml("""
        <p><b>Tips:</b></p>
        <ul>
        <li>Los atajos son sensibles al contexto</li>
        <li>Tab/Shift+Tab para navegar entre campos</li>
        <li>Enter para confirmar, Escape para cancelar</li>
        <li>F1 para mostrar esta ayuda</li>
        </ul>
        """)
        info_layout.addWidget(info_text)
        layout.addWidget(info_group)

        # Botones
        button_layout = QHBoxLayout()

        close_button = QPushButton("Cerrar")
        close_button.clicked.connect(self.accept)
        close_button.setDefault(True)

        print_button = QPushButton("Imprimir")
        print_button.clicked.connect(self.print_shortcuts)

        button_layout.addStretch()
        button_layout.addWidget(print_button)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

    def load_shortcuts(self):
        """Carga los atajos en la tabla."""
        self.shortcuts_table.setRowCount(len(self.shortcuts))

        for row, (action, shortcut) in enumerate(self.shortcuts.items()):
            # Acción
            action_item = QTableWidgetItem(action)
            action_item.setFlags(
                Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
            )
            self.shortcuts_table.setItem(row, 0, action_item)

            # Atajo
            shortcut_item = QTableWidgetItem(shortcut)
            shortcut_item.setFlags(
                Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
            )
            font = QFont()
            font.setFamily("Courier")
            shortcut_item.setFont(font)
            self.shortcuts_table.setItem(row, 1, shortcut_item)

        # Ajustar columnas
        self.shortcuts_table.resizeColumnsToContents()

    def print_shortcuts(self):
        """Imprime o exporta la lista de atajos."""
        # En un entorno real, esto abriría un diálogo de impresión
        print("Imprimiendo atajos de teclado...")
        for action, shortcut in self.shortcuts.items():
            print(f"{action}: {shortcut}")


class KeyboardHelpWidget:
    """Widget helper para mostrar ayuda de navegación."""

    @staticmethod
    def show_help(parent, navigation_manager):
        """Muestra la ayuda de atajos para un manager específico."""
        shortcuts = navigation_manager.get_shortcuts_help()
        dialog = ShortcutHelpDialog(shortcuts, parent)
        dialog.exec()

    @staticmethod
    def create_quick_help_label(shortcuts: Dict[str, str]) -> QLabel:
        """Crea un label con ayuda rápida."""
        quick_shortcuts = {k: v for k, v in list(shortcuts.items())[:3]}

        help_text = " | ".join([f"{k}: {v}" for k, v in quick_shortcuts.items()])
        if len(shortcuts) > 3:
            help_text += " | F1: Más atajos..."

        label = QLabel(help_text)
        label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                padding: 2px 5px;
                font-size: 11px;
                color: #666;
            }
        """)
        return label
