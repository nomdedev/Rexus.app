"""
Vista Completa de Pedidos - Rexus.app v2.0.0

Vista moderna y completa para gestión de pedidos con CRUD completo,
integración con inventario y experiencia de usuario optimizada.
"""


import logging
logger = logging.getLogger(__name__)

                        elif prioridad == 'ALTA':
                prioridad_item.setBackground(Qt.GlobalColor.magenta)

            self.tabla_pedidos.setItem(row, 5, prioridad_item)

            self.tabla_pedidos.setItem(row, 6,
                QTableWidgetItem(f"$ {pedido.get('total', 0):.2f}"))
            self.tabla_pedidos.setItem(row, 7,
                QTableWidgetItem(str(pedido.get('productos', 0))))
            self.tabla_pedidos.setItem(row, 8,
                QTableWidgetItem(pedido.get('observaciones', '')))

            # Botón de acciones
            btn_acciones = QPushButton("Ver Detalle")
            btn_acciones.clicked.connect(lambda checked, r=row: self.ver_detalle_pedido(r))
            self.tabla_pedidos.setCellWidget(row, 9, btn_acciones)

    def actualizar_estadisticas_demo(self):
        """Actualiza las estadísticas con datos demo."""
        stats = {
            'total_pedidos': '3',
            'pendientes': '1',
            'en_producción': '1',
            'entregados': '1',
            'facturación_total': '$ 56,301.25'
        }

        for key, value in stats.items():
            if key in self.labels_estadisticas:
                self.labels_estadisticas[key].setText(value)

    def actualizar_estadisticas(self):
        """Actualiza las estadísticas del panel."""
        try:
            # Implementar cálculos reales desde el controlador/modelo
            from rexus.core.database import get_inventario_connection
            
            db_connection = get_inventario_connection()
            if db_connection:
                cursor = db_connection.cursor()
                
                # Calcular estadísticas reales de pedidos (asumiendo tabla pedidos existe)
                stats = {}
                
                # Total de pedidos
                try:
                    cursor.execute()
                    stats["Total Pedidos"] = str(cursor.fetchone()[0])
                except:
                    stats["Total Pedidos"] = "0"
                
                # Pedidos pendientes
                try:
                    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE estado = 'PENDIENTE'")
                    stats["Pendientes"] = str(cursor.fetchone()[0])
                except:
                    stats["Pendientes"] = "0"
                
                # Pedidos confirmados
                try:
                    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE estado = 'CONFIRMADO'")
                    stats["Confirmados"] = str(cursor.fetchone()[0])
                except:
                    stats["Confirmados"] = "0"
                
                # En producción
                try:
                    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE estado = 'PRODUCCION'")
                    stats["En Producción"] = str(cursor.fetchone()[0])
                except:
                    stats["En Producción"] = "0"
                
                # Entregados
                try:
                    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE estado = 'ENTREGADO'")
                    stats["Entregados"] = str(cursor.fetchone()[0])
                except:
                    stats["Entregados"] = "0"
                
                # Monto total
                try:
                    cursor.execute("SELECT SUM(total) FROM pedidos WHERE estado != 'CANCELADO'")
                    total = cursor.fetchone()[0]
                    stats["Monto Total"] = f"${total:,.2f}" if total else "$0.00"
                except:
                    stats["Monto Total"] = "$0.00"
                
                self.cargar_estadisticas(stats)
            else:
                # Fallback a estadísticas por defecto
                stats = {
                    "Total Pedidos": "0",
                    "Pendientes": "0", 
                    "Confirmados": "0",
                    "En Producción": "0",
                    "Entregados": "0",
                    "Monto Total": "$0.00"
                }
                self.cargar_estadisticas(stats)
        except Exception as e:
            # En caso de error, mostrar estadísticas por defecto
            stats = {
                "Total Pedidos": "0",
                "Pendientes": "0",
                "Confirmados": "0", 
                "En Producción": "0",
                "Entregados": "0",
                "Monto Total": "$0.00"
            }
            self.cargar_estadisticas(stats)

    def ver_detalle_pedido(self, row):
        """Muestra el detalle del pedido."""
        codigo_item = self.tabla_pedidos.item(row, 0)
        if codigo_item:
            show_success(self, "Detalle", f"Viendo detalle del pedido {codigo_item.text()}")

    def agregar_pedido_demo(self, datos):
        """Agrega un pedido de demostración a la tabla."""
        row = self.tabla_pedidos.rowCount()
        self.tabla_pedidos.insertRow(row)

        self.tabla_pedidos.setItem(row, 0, QTableWidgetItem(datos['codigo']))
        self.tabla_pedidos.setItem(row, 1, QTableWidgetItem(datos['cliente']))
        self.tabla_pedidos.setItem(row, 2, QTableWidgetItem(datos['obra']))
        self.tabla_pedidos.setItem(row, 3, QTableWidgetItem(datos['fecha']))
        self.tabla_pedidos.setItem(row, 4, QTableWidgetItem(datos['estado']))
        self.tabla_pedidos.setItem(row, 5, QTableWidgetItem(datos['prioridad']))
        self.tabla_pedidos.setItem(row, 6, QTableWidgetItem(f"$ {datos['total']:.2f}"))
        self.tabla_pedidos.setItem(row, 7, QTableWidgetItem(str(len(datos['productos']))))
        self.tabla_pedidos.setItem(row, 8, QTableWidgetItem(datos['observaciones']))

        btn_acciones = QPushButton("Ver Detalle")
        btn_acciones.clicked.connect(lambda checked, r=row: self.ver_detalle_pedido(r))
        self.tabla_pedidos.setCellWidget(row, 9, btn_acciones)

    def actualizar_fila_pedido(self, row, datos):
        """Actualiza una fila específica con nuevos datos."""
        self.tabla_pedidos.setItem(row, 0, QTableWidgetItem(datos['codigo']))
        self.tabla_pedidos.setItem(row, 1, QTableWidgetItem(datos['cliente']))
        self.tabla_pedidos.setItem(row, 2, QTableWidgetItem(datos['obra']))
        self.tabla_pedidos.setItem(row, 3, QTableWidgetItem(datos['fecha']))
        self.tabla_pedidos.setItem(row, 4, QTableWidgetItem(datos['estado']))
        self.tabla_pedidos.setItem(row, 5, QTableWidgetItem(datos['prioridad']))
        self.tabla_pedidos.setItem(row, 6, QTableWidgetItem(f"$ {datos['total']:.2f}"))
        self.tabla_pedidos.setItem(row, 7, QTableWidgetItem(str(len(datos['productos']))))
        self.tabla_pedidos.setItem(row, 8, QTableWidgetItem(datos['observaciones']))

    def set_model(self, model):
        """Establece el modelo de datos."""
        self.model = model

    def set_controller(self, controller):
        """Establece el controlador."""
        self.controller = controller

    def set_inventario_model(self, inventario_model):
        """Establece el modelo de inventario para integración."""
        self.inventario_model = inventario_model
