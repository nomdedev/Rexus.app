"""
Vista Completa de Compras - Rexus.app v2.0.0

Vista moderna y completa para gestión de compras con CRUD completo,
gestión de proveedores y órdenes de compra funcionales.
"""


import logging
logger = logging.getLogger(__name__)

                        elif prioridad == 'ALTA':
                prioridad_item.setBackground(Qt.GlobalColor.magenta)

            self.tabla_compras.setItem(row, 4, prioridad_item)

            self.tabla_compras.setItem(row, 5,
                                            QTableWidgetItem(f"$ {compra.get('total', 0):.2f}"))
            self.tabla_compras.setItem(row, 6,
                                            QTableWidgetItem(str(compra.get('productos', 0))))
            self.tabla_compras.setItem(row, 7,
                                            QTableWidgetItem(compra.get('fecha_entrega', '')))
            self.tabla_compras.setItem(row, 8,
                                            QTableWidgetItem(compra.get('metodo_pago', '')))
            self.tabla_compras.setItem(row, 9,
                                            QTableWidgetItem(compra.get('observaciones', '')))

            # Botón de acciones
            btn_acciones = QPushButton("Ver Detalle")
            btn_acciones.clicked.connect(lambda checked, r=row: self.ver_detalle_orden_tabla(r))
            self.tabla_compras.setCellWidget(row, 10, btn_acciones)

    def actualizar_estadisticas_demo(self):
        """Actualiza estadísticas con datos demo."""
        stats = {
            'total_órdenes': '3',
            'pendientes': '1',
            'en_proceso': '1',
            'completadas': '1',
            'monto_total': '$ 47,201.25'
        }

        for key, value in stats.items():
            if key in self.labels_estadisticas:
                self.labels_estadisticas[key].setText(value)

    def actualizar_estadisticas(self, estadisticas=None):
        """Actualiza las estadísticas del panel."""
        if not estadisticas:
            estadisticas = {}
        # TODO: Implementar cálculos reales basados en estadisticas parameter

    def ver_detalle_orden_tabla(self, row):
        """Ve el detalle desde botón de tabla."""
        self.tabla_compras.selectRow(row)
        self.ver_detalle_orden()

    def agregar_orden_demo(self, datos):
        """Agrega orden demo a la tabla."""
        row = self.tabla_compras.rowCount()
        self.tabla_compras.insertRow(row)

        self.tabla_compras.setItem(row, 0, QTableWidgetItem(datos['numero_orden']))
        self.tabla_compras.setItem(row, 1, QTableWidgetItem(datos['fecha_orden']))
        self.tabla_compras.setItem(row, 2, QTableWidgetItem(datos['proveedor']))
        self.tabla_compras.setItem(row, 3, QTableWidgetItem(datos['estado']))
        self.tabla_compras.setItem(row, 4, QTableWidgetItem(datos['prioridad']))
        self.tabla_compras.setItem(row, 5, QTableWidgetItem(f"$ {datos['total_final']:.2f}"))
        self.tabla_compras.setItem(row, 6, QTableWidgetItem(str(len(datos['productos']))))
        self.tabla_compras.setItem(row, 7, QTableWidgetItem(datos['fecha_entrega']))
        self.tabla_compras.setItem(row, 8, QTableWidgetItem(datos['metodo_pago']))
        self.tabla_compras.setItem(row, 9, QTableWidgetItem(datos['observaciones']))

        btn_acciones = QPushButton("Ver Detalle")
        btn_acciones.clicked.connect(lambda checked, r=row: self.ver_detalle_orden_tabla(r))
        self.tabla_compras.setCellWidget(row, 10, btn_acciones)

    def actualizar_fila_orden(self, row, datos):
        """Actualiza una fila con nuevos datos."""
        self.tabla_compras.setItem(row, 0, QTableWidgetItem(datos['numero_orden']))
        self.tabla_compras.setItem(row, 1, QTableWidgetItem(datos['fecha_orden']))
        self.tabla_compras.setItem(row, 2, QTableWidgetItem(datos['proveedor']))
        self.tabla_compras.setItem(row, 3, QTableWidgetItem(datos['estado']))
        self.tabla_compras.setItem(row, 4, QTableWidgetItem(datos['prioridad']))
        self.tabla_compras.setItem(row, 5, QTableWidgetItem(f"$ {datos['total_final']:.2f}"))
        self.tabla_compras.setItem(row, 6, QTableWidgetItem(str(len(datos['productos']))))
        self.tabla_compras.setItem(row, 7, QTableWidgetItem(datos['fecha_entrega']))
        self.tabla_compras.setItem(row, 8, QTableWidgetItem(datos['metodo_pago']))
        self.tabla_compras.setItem(row, 9, QTableWidgetItem(datos['observaciones']))

    def set_model(self, model):
        """Establece el modelo."""
        self.model = model

    def set_controller(self, controller):
        """Establece el controlador."""
        self.controller = controller

    def actualizar_tabla(self, compras):
        """Actualiza la tabla principal con datos de compras."""
        if not compras:
            self.tabla_compras.setRowCount(0)
            return
        
        self.tabla_compras.setRowCount(len(compras))
        
        for row, compra in enumerate(compras):
            self.tabla_compras.setItem(row, 0, QTableWidgetItem(str(compra.get('numero_orden', compra.get('id', '')))))
            self.tabla_compras.setItem(row, 1, QTableWidgetItem(str(compra.get('fecha_pedido', compra.get('fecha_creacion', '')))))
            self.tabla_compras.setItem(row, 2, QTableWidgetItem(str(compra.get('proveedor', 'N/A'))))
            self.tabla_compras.setItem(row, 3, QTableWidgetItem(str(compra.get('estado', 'PENDIENTE'))))
            self.tabla_compras.setItem(row, 4, QTableWidgetItem(str(compra.get('prioridad', 'NORMAL'))))
            self.tabla_compras.setItem(row, 5, QTableWidgetItem(f"$ {float(compra.get('total_final', 0)):.2f}"))
            self.tabla_compras.setItem(row, 6, QTableWidgetItem(str(compra.get('total_items', 0))))
            self.tabla_compras.setItem(row, 7, QTableWidgetItem(str(compra.get('fecha_entrega_estimada', 'N/A'))))
            self.tabla_compras.setItem(row, 8, QTableWidgetItem(str(compra.get('metodo_pago', 'CONTADO'))))
            self.tabla_compras.setItem(row, 9, QTableWidgetItem(str(compra.get('observaciones', ''))))
            
            # Botón de acciones
            btn_acciones = QPushButton("Ver Detalle")
            btn_acciones.clicked.connect(lambda checked, r=row: self.ver_detalle_orden_tabla(r))
            self.tabla_compras.setCellWidget(row, 10, btn_acciones)
