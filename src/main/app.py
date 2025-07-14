# --- PRINCIPIOS Y PARÁMETROS DE DISEÑO UI/UX PARA TODA LA APP ---
# Estos lineamientos deben aplicarse SIEMPRE al crear cualquier ventana, diálogo, botón, label, input, tabla, etc.
# Si se requiere una excepción, debe justificarse y documentarse.
## IMPORTS ÚNICOS AL INICIO DEL ARCHIVO (PEP8)
#        widget.setGraphicsEffect(sombra)
#    - Documentar cualquier excepción visual en docs/estandares_visuales.md
#    - Bordes redondeados en headers y celdas: 8px.
#    - No saturar de información, usar scroll y paginación si es necesario.
# 8. Feedback visual:
#    - Mensajes breves, claros y con color adecuado.
#    - Siempre usar QMessageBox o widgets personalizados con los estilos definidos.
#    - El feedback debe ser inmediato tras la acción del usuario.
# 9. Accesibilidad:
#    - Contraste alto entre texto y fondo.
#    - No usar solo color para indicar estado (agregar íconos o texto).
#    - Tamaños de fuente nunca menores a 10px.
# 10. Código:
#     - Centralizar estilos en QSS global o helpers.
#     - No hardcodear estilos en cada widget, salvo casos justificados.
#     - Reutilizar componentes visuales y helpers para mantener coherencia.
#     - Documentar cualquier excepción a estas reglas.
# --- FIN DE PRINCIPIOS DE DISEÑO ---
import os
import platform
import subprocess
import sys
import traceback
import warnings
from functools import partial

import pkg_resources

# from components.sidebar_button import SidebarButton  # Módulo no disponible
from PyQt6.QtCore import QEvent, QSize, Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QIcon, QPalette, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from src.core.config import DEFAULT_THEME
from src.core.database import DatabaseConnection, InventarioDatabaseConnection
from src.core.login_dialog import LoginDialog
from src.core.security import SecurityManager, initialize_security_manager
from src.core.splash_screen import SplashScreen

# from src.core.startup_update_checker import check_and_update_critical_packages  # Módulo no disponible
from src.modules.auditoria.controller import AuditoriaController
from src.modules.auditoria.model import AuditoriaModel
from src.modules.auditoria.view import AuditoriaView
from src.modules.compras.pedidos.controller import ComprasPedidosController
from src.modules.compras.pedidos.model import PedidosModel as ComprasPedidosModel
from src.modules.compras.pedidos.view import PedidosView as ComprasPedidosView
from src.modules.configuracion.controller import ConfiguracionController
from src.modules.configuracion.model import ConfiguracionModel
from src.modules.configuracion.view import ConfiguracionView
from src.modules.contabilidad.view import ContabilidadView
from src.modules.herrajes.controller import HerrajesController
from src.modules.herrajes.model import HerrajesModel
from src.modules.herrajes.view import HerrajesView
from src.modules.inventario.controller import InventarioController

# Importar modelos, vistas y controladores principales
from src.modules.inventario.model import InventarioModel
from src.modules.inventario.view import InventarioView
from src.modules.logistica.controller import LogisticaController
from src.modules.logistica.model import LogisticaModel
from src.modules.logistica.view import LogisticaView
from src.modules.mantenimiento.view import MantenimientoView
from src.modules.obras.controller import ObrasController
from src.modules.obras.model import ObrasModel
from src.modules.obras.produccion.controller import ProduccionController
from src.modules.obras.produccion.model import ProduccionModel
from src.modules.obras.produccion.view import ProduccionView
from src.modules.obras.view import ObrasView
from src.modules.pedidos.controller import PedidosController
from src.modules.pedidos.model import PedidosModel
from src.modules.pedidos.view import PedidosView as PedidosIndependienteView
from src.modules.usuarios.controller import UsuariosController
from src.modules.usuarios.model import UsuariosModel
from src.modules.usuarios.view import UsuariosView
from src.utils.icon_loader import get_icon
from src.utils.theme_manager import aplicar_tema, cargar_modo_tema, set_theme

# --- FIN IMPORTS PRINCIPALES ---

warnings.filterwarnings("ignore", category=DeprecationWarning)


