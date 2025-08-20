"""
Diálogo para Seleccionar Obra - Inventario Module

Diálogo que permite al usuario seleccionar una obra para asociar presupuestos PDF.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QTableWidget, QTableWidgetItem, QPushButton, QMessageBox,
    QHeaderView, QAbstractItemView, QSplitter, QTextEdit, QFrame
)
from PyQt6.QtGui import QFont


class SeleccionarObraDialog(QDialog):
    """Diálogo para seleccionar una obra activa."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.obra_seleccionada = None
        self.obras_disponibles = []
        self.setup_ui()
        self.cargar_obras()

    def setup_ui(self):
        """Configura la interfaz del diálogo."""
        self.setWindowTitle("Seleccionar Obra para Presupuesto")
        self.setFixedSize(800, 600)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # Header
        header_label = QLabel("📋 Seleccionar Obra para Asociar Presupuesto")
        header_font = QFont()
        header_font.setPointSize(14)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_label.setStyleSheet("color: #1e40af; padding: 8px 0px;")
        layout.addWidget(header_label)

        # Búsqueda
        search_layout = QHBoxLayout()
        search_label = QLabel("🔍 Buscar:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por nombre, código o descripción...")
        self.search_input.textChanged.connect(self.filtrar_obras)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Splitter para dividir tabla y detalles
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Panel izquierdo - Lista de obras
        left_panel = QFrame()
        left_layout = QVBoxLayout(left_panel)
        
        obras_label = QLabel("Obras Activas:")
        obras_label.setStyleSheet("font-weight: bold; color: #374151;")
        left_layout.addWidget(obras_label)

        # Tabla de obras
        self.tabla_obras = QTableWidget()
        self.setup_tabla_obras()
        left_layout.addWidget(self.tabla_obras)
        
        splitter.addWidget(left_panel)

        # Panel derecho - Detalles de obra
        right_panel = QFrame()
        right_layout = QVBoxLayout(right_panel)
        
        detalles_label = QLabel("Detalles de la Obra:")
        detalles_label.setStyleSheet("font-weight: bold; color: #374151;")
        right_layout.addWidget(detalles_label)

        self.detalles_text = QTextEdit()
        self.detalles_text.setReadOnly(True)
        self.detalles_text.setMaximumHeight(200)
        self.detalles_text.setPlaceholderText("Seleccione una obra para ver sus detalles...")
        right_layout.addWidget(self.detalles_text)

        # Info adicional
        info_label = QLabel("💡 El presupuesto PDF se asociará a la obra seleccionada")
        info_label.setStyleSheet("color: #6b7280; font-style: italic; padding: 8px;")
        right_layout.addWidget(info_label)
        
        right_layout.addStretch()
        splitter.addWidget(right_panel)
        
        # Configurar proporciones del splitter
        splitter.setSizes([500, 300])
        layout.addWidget(splitter)

        # Botones
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.btn_cancelar = QPushButton("❌ Cancelar")
        self.btn_cancelar.clicked.connect(self.reject)
        button_layout.addWidget(self.btn_cancelar)

        self.btn_seleccionar = QPushButton("✅ Seleccionar Obra")
        self.btn_seleccionar.setEnabled(False)
        self.btn_seleccionar.clicked.connect(self.aceptar_seleccion)
        self.btn_seleccionar.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:disabled {
                background-color: #d1d5db;
                color: #6b7280;
            }
        """)
        button_layout.addWidget(self.btn_seleccionar)

        layout.addLayout(button_layout)

    def setup_tabla_obras(self):
        """Configura la tabla de obras."""
        headers = ["ID", "Código", "Nombre", "Estado", "Fecha Inicio", "Presupuesto"]
        self.tabla_obras.setColumnCount(len(headers))
        self.tabla_obras.setHorizontalHeaderLabels(headers)

        # Configurar header
        header = self.tabla_obras.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Código
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)          # Nombre
        
        # Configurar selección
        self.tabla_obras.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla_obras.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tabla_obras.setAlternatingRowColors(True)
        
        # Conectar eventos
        self.tabla_obras.itemSelectionChanged.connect(self.on_obra_seleccionada)
        self.tabla_obras.itemDoubleClicked.connect(self.aceptar_seleccion)

    def cargar_obras(self):
        """Carga las obras disponibles desde el modelo."""
        try:
            # Simular carga de obras (en la implementación real, obtener del modelo)
            self.obras_disponibles = [
                {
                    'id': 1,
                    'codigo': 'OBR-001',
                    'nombre': 'Construcción Edificio Central',
                    'descripcion': 'Construcción de edificio de oficinas de 5 pisos',
                    'estado': 'En Progreso',
                    'fecha_inicio': '2024-01-15',
                    'presupuesto_total': 2500000.0,
                    'cliente': 'Constructora ABC',
                    'ubicacion': 'Av. Principal 123'
                },
                {
                    'id': 2,
                    'codigo': 'OBR-002',
                    'nombre': 'Remodelación Casa Familiar',
                    'descripcion': 'Remodelación completa de casa de 2 pisos',
                    'estado': 'Planificación',
                    'fecha_inicio': '2024-02-01',
                    'presupuesto_total': 850000.0,
                    'cliente': 'Familia García',
                    'ubicacion': 'Calle Secundaria 456'
                },
                {
                    'id': 3,
                    'codigo': 'OBR-003',
                    'nombre': 'Instalación Sistema Solar',
                    'descripcion': 'Instalación de paneles solares en techo',
                    'estado': 'En Progreso',
                    'fecha_inicio': '2024-01-20',
                    'presupuesto_total': 450000.0,
                    'cliente': 'Empresa Verde SA',
                    'ubicacion': 'Zona Industrial Lote 10'
                }
            ]
            
            self.actualizar_tabla_obras()
            
        except Exception as e:
            QMessageBox.warning(self, "Advertencia", f"Error cargando obras: {str(e)}")

    def actualizar_tabla_obras(self):
        """Actualiza la tabla con las obras filtradas."""
        obras_filtradas = self.filtrar_obras_por_texto()
        
        self.tabla_obras.setRowCount(len(obras_filtradas))
        
        for row, obra in enumerate(obras_filtradas):
            self.tabla_obras.setItem(row, 0, QTableWidgetItem(str(obra['id'])))
            self.tabla_obras.setItem(row, 1, QTableWidgetItem(obra['codigo']))
            self.tabla_obras.setItem(row, 2, QTableWidgetItem(obra['nombre']))
            self.tabla_obras.setItem(row, 3, QTableWidgetItem(obra['estado']))
            self.tabla_obras.setItem(row, 4, QTableWidgetItem(obra['fecha_inicio']))
            self.tabla_obras.setItem(row, 5, QTableWidgetItem(f"${obra['presupuesto_total']:,.0f}"))

    def filtrar_obras_por_texto(self):
        """Filtra las obras basado en el texto de búsqueda."""
        texto_busqueda = self.search_input.text().lower()
        
        if not texto_busqueda:
            return self.obras_disponibles
            
        obras_filtradas = []
        for obra in self.obras_disponibles:
            if (texto_busqueda in obra['nombre'].lower() or
                texto_busqueda in obra['codigo'].lower() or
                texto_busqueda in obra['descripcion'].lower()):
                obras_filtradas.append(obra)
                
        return obras_filtradas

    def filtrar_obras(self):
        """Método llamado cuando cambia el texto de búsqueda."""
        self.actualizar_tabla_obras()

    def on_obra_seleccionada(self):
        """Maneja la selección de una obra en la tabla."""
        current_row = self.tabla_obras.currentRow()
        
        if current_row >= 0:
            # Obtener ID de la obra seleccionada
            id_item = self.tabla_obras.item(current_row, 0)
            if id_item:
                obra_id = int(id_item.text())
                
                # Buscar la obra completa
                for obra in self.obras_disponibles:
                    if obra['id'] == obra_id:
                        self.obra_seleccionada = obra
                        self.mostrar_detalles_obra(obra)
                        self.btn_seleccionar.setEnabled(True)
                        break
        else:
            self.obra_seleccionada = None
            self.detalles_text.clear()
            self.btn_seleccionar.setEnabled(False)

    def mostrar_detalles_obra(self, obra):
        """Muestra los detalles de la obra seleccionada."""
        detalles = f"""
📋 <b>Información de la Obra</b>

<b>Código:</b> {obra['codigo']}
<b>Nombre:</b> {obra['nombre']}
<b>Descripción:</b> {obra['descripcion']}

<b>Estado:</b> {obra['estado']}
<b>Fecha de Inicio:</b> {obra['fecha_inicio']}
<b>Presupuesto Total:</b> ${obra['presupuesto_total']:,.0f}

<b>Cliente:</b> {obra['cliente']}
<b>Ubicación:</b> {obra['ubicacion']}

<i>Al confirmar, el presupuesto PDF se asociará a esta obra.</i>
        """
        
        self.detalles_text.setHtml(detalles.strip())

    def aceptar_seleccion(self):
        """Confirma la selección de la obra."""
        if self.obra_seleccionada:
            self.accept()
        else:
            QMessageBox.warning(self, "Advertencia", "Debe seleccionar una obra")

    def get_obra_seleccionada(self):
        """Retorna la obra seleccionada."""
        return self.obra_seleccionada