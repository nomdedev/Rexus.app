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

Vista de Cronograma de Obras

Muestra las obras en un cronograma visual para facilitar la planificación y seguimiento.
"""


import logging
logger = logging.getLogger(__name__)

import datetime
                    self.actualizar_cronograma()

    def zoom_out(self):
        """Aumenta el rango de fechas visible (zoom out)."""
        fecha_inicio = self.date_desde.date()
        fecha_fin = self.date_hasta.date()

        # Aumentar el rango
        dias_totales = fecha_inicio.daysTo(fecha_fin)
        aumento = dias_totales // 2

        self.date_desde.setDate(fecha_inicio.addDays(-aumento))
        self.date_hasta.setDate(fecha_fin.addDays(aumento))
        self.actualizar_cronograma()

    def exportar_cronograma(self):
        """Exporta el cronograma a PDF o imagen."""
        try:
            from PyQt6.QtWidgets import QFileDialog, QMessageBox
            from PyQt6.QtGui import QPainter
            from PyQt6.QtCore import QDir
            
            # Seleccionar ubicación y formato de archivo
            file_path, file_filter = QFileDialog.getSaveFileName(
                self,
                ,
                QDir.homePath() + "/cronograma_obras.png",
                "Imagen PNG (*.png);;Imagen JPG (*.jpg);;PDF (*.pdf)"
            )
            
            if file_path:
                if file_path.endswith('.pdf'):
                    # Exportar a PDF
                    from PyQt6.QtPrintSupport import QPrinter
                    from PyQt6.QtGui import QPainter
                    
                    printer = QPrinter(QPrinter.PrinterMode.HighResolution)
                    printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
                    printer.setOutputFileName(file_path)
                    printer.setPageOrientation(QPrinter.PageOrientation.Landscape)
                    
                    painter = QPainter(printer)
                    self.canvas.render(painter)
                    painter.end()
                else:
                    # Exportar a imagen
                    pixmap = self.canvas.grab()
                    success = pixmap.save(file_path)
                    
                    if not success:
                        QMessageBox.warning(self, , "No se pudo guardar la imagen")
                        return
                
                QMessageBox.information(
                    self, "Exportar", f"Cronograma exportado exitosamente a:\n{file_path}"
                )
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self, , f"Error al exportar cronograma: {str(e)}"
            )

    def configurar_estilos(self):
        """Configura los estilos de la vista."""
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 12px;
            }
            QComboBox, QDateEdit, QPushButton {
                padding: 6px 12px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                font-size: 12px;
            }
            QComboBox:hover, QDateEdit:hover, QPushButton:hover {
                border-color: #3498db;
            }
            QPushButton {
                background-color: #ecf0f1;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d5dbdb;
            }
            QPushButton:pressed {
                background-color: #bdc3c7;
            }
            QLabel {
                font-weight: bold;
                color: #2c3e50;
            }
        """)


