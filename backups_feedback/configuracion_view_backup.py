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
Vista de Configuración - Rexus.app v2.0.0

Interfaz moderna para gestión de configuraciones del sistema.
""""""

from typing import Any, Dict, List
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class ConfiguracionView(QWidget):
    """Vista modernizada para gestión de configuraciones del sistema."""
    
    # Señales
    solicitud_actualizar_configuracion = pyqtSignal(str, object)  # clave, valor
    solicitud_restaurar_configuracion = pyqtSignal(str)  # clave
    solicitud_exportar_configuracion = pyqtSignal()
    solicitud_importar_configuracion = pyqtSignal()
    solicitud_probar_conexion_bd = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.controller = None
        self.configuraciones_data = []
        self.widgets_configuracion = {}
        
        self.init_ui()
        self.aplicar_estilos()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header_widget = self.crear_header()
        layout.addWidget(header_widget)
        
        # Tabs de configuración
        self.tab_widget = QTabWidget()
        
        # Pestaña de Base de Datos
        tab_database = self.crear_tab_database()
        self.tab_widget.addTab(tab_database, "🗄️ Base de Datos")
        
        # Pestaña de Empresa
        tab_empresa = self.crear_tab_empresa()
        self.tab_widget.addTab(tab_empresa, "🏢 Empresa")
        
        # Pestaña de Sistema
        tab_sistema = self.crear_tab_sistema()
        self.tab_widget.addTab(tab_sistema, "⚙️ Sistema")
        
        # Pestaña de Usuarios
        tab_usuarios = self.crear_tab_usuarios()
        self.tab_widget.addTab(tab_usuarios, "👥 Usuarios")
        
        # Pestaña de Reportes
        tab_reportes = self.crear_tab_reportes()
        self.tab_widget.addTab(tab_reportes, "[CHART] Reportes")
        
        # Pestaña de Tema
        tab_tema = self.crear_tab_tema()
        self.tab_widget.addTab(tab_tema, "🎨 Tema")
        
        # Pestaña de Backup
        tab_backup = self.crear_tab_backup()
        self.tab_widget.addTab(tab_backup, "💾 Backup")
        
        # Pestaña de Integraciones
        tab_integraciones = self.crear_tab_integraciones()
        self.tab_widget.addTab(tab_integraciones, "🔗 Integraciones")
        
        # Pestaña de Todas las Configuraciones
        tab_todas = self.crear_tab_todas_configuraciones()
        self.tab_widget.addTab(tab_todas, "📋 Todas")
        
        layout.addWidget(self.tab_widget)
        
        # Panel de acciones
        acciones_widget = self.crear_panel_acciones()
        layout.addWidget(acciones_widget)
    
    def crear_header(self):
        """Crea el header con título."""
        header = QFrame()
        header.setFixedHeight(80)
        layout = QVBoxLayout(header)
        
        titulo = QLabel("⚙️ Configuración del Sistema")
        titulo.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        titulo.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        
        subtitulo = QLabel("Gestión de configuraciones y parámetros del sistema")
        subtitulo.setFont(QFont("Segoe UI", 12))
        subtitulo.setStyleSheet("color: #7f8c8d;")
        
        layout.addWidget(titulo)
        layout.addWidget(subtitulo)
        layout.addStretch()
        
        return header
    
    def crear_tab_database(self):
        """Crea la pestaña de configuración de base de datos."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Grupo de configuración de conexión
        group_conexion = QGroupBox("Configuración de Conexión")
        form_layout = QFormLayout(group_conexion)
        
        # Crear campos de configuración
        self.widgets_configuracion['db_server'] = QLineEdit()
        self.widgets_configuracion['db_port'] = QSpinBox()
        self.widgets_configuracion['db_port'].setRange(1, 65535)
        self.widgets_configuracion['db_name'] = QLineEdit()
        self.widgets_configuracion['db_user'] = QLineEdit()
        self.widgets_configuracion['db_timeout'] = QSpinBox()
        self.widgets_configuracion['db_timeout'].setRange(1, 300)
        self.widgets_configuracion['db_timeout'].setSuffix(" seg")
        self.widgets_configuracion['db_pool_size'] = QSpinBox()
        self.widgets_configuracion['db_pool_size'].setRange(1, 100)
        
        form_layout.addRow("Servidor:", self.widgets_configuracion['db_server'])
        form_layout.addRow("Puerto:", self.widgets_configuracion['db_port'])
        form_layout.addRow("Base de datos:", self.widgets_configuracion['db_name'])
        form_layout.addRow("Usuario:", self.widgets_configuracion['db_user'])
        form_layout.addRow("Timeout:", self.widgets_configuracion['db_timeout'])
        form_layout.addRow("Pool Size:", self.widgets_configuracion['db_pool_size'])
        
        # Botón de prueba de conexión
        btn_probar = QPushButton("🔍 Probar Conexión")
        btn_probar.clicked.connect(self.solicitud_probar_conexion_bd.emit)
        form_layout.addRow("", btn_probar)
        
        layout.addWidget(group_conexion)
        layout.addStretch()
        
        return widget
    
    def crear_tab_empresa(self):
        """Crea la pestaña de configuración de empresa."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Scroll para el formulario
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Información básica
        group_basica = QGroupBox("Información Básica")
        form_basica = QFormLayout(group_basica)
        
        self.widgets_configuracion['empresa_nombre'] = QLineEdit()
        self.widgets_configuracion['empresa_nit'] = QLineEdit()
        self.widgets_configuracion['empresa_direccion'] = QLineEdit()
        self.widgets_configuracion['empresa_telefono'] = QLineEdit()
        self.widgets_configuracion['empresa_email'] = QLineEdit()
        self.widgets_configuracion['empresa_web'] = QLineEdit()
        
        form_basica.addRow("Nombre:", self.widgets_configuracion['empresa_nombre'])
        form_basica.addRow("NIT:", self.widgets_configuracion['empresa_nit'])
        form_basica.addRow("Dirección:", self.widgets_configuracion['empresa_direccion'])
        form_basica.addRow("Teléfono:", self.widgets_configuracion['empresa_telefono'])
        form_basica.addRow("Email:", self.widgets_configuracion['empresa_email'])
        form_basica.addRow("Sitio web:", self.widgets_configuracion['empresa_web'])
        
        # Información adicional
        group_adicional = QGroupBox("Información Adicional")
        form_adicional = QFormLayout(group_adicional)
        
        self.widgets_configuracion['empresa_moneda'] = QComboBox()
        self.widgets_configuracion['empresa_moneda'].addItems(['COP', 'USD', 'EUR'])
        self.widgets_configuracion['empresa_pais'] = QLineEdit()
        self.widgets_configuracion['empresa_ciudad'] = QLineEdit()
        self.widgets_configuracion['empresa_logo'] = QLineEdit()
        
        form_adicional.addRow("Moneda:", self.widgets_configuracion['empresa_moneda'])
        form_adicional.addRow("País:", self.widgets_configuracion['empresa_pais'])
        form_adicional.addRow("Ciudad:", self.widgets_configuracion['empresa_ciudad'])
        form_adicional.addRow("Logo (URL):", self.widgets_configuracion['empresa_logo'])
        
        scroll_layout.addWidget(group_basica)
        scroll_layout.addWidget(group_adicional)
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        return widget
    
    def crear_tab_sistema(self):
        """Crea la pestaña de configuración del sistema."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Scroll para el formulario
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Configuración general
        group_general = QGroupBox("Configuración General")
        form_general = QFormLayout(group_general)
        
        self.widgets_configuracion['sistema_version'] = QLineEdit()
        self.widgets_configuracion['sistema_version'].setReadOnly(True)
        self.widgets_configuracion['sistema_modo_debug'] = QCheckBox()
        self.widgets_configuracion['sistema_logs_nivel'] = QComboBox()
        self.widgets_configuracion['sistema_logs_nivel'].addItems(['DEBUG', 'INFO', 'WARNING', 'ERROR'])
        self.widgets_configuracion['sistema_max_backups'] = QSpinBox()
        self.widgets_configuracion['sistema_max_backups'].setRange(1, 365)
        
        form_general.addRow("Versión:", self.widgets_configuracion['sistema_version'])
        form_general.addRow("Modo Debug:", self.widgets_configuracion['sistema_modo_debug'])
        form_general.addRow("Nivel de Logs:", self.widgets_configuracion['sistema_logs_nivel'])
        form_general.addRow("Máx. Backups:", self.widgets_configuracion['sistema_max_backups'])
        
        # Configuración de sesión
        group_sesion = QGroupBox("Configuración de Sesión")
        form_sesion = QFormLayout(group_sesion)
        
        self.widgets_configuracion['sistema_timeout_sesion'] = QSpinBox()
        self.widgets_configuracion['sistema_timeout_sesion'].setRange(300, 86400)
        self.widgets_configuracion['sistema_timeout_sesion'].setSuffix(" seg")
        self.widgets_configuracion['sistema_max_intentos_login'] = QSpinBox()
        self.widgets_configuracion['sistema_max_intentos_login'].setRange(1, 10)
        
        form_sesion.addRow("Timeout Sesión:", self.widgets_configuracion['sistema_timeout_sesion'])
        form_sesion.addRow("Máx. Intentos Login:", self.widgets_configuracion['sistema_max_intentos_login'])
        
        # Configuración regional
        group_regional = QGroupBox("Configuración Regional")
        form_regional = QFormLayout(group_regional)
        
        self.widgets_configuracion['sistema_idioma'] = QComboBox()
        self.widgets_configuracion['sistema_idioma'].addItems(['es', 'en', 'pt'])
        self.widgets_configuracion['sistema_zona_horaria'] = QComboBox()
        self.widgets_configuracion['sistema_zona_horaria'].addItems(['America/Bogota', 'America/New_York', 'Europe/Madrid'])
        self.widgets_configuracion['sistema_formato_fecha'] = QComboBox()
        self.widgets_configuracion['sistema_formato_fecha'].addItems(['DD/MM/YYYY', 'MM/DD/YYYY', 'YYYY-MM-DD'])
        self.widgets_configuracion['sistema_formato_hora'] = QComboBox()
        self.widgets_configuracion['sistema_formato_hora'].addItems(['HH:mm:ss', 'HH:mm', 'hh:mm:ss AM/PM'])
        
        form_regional.addRow("Idioma:", self.widgets_configuracion['sistema_idioma'])
        form_regional.addRow("Zona Horaria:", self.widgets_configuracion['sistema_zona_horaria'])
        form_regional.addRow("Formato Fecha:", self.widgets_configuracion['sistema_formato_fecha'])
        form_regional.addRow("Formato Hora:", self.widgets_configuracion['sistema_formato_hora'])
        
        scroll_layout.addWidget(group_general)
        scroll_layout.addWidget(group_sesion)
        scroll_layout.addWidget(group_regional)
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        return widget
    
    def crear_tab_usuarios(self):
        """Crea la pestaña de configuración de usuarios."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Políticas de contraseña
        group_password = QGroupBox("Políticas de Contraseña")
        form_password = QFormLayout(group_password)
        
        self.widgets_configuracion['usuarios_password_min_length'] = QSpinBox()
        self.widgets_configuracion['usuarios_password_min_length'].setRange(4, 50)
        self.widgets_configuracion['usuarios_password_require_numbers'] = QCheckBox()
        self.widgets_configuracion['usuarios_password_require_symbols'] = QCheckBox()
        self.widgets_configuracion['usuarios_password_expire_days'] = QSpinBox()
        self.widgets_configuracion['usuarios_password_expire_days'].setRange(0, 365)
        self.widgets_configuracion['usuarios_password_expire_days'].setSuffix(" días")
        
        form_password.addRow("Long. Mínima:", self.widgets_configuracion['usuarios_password_min_length'])
        form_password.addRow("Requerir Números:", self.widgets_configuracion['usuarios_password_require_numbers'])
        form_password.addRow("Requerir Símbolos:", self.widgets_configuracion['usuarios_password_require_symbols'])
        form_password.addRow("Expirar en:", self.widgets_configuracion['usuarios_password_expire_days'])
        
        # Configuración de sesión
        group_session = QGroupBox("Configuración de Sesión")
        form_session = QFormLayout(group_session)
        
        self.widgets_configuracion['usuarios_session_timeout'] = QSpinBox()
        self.widgets_configuracion['usuarios_session_timeout'].setRange(300, 86400)
        self.widgets_configuracion['usuarios_session_timeout'].setSuffix(" seg")
        self.widgets_configuracion['usuarios_max_sessions'] = QSpinBox()
        self.widgets_configuracion['usuarios_max_sessions'].setRange(1, 10)
        
        form_session.addRow("Timeout Sesión:", self.widgets_configuracion['usuarios_session_timeout'])
        form_session.addRow("Máx. Sesiones:", self.widgets_configuracion['usuarios_max_sessions'])
        
        layout.addWidget(group_password)
        layout.addWidget(group_session)
        layout.addStretch()
        
        return widget
    
    def crear_tab_reportes(self):
        """Crea la pestaña de configuración de reportes."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Configuración de reportes
        group_reportes = QGroupBox("Configuración de Reportes")
        form_reportes = QFormLayout(group_reportes)
        
        self.widgets_configuracion['reportes_formato_default'] = QComboBox()
        self.widgets_configuracion['reportes_formato_default'].addItems(['PDF', 'Excel', 'Word'])
        self.widgets_configuracion['reportes_autor_default'] = QLineEdit()
        self.widgets_configuracion['reportes_logo_incluir'] = QCheckBox()
        self.widgets_configuracion['reportes_pie_pagina'] = QLineEdit()
        self.widgets_configuracion['reportes_max_registros'] = QSpinBox()
        self.widgets_configuracion['reportes_max_registros'].setRange(100, 1000000)
        
        form_reportes.addRow("Formato por Defecto:", self.widgets_configuracion['reportes_formato_default'])
        form_reportes.addRow("Autor por Defecto:", self.widgets_configuracion['reportes_autor_default'])
        form_reportes.addRow("Incluir Logo:", self.widgets_configuracion['reportes_logo_incluir'])
        form_reportes.addRow("Pie de Página:", self.widgets_configuracion['reportes_pie_pagina'])
        form_reportes.addRow("Máx. Registros:", self.widgets_configuracion['reportes_max_registros'])
        
        layout.addWidget(group_reportes)
        layout.addStretch()
        
        return widget
    
    def crear_tab_tema(self):
        """Crea la pestaña de configuración del tema."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Configuración de colores
        group_colores = QGroupBox("Configuración de Colores")
        form_colores = QFormLayout(group_colores)
        
        # Crear botones de color
        self.widgets_configuracion['tema_color_primario'] = self.crear_selector_color()
        self.widgets_configuracion['tema_color_secundario'] = self.crear_selector_color()
        self.widgets_configuracion['tema_color_exito'] = self.crear_selector_color()
        self.widgets_configuracion['tema_color_error'] = self.crear_selector_color()
        self.widgets_configuracion['tema_color_warning'] = self.crear_selector_color()
        
        form_colores.addRow("Color Primario:", self.widgets_configuracion['tema_color_primario'])
        form_colores.addRow("Color Secundario:", self.widgets_configuracion['tema_color_secundario'])
        form_colores.addRow("Color Éxito:", self.widgets_configuracion['tema_color_exito'])
        form_colores.addRow("Color Error:", self.widgets_configuracion['tema_color_error'])
        form_colores.addRow("Color Warning:", self.widgets_configuracion['tema_color_warning'])
        
        # Configuración de fuentes
        group_fuentes = QGroupBox("Configuración de Fuentes")
        form_fuentes = QFormLayout(group_fuentes)
        
        self.widgets_configuracion['tema_fuente_familia'] = QComboBox()
        self.widgets_configuracion['tema_fuente_familia'].addItems(['Segoe UI', 'Arial', 'Helvetica', 'Times New Roman'])
        self.widgets_configuracion['tema_fuente_tamaño'] = QSpinBox()
        self.widgets_configuracion['tema_fuente_tamaño'].setRange(8, 24)
        self.widgets_configuracion['tema_fuente_tamaño'].setSuffix(" px")
        self.widgets_configuracion['tema_modo_oscuro'] = QCheckBox()
        
        form_fuentes.addRow("Familia de Fuente:", self.widgets_configuracion['tema_fuente_familia'])
        form_fuentes.addRow("Tamaño de Fuente:", self.widgets_configuracion['tema_fuente_tamaño'])
        form_fuentes.addRow("Modo Oscuro:", self.widgets_configuracion['tema_modo_oscuro'])
        
        layout.addWidget(group_colores)
        layout.addWidget(group_fuentes)
        layout.addStretch()
        
        return widget
    
    def crear_tab_backup(self):
        """Crea la pestaña de configuración de backup."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Configuración de backup
        group_backup = QGroupBox("Configuración de Backup")
        form_backup = QFormLayout(group_backup)
        
        self.widgets_configuracion['backup_auto_habilitado'] = QCheckBox()
        self.widgets_configuracion['backup_intervalo_horas'] = QSpinBox()
        self.widgets_configuracion['backup_intervalo_horas'].setRange(1, 168)
        self.widgets_configuracion['backup_intervalo_horas'].setSuffix(" horas")
        self.widgets_configuracion['backup_directorio'] = QLineEdit()
        self.widgets_configuracion['backup_mantener_dias'] = QSpinBox()
        self.widgets_configuracion['backup_mantener_dias'].setRange(1, 365)
        self.widgets_configuracion['backup_mantener_dias'].setSuffix(" días")
        self.widgets_configuracion['backup_comprimir'] = QCheckBox()
        
        form_backup.addRow("Backup Automático:", self.widgets_configuracion['backup_auto_habilitado'])
        form_backup.addRow("Intervalo:", self.widgets_configuracion['backup_intervalo_horas'])
        form_backup.addRow("Directorio:", self.widgets_configuracion['backup_directorio'])
        form_backup.addRow("Mantener por:", self.widgets_configuracion['backup_mantener_dias'])
        form_backup.addRow("Comprimir:", self.widgets_configuracion['backup_comprimir'])
        
        layout.addWidget(group_backup)
        layout.addStretch()
        
        return widget
    
    def crear_tab_integraciones(self):
        """Crea la pestaña de configuración de integraciones."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Configuración de email
        group_email = QGroupBox("Configuración de Email")
        form_email = QFormLayout(group_email)
        
        self.widgets_configuracion['integraciones_email_smtp_server'] = QLineEdit()
        self.widgets_configuracion['integraciones_email_smtp_port'] = QSpinBox()
        self.widgets_configuracion['integraciones_email_smtp_port'].setRange(1, 65535)
        self.widgets_configuracion['integraciones_email_usuario'] = QLineEdit()
        self.widgets_configuracion['integraciones_email_ssl'] = QCheckBox()
        
        form_email.addRow("Servidor SMTP:", self.widgets_configuracion['integraciones_email_smtp_server'])
        form_email.addRow("Puerto SMTP:", self.widgets_configuracion['integraciones_email_smtp_port'])
        form_email.addRow("Usuario:", self.widgets_configuracion['integraciones_email_usuario'])
        form_email.addRow("Usar SSL:", self.widgets_configuracion['integraciones_email_ssl'])
        
        # Configuración de API
        group_api = QGroupBox("Configuración de API")
        form_api = QFormLayout(group_api)
        
        self.widgets_configuracion['integraciones_api_timeout'] = QSpinBox()
        self.widgets_configuracion['integraciones_api_timeout'].setRange(5, 300)
        self.widgets_configuracion['integraciones_api_timeout'].setSuffix(" seg")
        self.widgets_configuracion['integraciones_webhook_url'] = QLineEdit()
        
        form_api.addRow("Timeout API:", self.widgets_configuracion['integraciones_api_timeout'])
        form_api.addRow("Webhook URL:", self.widgets_configuracion['integraciones_webhook_url'])
        
        layout.addWidget(group_email)
        layout.addWidget(group_api)
        layout.addStretch()
        
        return widget
    
    def crear_tab_todas_configuraciones(self):
        """Crea la pestaña con todas las configuraciones."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Tabla de configuraciones
        self.tabla_configuraciones = QTableWidget()
        self.tabla_configuraciones.setColumnCount(5)
        self.tabla_configuraciones.setHorizontalHeaderLabels([
            "Clave", "Valor", "Descripción", "Categoría", "Acciones"
        ])
        
        # Configurar tabla
        header = self.tabla_configuraciones.horizontalHeader()
        header.setStretchLastSection(True)
        
        layout.addWidget(self.tabla_configuraciones)
        
        return widget
    
    def crear_panel_acciones(self):
        """Crea el panel de acciones."""
        panel = QFrame()
        layout = QHBoxLayout(panel)
        
        # Botones de acción
        btn_guardar = QPushButton("💾 Guardar Configuraciones")
        btn_guardar.clicked.connect(self.guardar_configuraciones)
        
        btn_restaurar = QPushButton("🔄 Restaurar Defecto")
        btn_restaurar.clicked.connect(self.restaurar_configuraciones)
        
        btn_exportar = QPushButton("📤 Exportar")
        btn_exportar.clicked.connect(self.solicitud_exportar_configuracion.emit)
        
        btn_importar = QPushButton("📥 Importar")
        btn_importar.clicked.connect(self.solicitud_importar_configuracion.emit)
        
        layout.addWidget(btn_guardar)
        layout.addWidget(btn_restaurar)
        layout.addWidget(btn_exportar)
        layout.addWidget(btn_importar)
        layout.addStretch()
        
        return panel
    
    def crear_selector_color(self):
        """Crea un selector de color."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        color_display = QLabel()
        color_display.setFixedSize(30, 20)
        color_display.setStyleSheet("border: 1px solid #ccc; background-color: #3498db;")
        
        btn_color = QPushButton("Seleccionar Color")
        btn_color.clicked.connect(lambda: self.seleccionar_color(color_display))
        
        layout.addWidget(color_display)
        layout.addWidget(btn_color)
        layout.addStretch()
        
        # Agregar referencia al display para poder acceder desde afuera
        widget.color_display = color_display
        
        return widget
    
    def seleccionar_color(self, display_widget):
        """Abre el selector de color."""
        color = QColorDialog.getColor()
        if color.isValid():
            display_widget.setStyleSheet(f"border: 1px solid #ccc; background-color: {color.name()};")
    
    def cargar_configuraciones(self, configuraciones: List[Dict[str, Any]]):
        """Carga las configuraciones en la interfaz."""
        self.configuraciones_data = configuraciones
        
        # Cargar en widgets específicos
        for config in configuraciones:
            clave = config['clave']
            valor = config['valor']
            
            if clave in self.widgets_configuracion:
                self.establecer_valor_widget(clave, valor)
        
        # Cargar en tabla
        self.cargar_tabla_configuraciones()
    
    def establecer_valor_widget(self, clave: str, valor: str):
        """Establece el valor en un widget específico."""
        widget = self.widgets_configuracion[clave]
        
        if isinstance(widget, QLineEdit):
            widget.setText(valor)
        elif isinstance(widget, QSpinBox):
            widget.setValue(int(valor) if valor.isdigit() else 0)
        elif isinstance(widget, QDoubleSpinBox):
            try:
                widget.setValue(float(valor))
            except ValueError:
                widget.setValue(0.0)
        elif isinstance(widget, QCheckBox):
            widget.setChecked(valor.lower() == 'true')
        elif isinstance(widget, QComboBox):
            index = widget.findText(valor)
            if index >= 0:
                widget.setCurrentIndex(index)
        elif hasattr(widget, 'color_display'):  # Selector de color
            widget.color_display.setStyleSheet(f"border: 1px solid #ccc; background-color: {valor};")
    
    def cargar_tabla_configuraciones(self):
        """Carga las configuraciones en la tabla."""
        self.tabla_configuraciones.setRowCount(len(self.configuraciones_data))
        
        for row, config in enumerate(self.configuraciones_data):
            # Clave
            self.tabla_configuraciones.setItem(row, 0, QTableWidgetItem(config['clave']))
            
            # Valor
            self.tabla_configuraciones.setItem(row, 1, QTableWidgetItem(str(config['valor'])))
            
            # Descripción
            self.tabla_configuraciones.setItem(row, 2, QTableWidgetItem(config.get('descripcion', '')))
            
            # Categoría
            self.tabla_configuraciones.setItem(row, 3, QTableWidgetItem(config.get('categoria', '')))
            
            # Botón de restaurar
            btn_restaurar = QPushButton("🔄 Restaurar")
            btn_restaurar.clicked.connect(
                lambda checked, c=config['clave']: self.solicitud_restaurar_configuracion.emit(c)
            )
            self.tabla_configuraciones.setCellWidget(row, 4, btn_restaurar)
    
    def guardar_configuraciones(self):
        """Guarda todas las configuraciones."""
        for clave, widget in self.widgets_configuracion.items():
            valor = self.obtener_valor_widget(widget)
            if valor is not None:
                self.solicitud_actualizar_configuracion.emit(clave, valor)
    
    def obtener_valor_widget(self, widget):
        """Obtiene el valor de un widget."""
        if isinstance(widget, QLineEdit):
            return widget.text()
        elif isinstance(widget, QSpinBox):
            return widget.value()
        elif isinstance(widget, QDoubleSpinBox):
            return widget.value()
        elif isinstance(widget, QCheckBox):
            return widget.isChecked()
        elif isinstance(widget, QComboBox):
            return widget.currentText()
        elif hasattr(widget, 'color_display'):  # Selector de color
            style = widget.color_display.styleSheet()
            # Extraer el color del estilo
            if 'background-color:' in style:
                return style.split('background-color:')[1].split(';')[0].strip()
        return None
    
    def restaurar_configuraciones(self):
        """Restaura las configuraciones seleccionadas."""
        # Por ahora, mostrar mensaje
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Restaurar", "Seleccione configuraciones específicas en la tabla para restaurar.")
    
    def aplicar_cambio_tema(self, clave: str, valor: Any):
        """Aplica un cambio de tema."""
        if clave.startswith('tema_color_'):
            # Aplicar cambio de color
            self.aplicar_estilos()
    
    def aplicar_estilos(self):
        """Aplica estilos modernos al widget."""
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                border-radius: 8px;
                background-color: white;
                padding: 10px;
            }
            
            QTabBar::tab {
                background: linear-gradient(135deg, #ecf0f1, #d5dbdb);
                border: 1px solid #bdc3c7;
                border-bottom: none;
                padding: 12px 24px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
                color: #2c3e50;
            }
            
            QTabBar::tab:selected {
                background: linear-gradient(135deg, #3498db, #2980b9);
                color: white;
                border-bottom: 2px solid #3498db;
            }
            
            QTabBar::tab:hover {
                background: linear-gradient(135deg, #d5dbdb, #bdc3c7);
            }
            
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #2c3e50;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: #f8f9fa;
            }
            
            QLabel {
                color: #2c3e50;
                font-weight: 500;
            }
            
            QLineEdit {
                padding: 8px 12px;
                border: 2px solid #e9ecef;
                border-radius: 6px;
                font-size: 14px;
                background-color: white;
            }
            
            QLineEdit:focus {
                border-color: #3498db;
                outline: none;
            }
            
            QPushButton {
                background: linear-gradient(135deg, #3498db, #2980b9);
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
                min-width: 100px;
            }
            
            QPushButton:hover {
                background: linear-gradient(135deg, #2980b9, #1f618d);
            }
            
            QPushButton:pressed {
                background: linear-gradient(135deg, #1f618d, #154360);
            }
            
            QComboBox {
                padding: 8px 12px;
                border: 2px solid #e9ecef;
                border-radius: 6px;
                background-color: white;
                min-width: 100px;
            }
            
            QComboBox:focus {
                border-color: #3498db;
            }
            
            QSpinBox, QDoubleSpinBox {
                padding: 8px 12px;
                border: 2px solid #e9ecef;
                border-radius: 6px;
                background-color: white;
            }
            
            QSpinBox:focus, QDoubleSpinBox:focus {
                border-color: #3498db;
            }
            
            QCheckBox {
                spacing: 8px;
                font-size: 13px;
            }
            
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #bdc3c7;
                border-radius: 3px;
                background-color: white;
            }
            
            QCheckBox::indicator:checked {
                background-color: #3498db;
                border-color: #3498db;
            }
            
            QTableWidget {
                background-color: white;
                alternate-background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                gridline-color: #e9ecef;
            }
            
            QTableWidget::item {
                padding: 8px;
                border: none;
            }
            
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            
            QHeaderView::section {
                background: linear-gradient(135deg, #34495e, #2c3e50);
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
    
    def set_controller(self, controller):
        """Establece el controlador para la vista."""
        self.controller = controller
