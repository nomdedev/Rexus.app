#!/usr/bin/env python3
"""
Ventana de diálogo para mostrar las obras asociadas a un ítem del inventario
"""


import logging
logger = logging.getLogger(__name__)

import sqlite3

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                            QTableWidget, QTableWidgetItem, QPushButton,
                            QHeaderView, QMessageBox, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from rexus.core.database import get_inventario_connection

class ObrasAsociadasDialog(QDialog):
    """Ventana que muestra las obras donde se usa un material específico"""

    def __init__(self, item_inventario, parent=None):
        super().__init__(parent)
        self.item_inventario = item_inventario
        self.initUI()
        self.cargar_obras_asociadas()

    def initUI(self):
        """Inicializar la interfaz de usuario"""
        self.setWindowTitle(f"Obras que usan: {self.item_inventario.get('descripcion', 'Material')}")
        self.setModal(True)
        self.resize(800, 600)

        # Layout principal
        layout = QVBoxLayout()

        # Información del material
        info_frame = QFrame()
        info_frame.setFrameStyle(QFrame.Shape.Box)
        info_layout = QVBoxLayout(info_frame)

        # Título
        titulo = QLabel("Información del Material")
        titulo.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        info_layout.addWidget(titulo)

        # Detalles del material
        codigo = self.item_inventario.get('codigo', 'N/A')
        descripcion = self.item_inventario.get('descripcion', 'N/A')
        tipo = self.item_inventario.get('tipo', 'N/A')
        stock_actual = self.item_inventario.get('stock_actual', 0)

        info_layout.addWidget(QLabel(f"Código: {codigo}"))
        info_layout.addWidget(QLabel(f"Descripción: {descripcion}"))
        info_layout.addWidget(QLabel(f"Tipo: {tipo}"))
        info_layout.addWidget(QLabel(f"Stock Actual: {stock_actual}"))

        layout.addWidget(info_frame)

        # Título de la tabla
        titulo_tabla = QLabel("Obras que utilizan este material:")
        titulo_tabla.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout.addWidget(titulo_tabla)

        # Tabla de obras asociadas
        self.tabla_obras = QTableWidget()
        self.tabla_obras.setColumnCount(6)
        self.tabla_obras.setHorizontalHeaderLabels([
            "ID Obra", "Nombre Obra", "Cantidad Usada",
            "Precio Unit.", "Total", "Estado"
        ])

        # Configurar tabla
        header = self.tabla_obras.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Nombre obra
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Cantidad
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Precio
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Total
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Estado

        # Aplicar estilos de alto contraste
        self.aplicar_estilos_tabla()

        layout.addWidget(self.tabla_obras)

        # Botones
        botones_layout = QHBoxLayout()

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.close)

        btn_exportar = QPushButton("Exportar")
        btn_exportar.clicked.connect(self.exportar_datos)

        botones_layout.addStretch()
        botones_layout.addWidget(btn_exportar)
        botones_layout.addWidget(btn_cerrar)

        layout.addLayout(botones_layout)

        self.setLayout(layout)

    def aplicar_estilos_tabla(self):
        """Aplicar estilos de alto contraste consistentes"""
        style = """
        QTableWidget {
            background-color: #ffffff;
            color: #000000;
            border: 2px solid #0066cc;
            font-size: 13px;
            font-weight: normal;
            gridline-color: #cccccc;
            selection-background-color: #0066cc;
            selection-color: #ffffff;
        }
        QTableWidget::item {
            padding: 8px;
            border-bottom: 1px solid #e0e0e0;
        }
        QTableWidget::item:selected {
            background-color: #0066cc;
            color: #ffffff;
            font-weight: bold;
        }
        QHeaderView::section {
            background-color: #f0f0f0;
            color: #000000;
            font-weight: bold;
            font-size: 13px;
            padding: 8px;
            border: 1px solid #cccccc;
        }
        """
        self.tabla_obras.setStyleSheet(style)

    def cargar_obras_asociadas(self):
        """Cargar las obras que usan este material específico por código exacto"""
        try:
            conn = get_inventario_connection()
            cursor = conn.cursor()

            # Obtener código específico del material seleccionado
            item_codigo = self.item_inventario.get('codigo', '').strip()
            self.item_inventario.get('descripcion', '').strip()

            logger.info(f"[DEBUG] Buscando obras para código específico: '{item_codigo}'")

            # Query para buscar obras que usan exactamente este código de inventario
            query = """
            SELECT DISTINCT
                o.id as obra_id,
                o.nombre as obra_nombre,
                d.detalle,
                d.cantidad,
                d.precio_unitario,
                d.precio_total,
                ISNULL(o.estado, 'Activa') as estado
            FROM obras o
            INNER JOIN detalles_obra d ON o.id = d.obra_id
            WHERE d.codigo_inventario = ?
            ORDER BY o.nombre, d.detalle
            """

            cursor.execute(query, (item_codigo,))
            obras = cursor.fetchall()

            logger.info(f"[DEBUG] Encontradas {len(obras)} obras que usan el código '{item_codigo}'")

            self.tabla_obras.setRowCount(len(obras))

            if not obras:
                # Mostrar mensaje cuando no hay obras asociadas
                self.tabla_obras.setRowCount(1)
                self.tabla_obras.setItem(0, 0, QTableWidgetItem(""))
                self.tabla_obras.setItem(0, 1, QTableWidgetItem(f"No se encontraron obras que usen el código: {item_codigo}"))
                self.tabla_obras.setItem(0, 2, QTableWidgetItem(""))
                self.tabla_obras.setItem(0, 3, QTableWidgetItem(""))
                self.tabla_obras.setItem(0, 4, QTableWidgetItem(""))
                self.tabla_obras.setItem(0, 5, QTableWidgetItem(""))

                # Centrar el mensaje
                item = self.tabla_obras.item(0, 1)
                if item:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            else:
                total_cantidad_usada = 0
                total_importe = 0

                for row, obra in enumerate(obras):
                    obra_id, obra_nombre, detalle, cantidad, precio_unit, precio_total, estado = obra

                    self.tabla_obras.setItem(row, 0, QTableWidgetItem(str(obra_id)))
                    self.tabla_obras.setItem(row, 1, QTableWidgetItem(str(obra_nombre or 'Sin nombre')))
                    self.tabla_obras.setItem(row, 2, QTableWidgetItem(str(cantidad or 0)))
                    self.tabla_obras.setItem(row, 3, QTableWidgetItem(f"${precio_unit or 0:.2f}"))
                    self.tabla_obras.setItem(row, 4, QTableWidgetItem(f"${precio_total or 0:.2f}"))
                    self.tabla_obras.setItem(row, 5, QTableWidgetItem(str(estado or 'Activa')))

                    logger.info(f"[DEBUG] Fila {row}: {obra_nombre} - {detalle} - Cant: {cantidad}")

                    # Acumular totales
                    if cantidad:
                        total_cantidad_usada += float(cantidad)
                    if precio_total:
                        total_importe += float(precio_total)

                # Actualizar título con totales
                titulo_con_totales = (f"Obras que usan el código {item_codigo}: "
                                    f"{len(obras)} materiales - "
                                    f"Cantidad total: {total_cantidad_usada} - "
                                    f"Importe total: ${total_importe:.2f}")

                # Buscar el QLabel del título y actualizarlo
                for widget in self.findChildren(QLabel):
                    if "Obras que utilizan" in widget.text() or "Obras que usan" in widget.text():
                        widget.setText(titulo_con_totales)
                        break

            conn.close()

        except (sqlite3.Error, AttributeError, ValueError, TypeError) as e:
            # sqlite3.Error: errores de base de datos
            # AttributeError: objeto None o sin atributos  
            # ValueError: conversión de tipos incorrecta
            # TypeError: tipo de dato incorrecto
            QMessageBox.critical(self, "Error", f"Error al cargar obras asociadas: {str(e)}")
            logger.info(f"[ERROR] Error cargando obras asociadas: {e}")
            import traceback
            traceback.print_exc()
            obras = cursor.fetchall()

            self.tabla_obras.setRowCount(len(obras))

            if not obras:
                # Mostrar mensaje cuando no hay obras asociadas
                self.tabla_obras.setRowCount(1)
                self.tabla_obras.setItem(0, 0, QTableWidgetItem(""))
                self.tabla_obras.setItem(0, 1, QTableWidgetItem("No se encontraron obras que usen este material"))
                self.tabla_obras.setItem(0, 2, QTableWidgetItem(""))
                self.tabla_obras.setItem(0, 3, QTableWidgetItem(""))
                self.tabla_obras.setItem(0, 4, QTableWidgetItem(""))
                self.tabla_obras.setItem(0, 5, QTableWidgetItem(""))

                # Centrar el mensaje
                item = self.tabla_obras.item(0, 1)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            else:
                total_cantidad_usada = 0
                total_importe = 0

                for row, obra in enumerate(obras):
                    obra_id, obra_nombre, cantidad, precio_unit, precio_total, estado = obra

                    self.tabla_obras.setItem(row, 0, QTableWidgetItem(str(obra_id)))
                    self.tabla_obras.setItem(row, 1, QTableWidgetItem(str(obra_nombre or 'Sin nombre')))
                    self.tabla_obras.setItem(row, 2, QTableWidgetItem(str(cantidad or 0)))
                    self.tabla_obras.setItem(row, 3, QTableWidgetItem(f"${precio_unit or 0:.2f}"))
                    self.tabla_obras.setItem(row, 4, QTableWidgetItem(f"${precio_total or 0:.2f}"))
                    self.tabla_obras.setItem(row, 5, QTableWidgetItem(str(estado or 'Activa')))

                    # Acumular totales
                    if cantidad:
                        total_cantidad_usada += float(cantidad)
                    if precio_total:
                        total_importe += float(precio_total)

                # Actualizar título con totales
                titulo_con_totales = (f"Obras que utilizan este material: "
                                    f"{len(obras)} obras - "
                                    f"Cantidad total: {total_cantidad_usada} - "
                                    f"Importe total: ${total_importe:.2f}")

                # Buscar el QLabel del título y actualizarlo
                for widget in self.findChildren(QLabel):
                    if "Obras que utilizan" in widget.text():
                        widget.setText(titulo_con_totales)
                        break

            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar obras asociadas: {str(e)}")
            logger.info(f"[ERROR] Error cargando obras asociadas: {e}")

    def exportar_datos(self):
        """Exportar datos a CSV"""
        try:
            import csv
            import os
            from datetime import datetime

            # Crear nombre de archivo
            codigo = self.item_inventario.get('codigo', 'material')
            timestamp = datetime.now().strftime()
            filename = f"obras_material_{codigo}_{timestamp}.csv"
            filepath = os.path.join(os.getcwd(), filename)

            # Escribir CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)

                # Encabezados
                headers = []
                for col in range(self.tabla_obras.columnCount()):
                    headers.append(self.tabla_obras.horizontalHeaderItem(col).text())
                writer.writerow(headers)

                # Datos
                for row in range(self.tabla_obras.rowCount()):
                    row_data = []
                    for col in range(self.tabla_obras.columnCount()):
                        item = self.tabla_obras.item(row, col)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)

            QMessageBox.information(self, "Éxito", f"Datos exportados a: {filename}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al exportar: {str(e)}")
