#!/usr/bin/env python3
"""
Script para crear un modo de usuario invitado que permita usar la aplicación sin login.
"""

def crear_modo_invitado():
    """Modifica la aplicación para permitir un modo invitado."""

    base_path = Path(__file__).parent.parent.parent
    main_py = base_path / "main.py"

    print("[INFO] Creando modo usuario invitado...")

    # Leer el archivo main.py
    with open(main_py, 'r', encoding='utf-8') as f:
        contenido = f.read()

    # Buscar la función continuar_inicio y modificarla
    buscar = '''def continuar_inicio():
        if error_dependencias:
            print("[LOG 4.5] Error de dependencias. Cerrando SplashScreen y abortando inicio de interfaz principal.")
            splash.fade_out.finished.connect(splash.close)
            splash.fade_out.start()
            QTimer.singleShot(1000, app.quit)
            return
        print("[LOG 4.6] Preparando LoginView y controladores...")
        db_connection_usuarios = DatabaseConnection()
        db_connection_usuarios.conectar_a_base("users")
        usuarios_model = UsuariosModel(db_connection=db_connection_usuarios)
        login_view = LoginView()
        login_controller = LoginController(login_view, usuarios_model)'''

    reemplazar = '''def continuar_inicio():
        if error_dependencias:
            print("[LOG 4.5] Error de dependencias. Cerrando SplashScreen y abortando inicio de interfaz principal.")
            splash.fade_out.finished.connect(splash.close)
            splash.fade_out.start()
            QTimer.singleShot(1000, app.quit)
            return

        # MODO INVITADO: Crear usuario por defecto para desarrollo/pruebas
        print("[LOG 4.6] Iniciando en modo invitado (sin login)...")
        usuario_invitado = {
            'id': 0,
            'usuario': 'invitado',
            'rol': 'TEST_USER',  # Permisos completos para desarrollo
            'ip': '127.0.0.1'
        }

        # Todos los módulos disponibles para el usuario invitado
        modulos_permitidos = [
            'Obras', 'Inventario', 'Herrajes', 'Compras / Pedidos',
            'Logística', 'Vidrios', 'Mantenimiento', 'Producción',
            'Contabilidad', 'Auditoría', 'Usuarios', 'Configuración'
        ]

        def iniciar_app_directamente():
            try:
                splash.close()
                main_window = MainWindow(usuario_invitado, modulos_permitidos)
                main_window.actualizar_usuario_label(usuario_invitado)
                main_window.mostrar_mensaje("Modo invitado - Sin autenticación", tipo="info", duracion=3000)
                main_window.show()
            except Exception as e:
                print(f"[ERROR MODO INVITADO] {e}\\n{traceback.format_exc()}", flush=True)
                with open("logs/error_inicio_ui.txt", "a", encoding="utf-8") as f:
                    f.write(f"[ERROR MODO INVITADO] {e}\\n{traceback.format_exc()}\\n")
                QMessageBox.critical(None, "Error crítico", f"Error al iniciar en modo invitado: {e}")
                app.quit()

        # Encadenar el fade out del splash al mostrar la app directamente
        splash.fade_out.finished.connect(iniciar_app_directamente)
        splash.fade_out.start()'''
import traceback
from pathlib import Path

from PyQt6.QtWidgets import QMessageBox

    if buscar in contenido:
        contenido = contenido.replace(buscar, reemplazar)

        # Escribir el archivo modificado
        with open(main_py, 'w', encoding='utf-8') as f:
            f.write(contenido)

        print("[OK] Modo invitado creado exitosamente")
        return True
    else:
        print("[ERROR] No se pudo encontrar la función continuar_inicio para modificar")
        return False

def crear_modo_login_opcional():
    """Crea una versión que permite tanto login como modo invitado."""
    print("[INFO] Esta funcionalidad se implementará si es necesario")
    return True

def main():
    """Función principal."""
    print("[TOOL] Configurando modo invitado para desarrollo...")

    if crear_modo_invitado():
        print("[OK] Aplicación configurada en modo invitado")
        print("[INFO] La aplicación ya no requerirá login y usará un usuario 'invitado' con permisos completos")
        print("[INFO] Esto resuelve los problemas de permisos y auditoría")
    else:
        print("[ERROR] No se pudo configurar el modo invitado")

if __name__ == "__main__":
    main()
