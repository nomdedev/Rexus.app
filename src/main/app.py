# --- IMPORTS MÍNIMOS REQUERIDOS PARA FUNCIONAMIENTO ---
import os
import platform
import sys

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
# from components.sidebar_button import SidebarButton  # Módulo no disponible
from PyQt6.QtWidgets import QApplication, QMessageBox

from src.core.login_dialog import LoginDialog
from src.core.security import initialize_security_manager


class MainWindow(QMessageBox):
    def __init__(self, user_data, modulos_permitidos):
        super().__init__()
        self.setWindowTitle("Stub MainWindow")
        self.setText(
            f"Bienvenido {user_data.get('username', 'Usuario')}\nRol: {user_data.get('rol', '')}"
        )
        self.security_manager = None

    def actualizar_usuario_label(self, user_data):
        pass

    def mostrar_mensaje(self, mensaje, tipo="info", duracion=2000):
        self.setText(mensaje)
        self.show()


from src.utils.theme_manager import set_theme

# --- FIN IMPORTS PRINCIPALES ---


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
                f"{paquete}=={version}",
            ]
            # Aquí normalmente se llamaría a subprocess para instalar
            # subprocess.check_call(cmd)
            print(f"[LOG 1.2.2] Comando pip generado: {cmd}")
            return True
        except Exception as e:
            print(f"[LOG 1.2.3] [ERROR] Error instalando dependencia {paquete}: {e}")
            return False


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
            print(
                f"🏗️ [SEGURIDAD] Creando MainWindow para usuario: {user_data['username']}"
            )
            main_window = MainWindow(user_data, modulos_permitidos)
            main_window.actualizar_usuario_label(user_data)
            # Inicializar el atributo si no existe
            if not hasattr(main_window, "security_manager"):
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
    # QApplication.instance() or QApplication(sys.argv)  # Eliminado: expresión sin uso
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
