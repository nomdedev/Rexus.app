#!/usr/bin/env python3
"""
Script de navegación automática por todos los módulos de la aplicación
para detectar errores durante el uso real.
"""

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Configurar el entorno Qt antes de importar PyQt5
os.environ['QT_QPA_PLATFORM'] = 'windows'

try:
    # Importar componentes de la aplicación
except ImportError as e:
    print(f"❌ Error al importar módulos necesarios: {e}")
    sys.exit(1)

class NavegadorAutomatico(QObject):
    """Navegador automático por los módulos de la aplicación"""

    error_detectado = pyqtSignal(str)

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.errores = []
        self.modulos_probados = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.siguiente_prueba)
        self.indice_actual = 0

        # Lista de pruebas a realizar
        self.pruebas = [
            self.probar_inventario,
            self.probar_obras,
            self.probar_pedidos,
            self.probar_compras,
            self.probar_vidrios,
            self.probar_herrajes,
            self.probar_contabilidad,
            self.probar_mantenimiento,
            self.probar_configuracion,
            self.probar_auditoria,
            self.probar_usuarios,
            self.probar_logistica,
            self.probar_notificaciones
        ]

    def iniciar_navegacion(self):
        """Inicia la navegación automática"""
        print("🚀 Iniciando navegación automática por módulos...")
        self.indice_actual = 0
        self.timer.start(3000)  # 3 segundos entre pruebas

    def siguiente_prueba(self):
        """Ejecuta la siguiente prueba"""
        if self.indice_actual >= len(self.pruebas):
            self.finalizar_navegacion()
            return

        try:
            prueba = self.pruebas[self.indice_actual]
            print(f"📋 Ejecutando: {prueba.__name__}")
            prueba()
            self.modulos_probados.append(prueba.__name__)
        except Exception as e:
            error_msg = f"❌ Error en {prueba.__name__}: {str(e)}"
            print(error_msg)
            self.errores.append(error_msg)

        self.indice_actual += 1

    def probar_inventario(self):
        """Prueba el módulo de inventario"""
        try:
            # Navegar al módulo de inventario
            if hasattr(self.main_window, 'navigate_to_module'):
                self.main_window.navigate_to_module('inventario')
            elif hasattr(self.main_window, 'show_inventario'):
                self.main_window.show_inventario()
            print("✅ Módulo inventario accesible")
        except Exception as e:
            raise Exception(f"Error al acceder a inventario: {str(e)}")

    def probar_obras(self):
        """Prueba el módulo de obras"""
        try:
            if hasattr(self.main_window, 'navigate_to_module'):
                self.main_window.navigate_to_module('obras')
            elif hasattr(self.main_window, 'show_obras'):
                self.main_window.show_obras()
            print("✅ Módulo obras accesible")
        except Exception as e:
            raise Exception(f"Error al acceder a obras: {str(e)}")

    def probar_pedidos(self):
        """Prueba el módulo de pedidos"""
        try:
            if hasattr(self.main_window, 'navigate_to_module'):
                self.main_window.navigate_to_module('pedidos')
            elif hasattr(self.main_window, 'show_pedidos'):
                self.main_window.show_pedidos()
            print("✅ Módulo pedidos accesible")
        except Exception as e:
            raise Exception(f"Error al acceder a pedidos: {str(e)}")

    def probar_compras(self):
        """Prueba el módulo de compras"""
        try:
            if hasattr(self.main_window, 'navigate_to_module'):
                self.main_window.navigate_to_module('compras')
            elif hasattr(self.main_window, 'show_compras'):
                self.main_window.show_compras()
            print("✅ Módulo compras accesible")
        except Exception as e:
            raise Exception(f"Error al acceder a compras: {str(e)}")

    def probar_vidrios(self):
        """Prueba el módulo de vidrios"""
        try:
            if hasattr(self.main_window, 'navigate_to_module'):
                self.main_window.navigate_to_module('vidrios')
            elif hasattr(self.main_window, 'show_vidrios'):
                self.main_window.show_vidrios()
            print("✅ Módulo vidrios accesible")
        except Exception as e:
            raise Exception(f"Error al acceder a vidrios: {str(e)}")

    def probar_herrajes(self):
        """Prueba el módulo de herrajes"""
        try:
            if hasattr(self.main_window, 'navigate_to_module'):
                self.main_window.navigate_to_module('herrajes')
            elif hasattr(self.main_window, 'show_herrajes'):
                self.main_window.show_herrajes()
            print("✅ Módulo herrajes accesible")
        except Exception as e:
            raise Exception(f"Error al acceder a herrajes: {str(e)}")

    def probar_contabilidad(self):
        """Prueba el módulo de contabilidad"""
        try:
            if hasattr(self.main_window, 'navigate_to_module'):
                self.main_window.navigate_to_module('contabilidad')
            elif hasattr(self.main_window, 'show_contabilidad'):
                self.main_window.show_contabilidad()
            print("✅ Módulo contabilidad accesible")
        except Exception as e:
            raise Exception(f"Error al acceder a contabilidad: {str(e)}")

    def probar_mantenimiento(self):
        """Prueba el módulo de mantenimiento"""
        try:
            if hasattr(self.main_window, 'navigate_to_module'):
                self.main_window.navigate_to_module('mantenimiento')
            elif hasattr(self.main_window, 'show_mantenimiento'):
                self.main_window.show_mantenimiento()
            print("✅ Módulo mantenimiento accesible")
        except Exception as e:
            raise Exception(f"Error al acceder a mantenimiento: {str(e)}")

    def probar_configuracion(self):
        """Prueba el módulo de configuración"""
        try:
            if hasattr(self.main_window, 'navigate_to_module'):
                self.main_window.navigate_to_module('configuracion')
            elif hasattr(self.main_window, 'show_configuracion'):
                self.main_window.show_configuracion()
            print("✅ Módulo configuración accesible")
        except Exception as e:
            raise Exception(f"Error al acceder a configuración: {str(e)}")

    def probar_auditoria(self):
        """Prueba el módulo de auditoría"""
        try:
            if hasattr(self.main_window, 'navigate_to_module'):
                self.main_window.navigate_to_module('auditoria')
            elif hasattr(self.main_window, 'show_auditoria'):
                self.main_window.show_auditoria()
            print("✅ Módulo auditoría accesible")
        except Exception as e:
            raise Exception(f"Error al acceder a auditoría: {str(e)}")

    def probar_usuarios(self):
        """Prueba el módulo de usuarios"""
        try:
            if hasattr(self.main_window, 'navigate_to_module'):
                self.main_window.navigate_to_module('usuarios')
            elif hasattr(self.main_window, 'show_usuarios'):
                self.main_window.show_usuarios()
            print("✅ Módulo usuarios accesible")
        except Exception as e:
            raise Exception(f"Error al acceder a usuarios: {str(e)}")

    def probar_logistica(self):
        """Prueba el módulo de logística"""
        try:
            if hasattr(self.main_window, 'navigate_to_module'):
                self.main_window.navigate_to_module('logistica')
            elif hasattr(self.main_window, 'show_logistica'):
                self.main_window.show_logistica()
            print("✅ Módulo logística accesible")
        except Exception as e:
            raise Exception(f"Error al acceder a logística: {str(e)}")

    def probar_notificaciones(self):
        """Prueba el módulo de notificaciones"""
        try:
            if hasattr(self.main_window, 'navigate_to_module'):
                self.main_window.navigate_to_module('notificaciones')
            elif hasattr(self.main_window, 'show_notificaciones'):
                self.main_window.show_notificaciones()
            print("✅ Módulo notificaciones accesible")
        except Exception as e:
            raise Exception(f"Error al acceder a notificaciones: {str(e)}")

    def finalizar_navegacion(self):
        """Finaliza la navegación y genera reporte"""
        self.timer.stop()

        print("\n" + "="*60)
        print("📊 REPORTE DE NAVEGACIÓN AUTOMÁTICA")
        print("="*60)
        print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"✅ Módulos probados exitosamente: {len(self.modulos_probados)}")
        print(f"❌ Errores detectados: {len(self.errores)}")

        if self.modulos_probados:
            print("\n📝 Módulos probados:")
            for modulo in self.modulos_probados:
                print(f"  ✅ {modulo}")

        if self.errores:
            print("\n🚨 Errores encontrados:")
            for error in self.errores:
                print(f"  {error}")
        else:
            print("\n🎉 ¡No se detectaron errores durante la navegación!")

        # Guardar reporte
        reporte = {
            'fecha': datetime.now().isoformat(),
            'modulos_probados': self.modulos_probados,
            'errores': self.errores,
            'total_modulos': len(self.pruebas),
            'exito': len(self.errores) == 0
        }

        try:
            os.makedirs('tests/reports', exist_ok=True)
            with open('tests/reports/navegacion_automatica.json', 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Reporte guardado en: tests/reports/navegacion_automatica.json")
        except Exception as e:
            print(f"⚠️ No se pudo guardar el reporte: {e}")

        print("\n✨ Navegación automática completada")

def main():
    """Función principal"""
    print("🔍 Iniciando prueba de navegación automática...")

    # Verificar que la app no esté ya ejecutándose
    try:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        # Simular el flujo de inicio de la aplicación
        db = DatabaseConnection()
        if not db.test_connection():
            print("❌ No se puede conectar a la base de datos")
            return False

        # Crear ventana principal con usuario invitado para testing
        main_window = MainWindow()

        # Configurar usuario invitado para testing
        main_window.current_user = {
            'id': 0,
import json
import os
import sys
from datetime import datetime

from PyQt5.QtCore import QObject, QTimer, pyqtSignal
from PyQt5.QtWidgets import QApplication

from core.database import DatabaseConnection
from main import MainWindow

            'username': 'invitado',
            'role': 'invitado',
            'nombre': 'Usuario Invitado'
        }

        main_window.show()

        # Crear y ejecutar navegador automático
        navegador = NavegadorAutomatico(main_window)

        # Esperar a que la ventana esté completamente cargada
        QTimer.singleShot(2000, navegador.iniciar_navegacion)

        # Ejecutar la aplicación
        if app:
            app.exec_()

    except Exception as e:
        print(f"❌ Error durante la ejecución: {e}")
        return False

    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
