"""
Test visual del sistema de notificaciones y bloqueo de avance de obras
Esta aplicación muestra una interfaz que permite probar visualmente el sistema de notificaciones
"""
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

                           QWidget, QPushButton, QLabel, QComboBox, QMessageBox,
                           QTextEdit, QGroupBox, QCheckBox, QTabWidget)
class TestVisualNotificaciones(QMainWindow):
    """
    Aplicación para probar visualmente el sistema de notificaciones y bloqueo de obras
    """
    def __init__(self):
        super().__init__()
        self.db = None
        self.integracion_model = None
        self.sistema_notificaciones = None
        self.obras_combo = None
        self.detalles_text = None
        self.estados_combo = None

        self.setup_db_y_modelos()
        self.init_ui()

    def setup_db_y_modelos(self):
        """Inicializar conexión a BD y modelos"""
        try:
            self.db = ObrasDatabaseConnection()
            self.db.conectar()
            print("✅ Conectado a base de datos")

            self.integracion_model = IntegracionObrasModel(self.db)
            print("✅ Modelo de integración inicializado")
        except Exception as e:
            print(f"❌ Error al conectar: {e}")
            QMessageBox.critical(self, "Error de conexión",
                                f"No se pudo conectar a la base de datos: {str(e)}")

    def init_ui(self):
        """Inicializar interfaz de usuario"""
        self.setWindowTitle("Test Visual - Sistema de Notificaciones de Obras")
        self.setMinimumSize(900, 700)

        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        # Título
        titulo = QLabel("Test Visual del Sistema de Notificaciones y Bloqueo de Avance")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold; margin: 5px;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(titulo)

        # Crear tabs
        tabs = QTabWidget()

        # Tab 1: Sistema de notificaciones
        tab_notificaciones = QWidget()
        notificaciones_layout = QVBoxLayout(tab_notificaciones)

        # Sistema de notificaciones
        self.sistema_notificaciones = SistemaNotificaciones()
        if self.integracion_model is not None:
            self.sistema_notificaciones.integracion_model = self.integracion_model
        notificaciones_layout.addWidget(self.sistema_notificaciones)

        # Botones para sistema de notificaciones
        btn_layout_notif = QHBoxLayout()

        btn_actualizar = QPushButton("🔄 Actualizar Notificaciones")
        btn_actualizar.clicked.connect(self.sistema_notificaciones.actualizar_notificaciones)
        btn_layout_notif.addWidget(btn_actualizar)

        btn_forzar = QPushButton("🧪 Insertar Notificación de Prueba")
        btn_forzar.clicked.connect(self.insertar_notificacion_prueba)
        btn_layout_notif.addWidget(btn_forzar)

        notificaciones_layout.addLayout(btn_layout_notif)
        tabs.addTab(tab_notificaciones, "Sistema de Notificaciones")

        # Tab 2: Prueba de verificación de avance
        tab_avance = QWidget()
        avance_layout = QVBoxLayout(tab_avance)

        # Selector de obra
        obras_group = QGroupBox("Selección de Obra")
        obras_layout = QVBoxLayout(obras_group)

        self.obras_combo = QComboBox()
        self.cargar_obras_en_combo()
        obras_layout.addWidget(self.obras_combo)

        btn_verificar = QPushButton("🔍 Verificar Estado")
        btn_verificar.clicked.connect(self.verificar_obra_seleccionada)
        obras_layout.addWidget(btn_verificar)

        avance_layout.addWidget(obras_group)

        # Detalles de la obra
        detalles_group = QGroupBox("Detalles de Estado")
        detalles_layout = QVBoxLayout(detalles_group)

        self.detalles_text = QTextEdit()
        self.detalles_text.setReadOnly(True)
        detalles_layout.addWidget(self.detalles_text)

        avance_layout.addWidget(detalles_group)

        # Intentar avanzar estado
        avanzar_group = QGroupBox("Prueba de Avance de Estado")
        avanzar_layout = QVBoxLayout(avanzar_group)

        estados_layout = QHBoxLayout()
        estados_layout.addWidget(QLabel("Nuevo estado:"))

        self.estados_combo = QComboBox()
        self.estados_combo.addItems([
            "en_planificacion",
            "en_proceso",
            "esperando_materiales",
            "esperando_vidrios",
            "esperando_herrajes",
            "esperando_pagos",
            "lista_para_avanzar",
            "finalizada"
        ])
        estados_layout.addWidget(self.estados_combo)

        avanzar_layout.addLayout(estados_layout)

        self.forzar_check = QCheckBox("Forzar avance (ignorar bloqueos)")
        avanzar_layout.addWidget(self.forzar_check)

        btn_avanzar = QPushButton("⏭️ Intentar Avanzar Estado")
        btn_avanzar.clicked.connect(self.intentar_avanzar_estado)
        avanzar_layout.addWidget(btn_avanzar)

        avance_layout.addWidget(avanzar_group)
        tabs.addTab(tab_avance, "Prueba de Avance de Estados")

        # Agregar tabs al layout principal
        main_layout.addWidget(tabs)

        # Estado de conexión
        estado_conexion = QLabel("Estado de conexión: Conectado a la base de datos")
        if not self.db or not self.integracion_model:
            estado_conexion.setText("Estado de conexión: ❌ Error de conexión")
            estado_conexion.setStyleSheet("color: red;")
        else:
            estado_conexion.setText("Estado de conexión: ✅ Conectado correctamente")
            estado_conexion.setStyleSheet("color: green;")

        main_layout.addWidget(estado_conexion)

        self.setCentralWidget(central_widget)

    def cargar_obras_en_combo(self):
        """Cargar obras en el combobox"""
        if not self.integracion_model or not self.obras_combo:
            return

        try:
            self.obras_combo.clear()

            obras = self.integracion_model.obras_model.obtener_obras() if hasattr(self.integracion_model, 'obras_model') else []

            for obra in obras:
                # Manejar diferentes formatos de datos (tupla o diccionario)
                if isinstance(obra, tuple):
                    id_obra = obra[0]
                    nombre = obra[1] if len(obra) > 1 else f"Obra {id_obra}"
                    cliente = obra[2] if len(obra) > 2 else "Sin cliente"
                elif isinstance(obra, dict):
                    id_obra = obra.get('id', '?')
                    nombre = obra.get('nombre', f"Obra {id_obra}")
                    cliente = obra.get('cliente', "Sin cliente")
                else:
                    continue

                # Formato: "ID - Nombre (Cliente)"
                texto = f"{id_obra} - {nombre} ({cliente})"
                self.obras_combo.addItem(texto, id_obra)
        except Exception as e:
            print(f"❌ Error al cargar obras: {e}")
            traceback.print_exc()

    def verificar_obra_seleccionada(self):
        """Verificar estado de la obra seleccionada"""
        if not self.integracion_model or not self.obras_combo or not self.detalles_text:
            return

        try:
            # Obtener ID de obra seleccionada
            id_obra = self.obras_combo.currentData()
            if not id_obra:
                return

            # Verificar estado
            estado = self.integracion_model.verificar_estado_completo_obra(id_obra)

            # Mostrar detalles
            txt = f"🏗️ OBRA ID: {id_obra}\n"
            txt += f"📊 Estado general: {estado['estado_general']}\n"
            txt += f"🚦 Puede avanzar: {estado.get('puede_avanzar', False)}\n\n"

            # Detalles por módulo
            txt += "📋 ESTADO POR MÓDULO:\n"
            for modulo, info in estado['modulos'].items():
                txt += f"- {modulo.upper()}: {info['estado']} ({info['pendientes']} pendientes)\n"

                # Mostrar detalles si hay pendientes
                if info['pendientes'] > 0 and info['detalles']:
                    for detalle in info['detalles'][:3]:  # Limitar a 3 detalles
                        txt += f"  • {detalle}\n"

                    if len(info['detalles']) > 3:
                        txt += f"  • ... y {len(info['detalles']) - 3} más\n"

            # Mostrar notificaciones
            txt += "\n🔔 NOTIFICACIONES:\n"
            notificaciones = estado.get('notificaciones', [])
            if notificaciones:
                for notif in notificaciones:
                    txt += f"- [{notif['tipo'].upper()}] {notif['mensaje']}\n"
            else:
                txt += "- No hay notificaciones para esta obra\n"

            self.detalles_text.setPlainText(txt)
        except Exception as e:
            print(f"❌ Error al verificar obra: {e}")
            traceback.print_exc()
            self.detalles_text.setPlainText(f"❌ ERROR: {str(e)}")

    def intentar_avanzar_estado(self):
        """Intentar avanzar el estado de la obra seleccionada"""
        if not self.integracion_model or not self.obras_combo:
            return

        try:
            # Obtener ID de obra y nuevo estado
            id_obra = self.obras_combo.currentData()
            nuevo_estado = self.estados_combo.currentText() if self.estados_combo else None
            forzar = self.forzar_check.isChecked()

            if not id_obra or not nuevo_estado:
                return

            # Intentar avanzar estado
            resultado = self.integracion_model.actualizar_estado_obra(
                id_obra, nuevo_estado, forzar=forzar, usuario_id=1
            )

            # Verificar resultado
            if resultado.get('exito'):
                QMessageBox.information(self, "Estado actualizado",
                                      f"Estado actualizado correctamente a: {nuevo_estado}")

                # Actualizar detalles
                self.verificar_obra_seleccionada()

                # Actualizar notificaciones
                if self.sistema_notificaciones is not None:
                    self.sistema_notificaciones.actualizar_notificaciones()
            else:
                QMessageBox.warning(self, "No se pudo actualizar",
                                   f"No se pudo actualizar el estado: {resultado.get('mensaje', 'Error desconocido')}")
        except Exception as e:
            print(f"❌ Error al intentar avanzar estado: {e}")
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Error al intentar actualizar estado: {str(e)}")

    def insertar_notificacion_prueba(self):
        """Insertar una notificación de prueba en el sistema"""
        if not self.sistema_notificaciones:
            return

        try:
            # Crear notificación de prueba
            notificacion_prueba = {
import os
import sys
import traceback

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import IntegracionObrasModel  # Agregar al sistema
from PyQt6.QtWidgets import (
    ObrasDatabaseConnection,
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QVBoxLayout,
    SistemaNotificaciones,
    12:00:00' },
    '2025-06-25,
    'alta',
    'Esta,
    'mensaje':,
    'prioridad':,
    'timestamp':,
    'tipo':,
    'warning',
    core.database,
    core.integracion_obras,
    de,
    el,
    es,
    from,
    import,
    notificacion_prueba,
    notificación,
    para,
    prueba,
    self.sistema_notificaciones.agregar_notificacion,
    sistema',
    una,
    verificar,
    widgets.sistema_notificaciones,
)

        except Exception as e:
            print(f"❌ Error al insertar notificación: {e}")

    def closeEvent(self, event):
        """Evento de cierre de la ventana"""
        # Cerrar conexión a BD
        if self.db:
            try:
                self.db.cerrar_conexion()
                print("✅ Conexión a base de datos cerrada")
            except:
                pass

        # Aceptar el evento de cierre
        event.accept()

def main():
    """Función principal"""
    app = QApplication.instance() or QApplication(sys.argv)
    window = TestVisualNotificaciones()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