# --- INSTALACIÓN AUTOMÁTICA DE DEPENDENCIAS CRÍTICAS (WHEELS) PARA TODA LA APP ---
def instalar_dependencias_criticas():
    from urllib.parse import urlparse

    print("[LOG 1.1] === INICIO DE CHEQUEO DE DEPENDENCIAS CRÍTICAS ===")
    py_version = (
        f"{sys.version_info.major}{sys.version_info.minor}"  # Ej: 311 para Python 3.11
    )
    arch = platform.architecture()[0]
    py_tag = f"cp{py_version}"
    win_tag = "win_amd64" if arch == "64bit" else "win32"
    wheels = {
        "pandas": f"pandas-2.2.2-{py_tag}-{py_tag}-{win_tag}.whl",
        "pyodbc": f"pyodbc-5.0.1-{py_tag}-{py_tag}-{win_tag}.whl",
    }
    url_base = "https://download.lfd.uci.edu/pythonlibs/archive/"

    def instalar_wheel(paquete, wheel_file):
        url = url_base + wheel_file
        local_path = os.path.join(os.getcwd(), wheel_file)
        try:
            # ...lógica de descarga y validación...
            pass  # Aquí va el código real de la función
        except Exception as e:
            print(f"[LOG 1.1.3] [ERROR] Error instalando {paquete} desde wheel: {e}")
            return False

    def instalar_dependencia(paquete, version):
        try:
            print(f"[LOG 1.2.1] Instalando {paquete}=={version} con pip...")
            # Validar que el paquete y versión sean strings seguros
            if not isinstance(paquete, str) or not isinstance(version, str):
                raise ValueError("Paquete y versión deben ser cadenas de texto")
            if not paquete.isidentifier():
                raise ValueError("Nombre de paquete no válido")
            if not version.replace(".", "").isdigit():
                raise ValueError("Versión no válida")
            # Validar argumentos antes de ejecutar subprocess
            cmd = [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--user",
def main():
    print("[LOG 4.1] Iniciando QApplication...")
    app = QApplication(sys.argv)
    print("[LOG 4.2] Mostrando login profesional...")

    # Inicializar sistema de seguridad
    security_manager = initialize_security_manager()

    # Crear dialog de login moderno
    login_dialog = LoginDialog()

    def cargar_main_window_con_seguridad(user_data, modulos_permitidos):
        global main_window
        try:
            print(f"🏗️ [SEGURIDAD] Creando MainWindow para usuario: {user_data['username']}")
            main_window = MainWindow(user_data, modulos_permitidos)
            main_window.actualizar_usuario_label(user_data)
            # Inicializar el atributo si no existe
            if not hasattr(main_window, 'security_manager'):
                main_window.security_manager = None
            main_window.security_manager = security_manager
            main_window.mostrar_mensaje(
                f"¡Bienvenido {user_data['username']}! ({user_data['rol']})",
                tipo="exito",
                duracion=3000,
            )
            main_window.show()
            print(f"✅ [SEGURIDAD] Aplicación iniciada para {user_data['username']}")
        except Exception as e:
            import traceback
            error_msg = f"[ERROR SEGURIDAD] {e}\n{traceback.format_exc()}"
            print(f"❌ [ERROR] {error_msg}", flush=True)
            os.makedirs("logs", exist_ok=True)
            with open("logs/error_inicio_seguridad.txt", "a", encoding="utf-8") as f:
                f.write(error_msg + "\n")
            QMessageBox.critical(
                None,
                "Error crítico",
                f"Error al iniciar la aplicación con seguridad: {e}",
            )
            app.quit()

    def on_login_success(username, role):
        print(f"✅ [LOGIN] Autenticación exitosa para {username} ({role})")
        user_data = security_manager.get_current_user()
        if not user_data:
            print("❌ [LOGIN] Error: No se pudo obtener datos del usuario")
            return
        modulos_permitidos = security_manager.get_user_modules(user_data["id"])
        cargar_main_window_con_seguridad(user_data, modulos_permitidos)

    def on_login_failed(error_message):
        print(f"❌ [LOGIN] Autenticación fallida: {error_message}")
        # El dialog ya muestra el mensaje de error

    login_dialog.login_successful.connect(on_login_success)
    login_dialog.login_failed.connect(on_login_failed)

    # Mostrar login directamente
    login_dialog.show()
    print("[LOG 4.10] QApplication loop iniciado.")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
                    print(f"[LOG 1.4.2] Chequeando {pkg}...")
                    pkg_resources.require(line.strip())
                    print(f"[LOG 1.4.3] [OK] {pkg} ya está instalado.")
                except Exception:
                    print(
                        f"[LOG 1.4.4] [ERROR] {pkg} no está instalado o la versión es incorrecta. Instalando..."
                    )
                    # Validar argumentos antes de ejecutar subprocess
                    cmd = [
                        sys.executable,
                        "-m",
                        "pip",
                        "install",
                        "--user",
                        line.strip(),
                    ]
                    if not all(isinstance(arg, str) and arg for arg in cmd):
                        print(
                            f"[LOG 1.4.4] [ERROR] Argumentos de subprocess no válidos: {cmd}"
                        )
                        continue
                    subprocess.check_call(cmd)
        os.remove(req_tmp_path)
        print("[LOG 1.4.5] [OK] Todas las dependencias instaladas correctamente.")
    except Exception as e:
        print(f"[LOG 1.4.6] [ERROR] Error instalando requirements.txt: {e}")
        print("Por favor, revisa los logs y ejecuta manualmente si es necesario.")
    print("[LOG 1.5] === FIN DE CHEQUEO DE DEPENDENCIAS CRÍTICAS ===")


# Ejecutar instalación automática antes de cualquier importación pesada o arranque de la app
def _verificar_e_instalar_dependencias():
    try:
        import pandas
        import pyodbc
    except ImportError:
        print("Instalando dependencias críticas automáticamente...")
        instalar_dependencias_criticas()


_verificar_e_instalar_dependencias()


def mostrar_mensaje_dependencias(titulo, texto, detalles, tipo="error"):
    # Todos los imports de PyQt6 ya están al inicio del archivo

    app = QApplication.instance() or QApplication(sys.argv)
    dialog = QDialog()
    dialog.setWindowTitle(titulo)
    dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
    dialog.setFixedWidth(420)
    dialog.setStyleSheet(
        f"""
        QDialog {{
            background: #fff9f3;
            border-radius: 18px;
            border: 2px solid #e3e3e3;
        }}
        QLabel#titulo {{
            color: #2563eb;
            font-size: 18px;
            font-weight: bold;
            padding: 12px 0 0 0;
            qproperty-alignment: AlignCenter;
        }}
        QLabel#mensaje {{
            color: #1e293b;
            font-size: 14px;
            font-weight: 500;
            padding: 8px 0 0 0;
            qproperty-alignment: AlignCenter;
        }}
        QLabel#detalles {{
            color: {"#ef4444" if tipo == "error" else "#fbbf24"};
            font-size: 13px;
            font-weight: 500;
            background: {"#ffe5e5" if tipo == "error" else "#fef9c3"};
            border-radius: 10px;
            padding: 10px 16px;
            margin: 12px 0 0 0;
            qproperty-alignment: AlignCenter;
        }}
        QPushButton {{
            background: #2563eb;
            color: white;
            border-radius: 8px;
            font-size: 14px;
            font-weight: bold;
            min-width: 100px;
            min-height: 32px;
            padding: 8px 24px;
            margin-top: 18px;
        }}
        QPushButton:hover {{
            background: #1e40af;
        }}
    """
    )
    layout = QVBoxLayout()
    # Ícono grande
    icon_label = QLabel()
    if tipo == "error":
        icon_label.setPixmap(
            QPixmap("img/reject.svg").scaled(
                48,
                48,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
    else:
        icon_label.setPixmap(
            QPixmap("img/warning.svg").scaled(
                48,
                48,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
    icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(icon_label)
    # Título
    titulo_label = QLabel(titulo)
    titulo_label.setObjectName("titulo")
    layout.addWidget(titulo_label)
    # Mensaje principal
    mensaje_label = QLabel(texto)
    mensaje_label.setObjectName("mensaje")
    mensaje_label.setWordWrap(True)
    layout.addWidget(mensaje_label)
    # Detalles (lista de dependencias)
    detalles_label = QLabel(detalles)
    detalles_label.setObjectName("detalles")
    detalles_label.setWordWrap(True)
    layout.addWidget(detalles_label)
    # Botón de cierre
    btn = QPushButton("Cerrar")
    btn.clicked.connect(dialog.accept)
    layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
    dialog.setLayout(layout)
    dialog.exec()


def verificar_dependencias():
    """
    Verifica si las dependencias críticas y secundarias están instaladas.
    Si falta una CRÍTICA (PyQt6, pandas, pyodbc), muestra un error y cierra.
    Si faltan secundarias, muestra advertencia visual pero permite iniciar la app.
    Ahora acepta versiones IGUALES O SUPERIORES a las requeridas.
    """
    import pkg_resources

    # Todos los imports de PyQt6 ya están al inicio del archivo

    requeridos_criticos = [("PyQt6", "6.9.0"), ("pandas", "2.2.2"), ("pyodbc", "5.0.1")]
    requeridos_secundarios = [
        ("reportlab", "4.4.0"),
        ("qrcode", "7.4.2"),
        ("matplotlib", "3.8.4"),
        ("pytest", "8.2.0"),
        ("pillow", "10.3.0"),
        ("python-dateutil", "2.9.0"),
        ("pytz", "2024.1"),
        ("tzdata", "2024.1"),
        ("openpyxl", "3.1.2"),
        ("colorama", "0.4.6"),
        ("ttkthemes", "3.2.2"),
        ("fpdf", None),
    ]
    faltantes_criticos = []
    faltantes_secundarios = []
    print("[LOG 2.1] Chequeando dependencias críticas...", flush=True)
    for paquete, version in requeridos_criticos:
        try:
            if version:
                pkg_resources.require(f"{paquete}>={version}")
            else:
                __import__(paquete)
            print(
                f"[LOG 2.1.1] [OK] {paquete} presente y versión >= {version if version else ''}.",
                flush=True,
            )
        except Exception:
            print(
                f"[LOG 2.1.2] [ERROR] {paquete} faltante o versión menor a la requerida.",
                flush=True,
            )
            faltantes_criticos.append(f"{paquete}{' >= ' + version if version else ''}")
    print("[LOG 2.2] Chequeando dependencias secundarias...", flush=True)
    for paquete, version in requeridos_secundarios:
        try:
            if version:
                pkg_resources.require(f"{paquete}>={version}")
            else:
                __import__(paquete)
            print(f"[LOG 2.2.1] [OK] {paquete} presente.", flush=True)
        except Exception:
            print(f"[LOG 2.2.2] [ERROR] {paquete} faltante.", flush=True)
            faltantes_secundarios.append(
                f"{paquete}{' >= ' + version if version else ''}"
            )
    if faltantes_criticos:
        print(
            "[LOG 2.3] Dependencias críticas faltantes. Mostrando mensaje y abortando.",
            flush=True,
        )
        mostrar_mensaje_dependencias(
            "Faltan dependencias críticas",
            "No se puede iniciar la aplicación. Instala las siguientes dependencias críticas:",
            "\n".join(faltantes_criticos),
            tipo="error",
        )
        sys.exit(1)
    elif faltantes_secundarios:
        print(
            "[LOG 2.4] Dependencias secundarias faltantes. Mostrando advertencia.",
            flush=True,
        )
        mostrar_mensaje_dependencias(
            "Dependencias opcionales faltantes",
            "La aplicación se iniciará, pero faltan dependencias secundarias. Algunas funciones pueden estar limitadas (exportar PDF, QR, gráficos, etc.):",
            "\n".join(faltantes_secundarios),
            tipo="warning",
        )
    else:
        print(
            "[LOG 2.5] [OK] Todas las dependencias críticas y secundarias están instaladas correctamente.",
            flush=True,
        )


# os ya importado anteriormente
# Refuerzo para evitar errores de OpenGL/Skia/Chromium en Windows
os.environ["QT_OPENGL"] = "software"
os.environ["QT_QUICK_BACKEND"] = "software"
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --disable-software-rasterizer"


# --- CLASE LOGGER MÍNIMA PARA LOGGING ROBUSTO ---
import logging


class Logger:
    def __init__(self):
        self.logger = logging.getLogger("stock.app")
        if not self.logger.hasHandlers():
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(levelname)s] %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)


# --- DEFINICIÓN DE MODELOS OPCIONALES COMO NONE SI NO EXISTEN ---
try:
    from src.modules.mantenimiento.model import MantenimientoModel
except ImportError:
    MantenimientoModel = None
try:
    from src.modules.contabilidad.model import ContabilidadModel
except ImportError:
    ContabilidadModel = None
try:
    from src.modules.vidrios.model import VidriosModel
except ImportError:
    VidriosModel = None


# --- FUNCIONES DE VALIDACIÓN ROBUSTA ---
def validar_usuario_robusto(usuario_data):
    """Validación robusta de datos de usuario."""
    if not usuario_data:
        return False, "Usuario no puede ser None"

    if not isinstance(usuario_data, dict):
        return False, "Usuario debe ser un diccionario"

    if "usuario" not in usuario_data:
        return False, "Falta campo 'usuario'"

    if not usuario_data["usuario"].strip():
        return False, "Campo 'usuario' no puede estar vacío"

    # Rol opcional, pero si existe debe ser válido
    if "rol" in usuario_data:
        roles_validos = ["admin", "TEST_USER", "supervisor", "usuario"]
        if usuario_data["rol"] not in roles_validos:
            return False, f"Rol inválido. Debe ser uno de: {roles_validos}"

    return True, "Usuario válido"


def validar_modulos_permitidos_robusto(modulos):
    """Validación robusta de módulos permitidos con fallback."""
    modulos_disponibles = [
        "Obras",
        "Inventario",
        "Herrajes",
        "Compras / Pedidos",
        "Logística",
        "Vidrios",
        "Mantenimiento",
        "Producción",
        "Contabilidad",
        "Auditoría",
        "Usuarios",
        "Configuración",
    ]

    if modulos is None:
        return ["Configuración"]  # Fallback por defecto

    if not isinstance(modulos, list):
        return ["Configuración"]  # Fallback por defecto

    # Filtrar módulos válidos
    modulos_validos = [m for m in modulos if m in modulos_disponibles]

    if not modulos_validos:
        return ["Configuración"]  # Fallback si no hay módulos válidos

    return modulos_validos


# --- FIN FUNCIONES DE VALIDACIÓN ROBUSTA ---


try:
    from components.modern_header import ModernHeader

    print("[OK] ModernHeader importado correctamente")
except ImportError as e:
    print(f"Warning: Error importando ModernHeader: {e}")
    ModernHeader = None

# Configurar Sidebar con manejo robusto
SidebarClass = None


# Usar FallbackSidebar por defecto para evitar problemas de compatibilidad
class FallbackSidebar(QWidget):
    pageChanged = pyqtSignal(int)

    def __init__(self, sections=None, mostrar_nombres=True):
        super().__init__()
        self.sections = sections or []
        self.setLayout(QVBoxLayout())
        print("Warning: Usando Sidebar básico como fallback")

    def set_sections(self, sections):
        self.sections = sections

    def set_expanded(self, expanded):
        pass


SidebarClass = FallbackSidebar


# Clase principal
class MainWindow(QMainWindow):
    def __init__(self, usuario, modulos_permitidos):
        super().__init__()
        from PyQt6.QtWidgets import QStatusBar

        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self.logger = Logger()
        self.logger.info("Aplicación iniciada")
        self.setWindowTitle("MPS Inventario App")
        self.resize(1280, 720)
        self.setMinimumSize(1024, 600)
        self.usuario_actual = usuario
        self.modulos_permitidos = modulos_permitidos
        self.security_manager = None  # Se asignará después
        self.usuario_label = QLabel()
        self.usuario_label.setObjectName("usuarioActualLabel")
        self.usuario_label.setStyleSheet("")
        self.usuario_label.setText("")
        self._status_bar.addPermanentWidget(self.usuario_label, 1)
        self.initUI(usuario, modulos_permitidos)

    def mostrar_mensaje(self, mensaje, tipo="info", duracion=4000):
        colores = {
            "info": "#2563eb",
            "exito": "#22c55e",
            "advertencia": "#fbbf24",
            "error": "#ef4444",
        }
        color = colores.get(tipo, "#2563eb")
        self._status_bar.setStyleSheet(
            f"background: #f1f5f9; color: {color}; font-weight: bold; font-size: 13px; border-radius: 8px; padding: 4px 12px;"
        )
        self._status_bar.showMessage(mensaje, duracion)
        if tipo == "error":
            QMessageBox.critical(self, "Error", mensaje)
        elif tipo == "advertencia":
            QMessageBox.warning(self, "Advertencia", mensaje)
        elif tipo == "exito":
            QMessageBox.information(self, "Éxito", mensaje)

    def actualizar_usuario_label(self, usuario):
        """Actualizar label de usuario con estilo profesional"""
        if not usuario or not isinstance(usuario, dict):
            self.usuario_label.setText("Usuario: Desconocido")
            self.usuario_label.setObjectName("usuarioActualLabel")
            return

        rol = usuario.get("rol", "").lower()
        nombre_usuario = usuario.get("usuario", "Usuario")

        # Colores profesionales según rol
        colores_rol = {
            "TEST_USER": {"bg": "#e0e7ff", "text": "#1e40af", "border": "#c7d2fe"},
            "supervisor": {"bg": "#fef3c7", "text": "#d97706", "border": "#fde68a"},
            "usuario": {"bg": "#d1fae5", "text": "#065f46", "border": "#a7f3d0"},
        }

        estilo_rol = colores_rol.get(rol, colores_rol["usuario"])

        # Aplicar estilo profesional consistente con el QSS global
        self.usuario_label.setObjectName("usuarioActualLabel")
        self.usuario_label.setStyleSheet(
            f"""
            QLabel#usuarioActualLabel {{
                background: {estilo_rol["bg"]};
                color: {estilo_rol["text"]};
                font-size: 13px;
                font-weight: 600;
                font-family: "Segoe UI", sans-serif;
                border-radius: 12px;
                padding: 6px 12px;
                margin-right: 8px;
                border: 1px solid {estilo_rol["border"]};
            }}
        """
        )
        self.usuario_label.setText(f"[USER] {nombre_usuario} • {rol.title()}")

    def initUI(self, usuario=None, modulos_permitidos=None):
        # Crear conexiones persistentes a las bases de datos (una sola instancia por base)
        self.db_connection_inventario = DatabaseConnection()
        self.db_connection_inventario.conectar_a_base("inventario")
        self.db_connection_usuarios = DatabaseConnection()
        self.db_connection_usuarios.conectar_a_base("users")
        self.db_connection_auditoria = DatabaseConnection()
        self.db_connection_auditoria.conectar_a_base("auditoria")
        self.db_connection_pedidos = self.db_connection_inventario
        self.db_connection_configuracion = self.db_connection_inventario
        self.db_connection_produccion = self.db_connection_inventario

        # Crear instancias de modelos
        self.inventario_model = InventarioModel(
            db_connection=self.db_connection_inventario
        )
        self.inventario_model.actualizar_qr_y_campos_por_descripcion()
        self.obras_model = ObrasModel(db_connection=self.db_connection_inventario)
        self.produccion_model = ProduccionModel(
            db_connection=self.db_connection_produccion
        )
        self.logistica_model = LogisticaModel(
            db_connection=self.db_connection_inventario
        )
        self.pedidos_model = PedidosModel(db_connection=self.db_connection_pedidos)
        self.configuracion_model = ConfiguracionModel(
            db_connection=self.db_connection_configuracion
        )
        self.herrajes_model = HerrajesModel(self.db_connection_inventario)
        self.usuarios_model = UsuariosModel(db_connection=self.db_connection_usuarios)
        self.usuarios_model.crear_usuarios_iniciales()

        # Crear vistas y controladores principales
        usuario_str = (
            usuario.get("usuario", "usuario_default")
            if isinstance(usuario, dict)
            else str(usuario)
            if usuario
            else "usuario_default"
        )
        self.inventario_view = InventarioView(
            db_connection=self.db_connection_inventario, usuario_actual=usuario_str
        )
        self.inventario_controller = InventarioController(
            model=self.inventario_model,
            view=self.inventario_view,
            db_connection=self.db_connection_inventario,
        )
        self.obras_view = ObrasView()
        self.obras_controller = ObrasController(
            model=self.obras_model,
            view=self.obras_view,
            db_connection=self.db_connection_inventario,
            usuarios_model=self.usuarios_model,
            logistica_controller=None,
        )
        self.produccion_view = ProduccionView()
        self.produccion_controller = ProduccionController(
            model=self.produccion_model,
            view=self.produccion_view,
            db_connection=self.db_connection_produccion,
        )
        self.logistica_view = LogisticaView()
        self.logistica_controller = LogisticaController(
            model=self.logistica_model,
            view=self.logistica_view,
            db_connection=self.db_connection_inventario,
            usuarios_model=self.usuarios_model,
        )
        self.obras_controller.logistica_controller = self.logistica_controller
        self.compras_pedidos_view = ComprasPedidosView()
        self.compras_pedidos_controller = ComprasPedidosController(
            self.pedidos_model,
            self.compras_pedidos_view,
            self.db_connection_pedidos,
            self.usuarios_model,
        )
        self.compras_pedidos_controller.cargar_pedidos()
        self.pedidos_view = PedidosIndependienteView()
        self.pedidos_controller = PedidosController(
            self.pedidos_view, self.db_connection_pedidos
        )
        self.usuarios_controller = UsuariosController(
            model=self.usuarios_model,
            view=None,
            db_connection=self.db_connection_usuarios,
        )
        self.usuarios_view = UsuariosView()
        self.usuarios_controller.view = self.usuarios_view
        self.auditoria_view = AuditoriaView()
        self.auditoria_model = AuditoriaModel(
            db_connection=self.db_connection_auditoria
        )
        self.auditoria_controller = AuditoriaController(
            model=self.auditoria_model,
            view=self.auditoria_view,
            db_connection=self.db_connection_auditoria,
        )
        self.configuracion_view = ConfiguracionView()
        self.configuracion_controller = ConfiguracionController(
            model=self.configuracion_model,
            view=self.configuracion_view,
            db_connection=self.db_connection_configuracion,
            usuarios_model=self.usuarios_model,
        )
        # Crear vistas con fallback robusto
        self.mantenimiento_view = MantenimientoView()
        self.contabilidad_view = ContabilidadView()
        self.herrajes_view = HerrajesView()

        try:
            from src.modules.vidrios.view import VidriosView

            self.vidrios_view = VidriosView()
        except ImportError as e:
            print(f"Warning: VidriosView no disponible: {e}")
            # Usar QWidget importado globalmente
            self.vidrios_view = QWidget()

        # Crear controladores con fallback robusto
        try:
            from src.modules.mantenimiento.controller import MantenimientoController

            if MantenimientoModel:
                mantenimiento_model = MantenimientoModel(
                    db_connection=self.db_connection_inventario
                )
            else:
                mantenimiento_model = None
            self.mantenimiento_controller = MantenimientoController(
                model=mantenimiento_model,
                view=self.mantenimiento_view,
                db_connection=self.db_connection_inventario,
                usuarios_model=self.usuarios_model,
            )
        except ImportError as e:
            print(f"Warning: MantenimientoController no disponible: {e}")
            self.mantenimiento_controller = None

        try:
            from src.modules.contabilidad.controller import ContabilidadController

            if ContabilidadModel:
                contabilidad_model = ContabilidadModel(
                    db_connection=self.db_connection_inventario
                )
            else:
                contabilidad_model = None
            self.contabilidad_controller = ContabilidadController(
                model=contabilidad_model,
                view=self.contabilidad_view,
                db_connection=self.db_connection_inventario,
                usuarios_model=self.usuarios_model,
            )
        except ImportError as e:
            print(f"Warning: ContabilidadController no disponible: {e}")
            self.contabilidad_controller = None

        self.herrajes_controller = HerrajesController(
            self.herrajes_model,
            self.herrajes_view,
            db_connection=self.db_connection_inventario,
            usuarios_model=self.usuarios_model,
        )

        try:
            from src.modules.vidrios.controller import VidriosController

            if VidriosModel:
                vidrios_model = VidriosModel(
                    db_connection=self.db_connection_inventario
                )
            else:
                vidrios_model = None
            self.vidrios_controller = VidriosController(
                model=vidrios_model,
                view=self.vidrios_view,
                db_connection=self.db_connection_inventario,
            )
        except ImportError as e:
            print(f"Warning: VidriosController no disponible: {e}")
            self.vidrios_controller = None

        # Layout principal mejorado con header
        # Widget central principal
        central_widget = QWidget()
        central_widget.setStyleSheet(
            """
            QWidget {
                background: #f8fafc;
            }
        """
        )
        self.setCentralWidget(central_widget)

        # Layout vertical principal para incluir header + contenido
        main_vertical_layout = QVBoxLayout(central_widget)
        main_vertical_layout.setContentsMargins(0, 0, 0, 0)
        main_vertical_layout.setSpacing(0)

        # Crear header moderno
        if ModernHeader:
            self.header = ModernHeader(usuario)
            self.header.search_requested.connect(self.on_global_search)
            self.header.notifications_clicked.connect(self.on_notifications_clicked)
            self.header.profile_clicked.connect(self.on_profile_clicked)
            self.header.theme_toggled.connect(self.on_theme_toggle)
            main_vertical_layout.addWidget(self.header)
            print("[OK] Header moderno agregado")
        else:
            print("[WARN] Header moderno no disponible, continuando sin header")

        # Layout horizontal para sidebar + contenido
        main_horizontal_layout = QHBoxLayout()
        main_horizontal_layout.setContentsMargins(0, 0, 0, 0)
        main_horizontal_layout.setSpacing(0)

        # Crear un contenedor para el área de contenido con márgenes y sombra
        content_container = QWidget()
        content_container.setStyleSheet(
            """
            QWidget {
                background: white;
                border-radius: 12px;
                margin: 8px 8px 8px 0px;
            }
        """
        )
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(0)

        self.module_stack = QStackedWidget()
        self.module_stack.setStyleSheet(
            """
            QStackedWidget {
                background: white;
                border: none;
                border-radius: 12px;
            }
        """
        )
        self.module_stack.addWidget(self.obras_view)
        self.module_stack.addWidget(self.inventario_view)
        self.module_stack.addWidget(self.herrajes_view)
        self.module_stack.addWidget(self.compras_pedidos_view)
        self.module_stack.addWidget(self.logistica_view)
        self.module_stack.addWidget(self.vidrios_view)
        self.module_stack.addWidget(self.mantenimiento_view)
        self.module_stack.addWidget(self.produccion_view)
        self.module_stack.addWidget(self.contabilidad_view)
        self.module_stack.addWidget(self.auditoria_view)
        self.module_stack.addWidget(self.usuarios_view)
        self.module_stack.addWidget(self.configuracion_view)

        content_layout.addWidget(self.module_stack)

        # Configurar iconos SVG mejorados
        svg_dir = os.path.join(os.path.dirname(__file__), "resources", "icons")
        sidebar_sections = [
            ("Obras", os.path.join(svg_dir, "obras.svg")),
            ("Inventario", os.path.join(svg_dir, "inventario.svg")),
            ("Herrajes", os.path.join(svg_dir, "herrajes.svg")),
            ("Compras / Pedidos", os.path.join(svg_dir, "compras.svg")),
            ("Logística", os.path.join(svg_dir, "logistica.svg")),
            ("Vidrios", os.path.join(svg_dir, "vidrios.svg")),
            ("Mantenimiento", os.path.join(svg_dir, "mantenimiento.svg")),
            ("Producción", os.path.join(svg_dir, "produccion.svg")),
            ("Contabilidad", os.path.join(svg_dir, "contabilidad.svg")),
            ("Auditoría", os.path.join(svg_dir, "auditoria.svg")),
            ("Usuarios", os.path.join(svg_dir, "users.svg")),
            ("Configuración", os.path.join(svg_dir, "settings.svg")),
        ]

        # Fallback para iconos faltantes
        sidebar_sections_robustos = []
        placeholder_icon = os.path.join(
            os.path.dirname(__file__), "resources", "icons", "placeholder.svg"
        )
        for nombre, icono in sidebar_sections:
            if not os.path.exists(icono):
                icono = placeholder_icon if os.path.exists(placeholder_icon) else ""
            sidebar_sections_robustos.append((nombre, icono))

        # Crear sidebar mejorado
        if SidebarClass:
            try:
                # Usar FallbackSidebar simple
                self.sidebar = SidebarClass(
                    sections=sidebar_sections_robustos, mostrar_nombres=True
                )
                self.sidebar.pageChanged.connect(self.module_stack.setCurrentIndex)
                print("[OK] Sidebar creado exitosamente")
            except Exception as e:
                print(f"[WARN] Error creando sidebar: {e}")
                self.sidebar = None

        if not self.sidebar:
            # Fallback mejorado
            class EmptySidebarWrapper(QWidget):
                pageChanged = pyqtSignal(int)

                def __init__(self):
                    super().__init__()
                    self.sections = sidebar_sections_robustos
                    self.setStyleSheet(
                        """
                        QWidget {
                            background: #f1f5f9;
                            border-right: 2px solid #e2e8f0;
                            min-width: 200px;
                            max-width: 250px;
                        }
                    """
                    )
                    layout = QVBoxLayout(self)
                    label = QPushButton("[DATA] STOCK APP\n(Sidebar no disponible)")
                    label.setStyleSheet(
                        """
                        QPushButton {
                            background: #ef4444;
                            color: white;
                            padding: 20px;
                            border-radius: 8px;
                            font-weight: bold;
                            text-align: center;
                        }
                    """
                    )
                    layout.addWidget(label)
                    layout.addStretch()

                def set_sections(self, sections):
                    self.sections = sections

                def set_expanded(self, expanded):
                    pass

            self.sidebar = EmptySidebarWrapper()
            print("[WARN] Usando Sidebar básico como fallback")

        # Agregar widgets al layout horizontal
        main_horizontal_layout.addWidget(self.sidebar)
        main_horizontal_layout.addWidget(content_container, 1)  # Expandir contenido

        # Agregar el layout horizontal al layout vertical principal
        main_vertical_layout.addLayout(main_horizontal_layout, 1)

        self._ajustar_sidebar()

        # --- FILTRADO ROBUSTO Y DOCUMENTADO DE MÓDULOS EN SIDEBAR Y STACK PRINCIPAL ---
        # 1. Validar usuario antes de obtener módulos permitidos
        validacion_usuario, mensaje_usuario = validar_usuario_robusto(usuario)
        if not validacion_usuario:
            self.logger.warning(f"[VALIDACIÓN] Usuario inválido: {mensaje_usuario}")
            # Fallback: usar configuración mínima
            modulos_permitidos_usuario = ["Configuración"]
        else:
            # 2. Obtener módulos permitidos para el usuario actual (según permisos_modulos)
            try:
                modulos_obtenidos = self.usuarios_model.obtener_modulos_permitidos(
                    usuario
                )
                modulos_permitidos_usuario = validar_modulos_permitidos_robusto(
                    modulos_obtenidos
                )

                if not modulos_permitidos_usuario or modulos_permitidos_usuario == [
                    "Configuración"
                ]:
                    self.logger.warning(
                        f"[PERMISOS] No se encontraron módulos permitidos para el usuario: {usuario}"
                    )
            except Exception as e:
                import traceback

                self.logger.error(
                    f"[ERROR] Excepción al obtener módulos permitidos: {e}\n{traceback.format_exc()}"
                )
                # Fallback de emergencia usando función robusta
                modulos_permitidos_usuario = validar_modulos_permitidos_robusto(None)
                QMessageBox.warning(
                    self,
                    "Error de permisos",
                    f"Error al cargar permisos de usuario. Solo se habilitará Configuración.\nError: {e}",
                )

        # 3. Filtrar secciones del sidebar y widgets del stack según permisos
        secciones_filtradas = []
        indices_permitidos = []
        nombre_a_widget = {
            "Obras": self.obras_view,
            "Inventario": self.inventario_view,
            "Herrajes": self.herrajes_view,
            "Compras / Pedidos": self.compras_pedidos_view,
            "Logística": self.logistica_view,
            "Vidrios": self.vidrios_view,
            "Mantenimiento": self.mantenimiento_view,
            "Producción": self.produccion_view,
            "Contabilidad": self.contabilidad_view,
            "Auditoría": self.auditoria_view,
            "Usuarios": self.usuarios_view,
            "Configuración": self.configuracion_view,
        }

        # 4. Filtrar secciones y sincronizar con el stack
        for i, (nombre, icono) in enumerate(self.sidebar.sections):
            if nombre in modulos_permitidos_usuario:
                secciones_filtradas.append((nombre, icono))
                indices_permitidos.append(i)

        # 5. Si no hay módulos permitidos, aplicar fallback seguro (ya aplicado por validar_modulos_permitidos_robusto)
        if not secciones_filtradas or modulos_permitidos_usuario == ["Configuración"]:
            self.logger.warning(
                "[PERMISOS] Usuario con acceso limitado. Mostrando solo Configuración."
            )
            configuracion_icono = os.path.join(
                os.path.dirname(__file__), "utils", "configuracion.svg"
            )
            if not os.path.exists(configuracion_icono):
                configuracion_icono = os.path.join(
                    os.path.dirname(__file__), "img", "placeholder.svg"
                )
            secciones_filtradas = [("Configuración", configuracion_icono)]
            indices_permitidos = [list(nombre_a_widget.keys()).index("Configuración")]
            # Mostrar mensaje visual claro en la UI
            self.mostrar_mensaje(
                "Acceso limitado: Solo tienes acceso a Configuración. Contacta al administrador.",
                tipo="advertencia",
                duracion=8000,
            )

        # 6. Aplicar filtrado al sidebar
        self.sidebar.set_sections(secciones_filtradas)

        # 7. Seleccionar el primer módulo permitido como vista inicial
        if indices_permitidos:
            primer_indice = indices_permitidos[0]
            # Mapear el índice original al nuevo índice filtrado
            self.module_stack.setCurrentIndex(primer_indice)
        else:
            self.module_stack.setCurrentIndex(0)

        # 8. Accesibilidad: enfocar el sidebar tras el filtrado
        self.sidebar.setFocus()

        # 9. Documentación y log para diagnóstico
        self.logger.info(
            f"[PERMISOS] Sidebar filtrado: {[n for n, _ in secciones_filtradas]}"
        )
        self.logger.info(f"[PERMISOS] Índices permitidos: {indices_permitidos}")
        # --- FIN FILTRADO ROBUSTO DE MÓDULOS ---

        # Pasar usuario_actual a los controladores con verificación robusta
        controladores_principales = [
            self.inventario_controller,
            self.obras_controller,
            self.produccion_controller,
            self.logistica_controller,
            self.compras_pedidos_controller,
            self.pedidos_controller,
            self.usuarios_controller,
            self.auditoria_controller,
            self.configuracion_controller,
            self.herrajes_controller,
        ]

        for controller in controladores_principales:
            if controller and hasattr(controller, "usuario_actual"):
                controller.usuario_actual = usuario
                # Inicializar vista para el controlador de usuarios si es admin
                if (
                    controller == self.usuarios_controller
                    and usuario
                    and isinstance(usuario, dict)
                    and usuario.get("rol") == "admin"
                ):
                    try:
                        controller.inicializar_vista()
                        print("[OK] Vista de usuarios inicializada para admin")
                    except Exception as e:
                        print(f"[WARN] Error inicializando vista de usuarios: {e}")

        # Controladores opcionales con verificación de existencia
        controladores_opcionales = [
            ("mantenimiento_controller", self.mantenimiento_controller),
            ("contabilidad_controller", self.contabilidad_controller),
            ("vidrios_controller", self.vidrios_controller),
        ]

        for nombre, controller in controladores_opcionales:
            if controller and hasattr(controller, "usuario_actual"):
                controller.usuario_actual = usuario
                print(f"[OK] Usuario asignado a {nombre}")
            elif controller is None:
                print(f"[WARN] {nombre} no disponible (None)")
            else:
                print(f"[WARN] {nombre} no tiene atributo usuario_actual")

        # INTEGRACIÓN EN TIEMPO REAL ENTRE MÓDULOS (Obras, Inventario, Vidrios)
        # Conectar la señal obra_agregada de ObrasView a los controladores de Inventario y Vidrios
        if hasattr(self.obras_view, "obra_agregada"):
            if hasattr(self.inventario_controller, "actualizar_por_obra"):
                self.obras_view.obra_agregada.connect(
                    self.inventario_controller.actualizar_por_obra
                )
            if self.vidrios_controller and hasattr(
                self.vidrios_controller, "actualizar_por_obra"
            ):
                self.obras_view.obra_agregada.connect(
                    self.vidrios_controller.actualizar_por_obra
                )

    def showEvent(self, event):
        super().showEvent(event)
        self._ajustar_sidebar()

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QEvent.Type.WindowStateChange:
            self._ajustar_sidebar()

    def _ajustar_sidebar(self):
        expanded = self.isMaximized() or self.isFullScreen() or self.width() > 1400
        if self.sidebar and hasattr(self.sidebar, "set_expanded"):
            self.sidebar.set_expanded(expanded)

    # Métodos para manejar las señales del header moderno
    def on_global_search(self, query):
        """Maneja la búsqueda global desde el header."""
        print(f"[INFO] Búsqueda global: {query}")
        # TODO: Implementar búsqueda global en todos los módulos
        if hasattr(self, "_status_bar"):
            self._status_bar.showMessage(f"Buscando: {query}", 3000)

        # Por ahora, mostrar mensaje informativo
        from PyQt6.QtWidgets import QMessageBox

        QMessageBox.information(
            self,
            "Búsqueda Global",
            f"Función de búsqueda global en desarrollo.\nTérmino buscado: {query}",
        )

    def on_notifications_clicked(self):
        """Maneja el clic en notificaciones."""
        print("🔔 Abriendo notificaciones...")
        # TODO: Implementar sistema de notificaciones
        from PyQt6.QtWidgets import QMessageBox

        QMessageBox.information(
            self,
            "Notificaciones",
            "Sistema de notificaciones en desarrollo.\n\nPróximamente podrás ver:\n• Pedidos pendientes\n• Inventario bajo\n• Actualizaciones del sistema",
        )

    def on_profile_clicked(self):
        """Maneja el clic en el perfil de usuario."""
        print("[USER] Abriendo perfil de usuario...")

        if not self.usuario_actual:
            return

        from PyQt6.QtWidgets import QMessageBox

        usuario_info = f"""
        Usuario: {self.usuario_actual.get("usuario", "N/A")}
        Rol: {self.usuario_actual.get("rol", "N/A")}
        Nombre: {self.usuario_actual.get("nombre", "N/A")}
        Email: {self.usuario_actual.get("email", "N/A")}
        Estado: {self.usuario_actual.get("estado", "N/A")}
        """

        QMessageBox.information(
            self,
            "Perfil de Usuario",
            f"Información del usuario actual:\n{usuario_info}\n\nFunciones de perfil en desarrollo...",
        )

    def on_theme_toggle(self):
        """Maneja el cambio de tema claro/oscuro."""
        print("🌓 Cambiando tema...")

        try:
            from src.utils.theme_manager import (
                cargar_modo_tema,
                guardar_modo_tema,
                set_theme,
            )

            # Obtener tema actual
            tema_actual = cargar_modo_tema()
            nuevo_tema = "dark" if tema_actual == "light" else "light"

            # Guardar nuevo tema
            guardar_modo_tema(nuevo_tema)

            # Aplicar nuevo tema
            from PyQt6.QtWidgets import QApplication

            app = QApplication.instance()
            if app:
                set_theme(app, nuevo_tema)

            # Actualizar mensaje
            if hasattr(self, "_status_bar"):
                self._status_bar.showMessage(f"Tema cambiado a: {nuevo_tema}", 2000)

            print(f"[OK] Tema cambiado a: {nuevo_tema}")

        except Exception as e:
            print(f"[ERROR] Error cambiando tema: {e}")
            from PyQt6.QtWidgets import QMessageBox

            QMessageBox.warning(
                self, "Error de Tema", f"No se pudo cambiar el tema.\nError: {e}"
            )


def chequear_conexion_bd():
    import pyodbc

    # Puedes ajustar estos valores según tu configuración real
    DB_DRIVER = os.environ.get("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    DB_SERVER = os.environ.get("DB_SERVER", "localhost\\SQLEXPRESS")
    DB_DATABASE = os.environ.get("DB_DATABASE", "inventario")
    DB_USERNAME = os.environ.get("DB_USERNAME", "sa")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "tu_contraseña_aqui")
    try:
        connection_string = (
            f"DRIVER={{{DB_DRIVER}}};"
            f"SERVER={DB_SERVER};"
            f"DATABASE={DB_DATABASE};"
            f"UID={DB_USERNAME};"
            f"PWD={DB_PASSWORD};"
            f"TrustServerCertificate=yes;"
        )
        with pyodbc.connect(connection_string, timeout=10):
            print("[OK] Conexión exitosa a la base de datos.")
    except Exception as e:
        print(f"[ERROR] Error de conexión a la base de datos: {e}")
        print(
            "Verifica usuario, contraseña, servidor y que SQL Server acepte autenticación SQL."
        )
        sys.exit(1)


def chequear_conexion_bd_gui():
    """Verificación rápida de conectividad de BD - solo una vez al inicio"""
    from PyQt6.QtWidgets import QApplication, QMessageBox

    from src.core.config import (
        DB_DEFAULT_DATABASE,
        DB_PASSWORD,
        DB_SERVER,
        DB_SERVER_ALTERNATE,
        DB_TIMEOUT,
        DB_USERNAME,
    )

    DB_DRIVER = "ODBC Driver 17 for SQL Server"
    servidores = [DB_SERVER, DB_SERVER_ALTERNATE]
    for DB_SERVER_ACTUAL in servidores:
        try:
            print(f"[LOG 3.1] ⚡ Verificación rápida de BD: {DB_SERVER_ACTUAL}")
            connection_string = (
                f"DRIVER={{{DB_DRIVER}}};"
                f"SERVER={DB_SERVER_ACTUAL};"
                f"DATABASE={DB_DEFAULT_DATABASE};"
                f"UID={DB_USERNAME};"
                f"PWD={DB_PASSWORD};"
                f"TrustServerCertificate=yes;"
            )
            import pyodbc

            with pyodbc.connect(connection_string, timeout=5):  # Timeout reducido a 5s
                print(f"[LOG 3.2] ✅ BD disponible: {DB_SERVER_ACTUAL}")
                return
        except Exception as e:
            print(f"[LOG 3.3] ❌ BD no disponible ({DB_SERVER_ACTUAL}): {e}")
    print("[LOG 3.4] ❌ Sin acceso a BD. Mostrando error.")
    QApplication.instance() or QApplication(sys.argv)
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setWindowTitle("Error de conexión")
    msg.setText("❌ Sin acceso a la base de datos")
    msg.setInformativeText(
        f"Verifica conexión y credenciales.\nServidores: {DB_SERVER}, {DB_SERVER_ALTERNATE}"
    )
    msg.exec()
    sys.exit(1)


# --- DIAGNÓSTICO BÁSICO DE ENTORNO Y DEPENDENCIAS ---
def diagnostico_entorno_dependencias():
    """Diagnóstico básico de entorno y dependencias críticas."""
    import datetime
    import os
    import sys

    log_path = os.path.join(os.getcwd(), "logs", "diagnostico_dependencias.txt")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    def log(msg):
        print(msg, flush=True)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now().isoformat()} | {msg}\n")

    try:
        import pandas

        log(f"pandas importado correctamente. Versión: {pandas.__version__}")
    except Exception as e:
        log(f"Error importando pandas: {e}")
    try:
        import reportlab

        log(f"reportlab importado correctamente. Versión: {reportlab.__version__}")
    except Exception as e:
        log(f"Error importando reportlab: {e}")


diagnostico_entorno_dependencias()

chequear_conexion_bd_gui()

if __name__ == "__main__":
    print("[LOG 4.1] Iniciando QApplication...")
    app = QApplication(sys.argv)
    print("[LOG 4.2] Aplicando tema profesional...")
    try:
        set_theme(DEFAULT_THEME)
    except Exception as e:
        print(f"[LOG 4.3] Error aplicando tema: {e}")

    print("[LOG 4.4] Iniciando sistema de login directo...")

    # Inicializar sistema de seguridad
    security_manager = initialize_security_manager()

    # Crear dialog de login moderno
    login_dialog = LoginDialog()

    # Variable global para main window
    main_window = None

    # Conectar señales del dialog de login
    def on_login_success(username, role):
    print("[LOG 4.1] Iniciando QApplication...")
    app = QApplication(sys.argv)
    print("[LOG 4.2] Mostrando login profesional...")

    # Inicializar sistema de seguridad
    security_manager = initialize_security_manager()

    # Crear dialog de login moderno
    login_dialog = LoginDialog()

    # Conectar señales del dialog de login
    def on_login_success(username, role):
        print(f"✅ [LOGIN] Autenticación exitosa para {username} ({role})")
        user_data = security_manager.get_current_user()
        if not user_data:
            print("❌ [LOGIN] Error: No se pudo obtener datos del usuario")
            return
        modulos_permitidos = security_manager.get_user_modules(user_data["id"])
        cargar_main_window_con_seguridad(user_data, modulos_permitidos)

    def on_login_failed(error_message):
        print(f"❌ [LOGIN] Autenticación fallida: {error_message}")
        # El dialog ya muestra el mensaje de error

    login_dialog.login_successful.connect(on_login_success)
    login_dialog.login_failed.connect(on_login_failed)

    def cargar_main_window_con_seguridad(user_data, modulos_permitidos):
        global main_window
        try:
            print(f"🏗️ [SEGURIDAD] Creando MainWindow para usuario: {user_data['username']}")
            main_window = MainWindow(user_data, modulos_permitidos)
            main_window.actualizar_usuario_label(user_data)
            main_window.security_manager = security_manager
            main_window.mostrar_mensaje(
                f"¡Bienvenido {user_data['username']}! ({user_data['rol']})",
                tipo="exito",
                duracion=3000,
            )
            main_window.show()
            print(f"✅ [SEGURIDAD] Aplicación iniciada para {user_data['username']}")
        except Exception as e:
            import traceback
            error_msg = f"[ERROR SEGURIDAD] {e}\n{traceback.format_exc()}"
            print(f"❌ [ERROR] {error_msg}", flush=True)
            os.makedirs("logs", exist_ok=True)
            with open("logs/error_inicio_seguridad.txt", "a", encoding="utf-8") as f:
                f.write(error_msg + "\n")
            QMessageBox.critical(
                None,
                "Error crítico",
                f"Error al iniciar la aplicación con seguridad: {e}",
            )
            app.quit()

    # Mostrar login directamente
    login_dialog.show()
    print("[LOG 4.10] QApplication loop iniciado.")
    sys.exit(app.exec())
    # Conectar señales