class CronogramaWidget(QWidget):
    """Widget personalizado para dibujar el cronograma."""

    obra_clickeada = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.obras = []
        self.fecha_inicio = datetime.date.today()
        self.fecha_fin = datetime.date.today() + datetime.timedelta(days=365)
        self.escala = "mensual"
        self.altura_fila = 40
        self.ancho_etiqueta = 200
        self.obra_seleccionada = None

        self.setMinimumSize(800, 400)
        self.setMouseTracking(True)

    def actualizar_cronograma(
        self,
        obras: List[Dict[str, Any]],
        fecha_inicio: datetime.date,
        fecha_fin: datetime.date,
        escala: str,
    ):
        """Actualiza los datos del cronograma."""
        self.obras = obras
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.escala = escala

        # Calcular altura necesaria
        altura_necesaria = len(obras) * self.altura_fila + 100
        self.setMinimumHeight(altura_necesaria)

        self.update()

    def paintEvent(self, event):
        """Dibuja el cronograma."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Limpiar fondo
        painter.fillRect(self.rect(), QColor(255, 255, 255))

        if not self.obras:
            self.dibujar_mensaje_vacio(painter)
            return

        # Dibujar líneas de tiempo
        self.dibujar_lineas_tiempo(painter)

        # Dibujar obras
        self.dibujar_obras(painter)

        # Dibujar línea de hoy
        self.dibujar_linea_hoy(painter)

    def dibujar_mensaje_vacio(self, painter: QPainter):
        """Dibuja un mensaje cuando no hay obras."""
        painter.setPen(QPen(QColor(149, 165, 166), 2))
        painter.setFont(QFont("Arial", 16))
        rect = self.rect()
        painter.drawText(
            rect, Qt.AlignmentFlag.AlignCenter, "No hay obras para mostrar"
        )

    def dibujar_lineas_tiempo(self, painter: QPainter):
        """Dibuja las líneas de tiempo del cronograma."""
        painter.setPen(QPen(QColor(189, 195, 199), 1))

        # Área de cronograma
        x_inicio = self.ancho_etiqueta
        ancho_cronograma = self.width() - x_inicio - 20

        # Calcular posiciones de las líneas de tiempo
        dias_totales = (self.fecha_fin - self.fecha_inicio).days
        if dias_totales <= 0:
            return

        # Dibujar líneas verticales según la escala
        if self.escala == "mensual":
            self.dibujar_lineas_mensuales(painter, x_inicio, ancho_cronograma)
        elif self.escala == "semanal":
            self.dibujar_lineas_semanales(painter, x_inicio, ancho_cronograma)
        else:  # diario
            self.dibujar_lineas_diarias(painter, x_inicio, ancho_cronograma)

    def dibujar_lineas_mensuales(self,
painter: QPainter,
        x_inicio: int,
        ancho: int):
        """Dibuja líneas mensuales."""
        painter.setPen(QPen(QColor(127, 140, 141), 1))
        painter.setFont(QFont("Arial", 10))

        fecha_actual = self.fecha_inicio.replace(day=1)  # Primer día del mes

        while fecha_actual <= self.fecha_fin:
            # Calcular posición X
            dias_desde_inicio = (fecha_actual - self.fecha_inicio).days
            dias_totales = (self.fecha_fin - self.fecha_inicio).days

            if dias_totales > 0:
                x = x_inicio + int((dias_desde_inicio / dias_totales) * ancho)

                # Dibujar línea vertical
                painter.drawLine(x, 0, x, self.height())

                # Dibujar etiqueta de mes
                mes_texto = fecha_actual.strftime("%b %Y")
                painter.drawText(x + 5, 15, mes_texto)

            # Siguiente mes
            if fecha_actual.month == 12:
                fecha_actual = fecha_actual.replace(year=fecha_actual.year + 1, month=1)
            else:
                fecha_actual = fecha_actual.replace(month=fecha_actual.month + 1)

    def dibujar_lineas_semanales(self,
painter: QPainter,
        x_inicio: int,
        ancho: int):
        """Dibuja líneas semanales."""
        painter.setPen(QPen(QColor(127, 140, 141), 1))
        painter.setFont(QFont("Arial", 9))

        # Encontrar el primer lunes
        fecha_actual = self.fecha_inicio
        while fecha_actual.weekday() != 0:  # 0 = Lunes
            fecha_actual += datetime.timedelta(days=1)

        while fecha_actual <= self.fecha_fin:
            dias_desde_inicio = (fecha_actual - self.fecha_inicio).days
            dias_totales = (self.fecha_fin - self.fecha_inicio).days

            if dias_totales > 0:
                x = x_inicio + int((dias_desde_inicio / dias_totales) * ancho)

                painter.drawLine(x, 0, x, self.height())

                # Etiqueta de semana
                semana_texto = fecha_actual.strftime("%d/%m")
                painter.drawText(x + 2, 15, semana_texto)

            fecha_actual += datetime.timedelta(days=7)

    def dibujar_lineas_diarias(self,
painter: QPainter,
        x_inicio: int,
        ancho: int):
        """Dibuja líneas diarias."""
        painter.setPen(QPen(QColor(189, 195, 199), 1))
        painter.setFont(QFont("Arial", 8))

        dias_totales = (self.fecha_fin - self.fecha_inicio).days
        if dias_totales > 100:  # Demasiados días, mostrar solo algunos
            intervalo = dias_totales // 50
        else:
            intervalo = 1

        for i in range(0, dias_totales, intervalo):
            fecha_actual = self.fecha_inicio + datetime.timedelta(days=i)
            x = x_inicio + int((i / dias_totales) * ancho)

            painter.drawLine(x, 0, x, self.height())

            if i % (intervalo * 7) == 0:  # Etiqueta cada semana
                dia_texto = fecha_actual.strftime("%d/%m")
                painter.drawText(x + 2, 15, dia_texto)

    def dibujar_obras(self, painter: QPainter):
        """Dibuja las barras de las obras."""
        y_actual = 30

        for obra in self.obras:
            self.dibujar_obra(painter, obra, y_actual)
            y_actual += self.altura_fila

    def dibujar_obra(self, painter: QPainter, obra: Dict[str, Any], y: int):
        """Dibuja una obra individual."""
        # Datos de la obra
        codigo = obra.get("codigo", "Sin código")
        nombre = obra.get("nombre", "Sin nombre")
        obra.get("estado", "PLANIFICACION")
        fecha_inicio = obra.get("fecha_inicio")
        fecha_fin = obra.get("fecha_fin_estimada")

        # Convertir fechas
        if isinstance(fecha_inicio, str):
            fecha_inicio = datetime.datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
        if isinstance(fecha_fin, str):
            fecha_fin = datetime.datetime.strptime(fecha_fin, "%Y-%m-%d").date()

        if not fecha_inicio:
            return

        # Dibujar etiqueta de obra
        etiqueta_rect = QRect(5,
y,
            self.ancho_etiqueta - 10,
            self.altura_fila - 5)
        painter.fillRect(etiqueta_rect, QColor(236, 240, 241))
        painter.setPen(QPen(QColor(44, 62, 80), 1))
        painter.drawRect(etiqueta_rect)

        # Texto de la etiqueta
        painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        painter.drawText(
            etiqueta_rect.adjusted(5,
2,
                -5,
                -2),
                Qt.AlignmentFlag.AlignTop,
                codigo
        )

        painter.setFont(QFont("Arial", 9))
        painter.drawText(
            etiqueta_rect.adjusted(5,
18,
                -5,
                -2),
                Qt.AlignmentFlag.AlignTop,
                nombre
        )

        # Dibujar barra de cronograma
        self.dibujar_barra_cronograma(painter,
obra,
            fecha_inicio,
            fecha_fin,
            y)

    def dibujar_barra_cronograma(
        self,
        painter: QPainter,
        obra: Dict[str, Any],
        fecha_inicio: datetime.date,
        fecha_fin: datetime.date,
        y: int,
    ):
        """Dibuja la barra de cronograma de una obra."""
        estado = obra.get("estado", "PLANIFICACION")

        # Colores por estado
        colores_estado = {
            "PLANIFICACION": QColor(241, 196, 15),  # Amarillo
            "EN_PROCESO": QColor(46, 204, 113),  # Verde
            "PAUSADA": QColor(231, 76, 60),  # Rojo
            "FINALIZADA": QColor(52, 152, 219),  # Azul
            "CANCELADA": QColor(149, 165, 166),  # Gris
        }

        color = colores_estado.get(estado, QColor(189, 195, 199))

        # Calcular posición y tamaño de la barra
        x_inicio = self.ancho_etiqueta
        ancho_cronograma = self.width() - x_inicio - 20

        dias_totales = (self.fecha_fin - self.fecha_inicio).days
        if dias_totales <= 0:
            return

        # Posición de inicio
        dias_hasta_inicio = (fecha_inicio - self.fecha_inicio).days
        x_barra = x_inicio + int((dias_hasta_inicio / dias_totales) * ancho_cronograma)

        # Ancho de la barra
        if fecha_fin:
            dias_duracion = (fecha_fin - fecha_inicio).days
            ancho_barra = int((dias_duracion / dias_totales) * ancho_cronograma)
        else:
            ancho_barra = 50  # Barra por defecto si no hay fecha fin

        # Asegurar que la barra sea visible
        if ancho_barra < 3:
            ancho_barra = 3

        # Dibujar barra
        barra_rect = QRect(x_barra, y + 5, ancho_barra, self.altura_fila - 15)

        # Efecto de gradiente
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(color.darker(120), 2))
        painter.drawRoundedRect(barra_rect, 4, 4)

        # Texto del estado en la barra si hay espacio
        if ancho_barra > 60:
            painter.setPen(QPen(QColor(255, 255, 255), 1))
            painter.setFont(QFont("Arial", 8, QFont.Weight.Bold))
            painter.drawText(barra_rect, Qt.AlignmentFlag.AlignCenter, estado)

    def dibujar_linea_hoy(self, painter: QPainter):
        """Dibuja una línea vertical indicando el día de hoy."""
        hoy = datetime.date.today()

        if self.fecha_inicio <= hoy <= self.fecha_fin:
            dias_hasta_hoy = (hoy - self.fecha_inicio).days
            dias_totales = (self.fecha_fin - self.fecha_inicio).days

            if dias_totales > 0:
                x_inicio = self.ancho_etiqueta
                ancho_cronograma = self.width() - x_inicio - 20
                x_hoy = x_inicio + int(
                    (dias_hasta_hoy / dias_totales) * ancho_cronograma
                )

                # Línea roja para "hoy"
                painter.setPen(QPen(QColor(231, 76, 60), 3))
                painter.drawLine(x_hoy, 0, x_hoy, self.height())

                # Etiqueta "HOY"
                painter.setPen(QPen(QColor(255, 255, 255), 1))
                painter.fillRect(x_hoy - 20,
5,
                    40,
                    20,
                    QBrush(QColor(231,
                    76,
                    60)))
                painter.setFont(QFont("Arial", 9, QFont.Weight.Bold))
                painter.drawText(
                    x_hoy - 20, 5, 40, 20, Qt.AlignmentFlag.AlignCenter, "HOY"
                )

    def mousePressEvent(self, event):
        """Maneja clics del mouse."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Determinar qué obra fue clickeada
            y_click = event.position().y()
            obra_index = int((y_click - 30) // self.altura_fila)

            if 0 <= obra_index < len(self.obras):
                obra = self.obras[obra_index]
                self.obra_clickeada.emit(obra)

    def mouseMoveEvent(self, event):
        """Maneja el movimiento del mouse para tooltips."""
        y_mouse = event.position().y()
        obra_index = int((y_mouse - 30) // self.altura_fila)

        if 0 <= obra_index < len(self.obras):
            obra = self.obras[obra_index]
            tooltip_text = self.crear_tooltip_obra(obra)
            QToolTip.showText(event.globalPosition().toPoint(), tooltip_text)

    def crear_tooltip_obra(self, obra: Dict[str, Any]) -> str:
        """Crea el texto del tooltip para una obra."""
        codigo = obra.get("codigo", "Sin código")
        nombre = obra.get("nombre", "Sin nombre")
        cliente = obra.get("cliente", "Sin cliente")
        estado = obra.get("estado", "PLANIFICACION")
        responsable = obra.get("responsable", "Sin responsable")
        fecha_inicio = obra.get("fecha_inicio", "")
        fecha_fin = obra.get("fecha_fin_estimada", "")
        presupuesto = obra.get("presupuesto_total", 0)

        tooltip = f"""
        <b>{codigo}</b><br>
        <b>Nombre:</b> {nombre}<br>
        <b>Cliente:</b> {cliente}<br>
        <b>Estado:</b> {estado}<br>
        <b>Responsable:</b> {responsable}<br>
        <b>Inicio:</b> {fecha_inicio}<br>
        <b>Fin estimado:</b> {fecha_fin}<br>
        <b>Presupuesto:</b> ${presupuesto:,.2f}
        """

        return tooltip.strip()
