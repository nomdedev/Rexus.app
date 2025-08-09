"""
Test de Verificación del Sistema de Notificaciones
Valida que el sistema de notificaciones funciona correctamente
"""
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class TestSistemaNotificaciones:
    """Clase para probar el sistema de notificaciones"""

    def __init__(self):
        """Inicializar el test"""
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.db = None
import os
import sys
import traceback

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication
from widgets.sistema_notificaciones import SistemaNotificaciones

from core.database import ObrasDatabaseConnection
from core.integracion_obras import IntegracionObrasModel

        self.integracion_model = None
        self.sistema_notificaciones = None

    def setup(self):
        """Configurar el entorno de prueba"""
        try:
            # Conexión a BD
            self.db = ObrasDatabaseConnection()
            self.db.conectar()
            print("[CHECK] Conectado a base de datos")

            # Modelo de integración
            self.integracion_model = IntegracionObrasModel(self.db)
            print("[CHECK] Modelo de integración inicializado")

            # Sistema de notificaciones
            self.sistema_notificaciones = SistemaNotificaciones()
            print("[CHECK] Sistema de notificaciones creado")

            return True
        except Exception as e:
            print(f"[ERROR] Error en setup: {e}")
            traceback.print_exc()
            return False

    def test_verificar_obras(self):
        """Verificar obras y notificaciones"""
        try:
            print("\n📋 Verificando obras en sistema...")
            # Obtener todas las obras
            if not self.integracion_model or not hasattr(self.integracion_model, 'obras_model') or self.integracion_model.obras_model is None:
                print("[ERROR] El modelo de integración o su atributo 'obras_model' no está inicializado correctamente")
                return False
            if not self.integracion_model or not hasattr(self.integracion_model, 'obras_model') or self.integracion_model.obras_model is None:
                print("[ERROR] El modelo de integración o su atributo 'obras_model' no está inicializado correctamente")
                return False
            obras = self.integracion_model.obras_model.obtener_obras()
            if not obras:
                print("[WARN] No hay obras registradas para probar")
                return False

            print(f"[CHECK] Se encontraron {len(obras)} obras")

            # Verificar estado de cada obra
            for obra in obras[:3]:  # Limitar a 3 obras para eficiencia
                id_obra = obra[0] if isinstance(obra, tuple) else obra['id'] if isinstance(obra, dict) else None
                if not id_obra:
                    continue

                print(f"\n🔍 Verificando obra ID {id_obra}...")
                estado = self.integracion_model.verificar_estado_completo_obra(id_obra)

                # Verificar estado
                print(f"  [CHART] Estado general: {estado['estado_general']}")
                print(f"  🛠️ Puede avanzar: {estado.get('puede_avanzar', False)}")

                # Verificar módulos
                for modulo, info in estado['modulos'].items():
                    print(f"  - {modulo}: {info['estado']} ({info['pendientes']} pendientes)")

                # Verificar notificaciones
                notificaciones = estado.get('notificaciones', [])
                print(f"  🔔 Notificaciones: {len(notificaciones)}")
                for i, notif in enumerate(notificaciones):
                    print(f"    {i+1}. [{notif['tipo']}] {notif['mensaje'][:50]}...")

            return True
        except Exception as e:
            print(f"[ERROR] Error al verificar obras: {e}")
            traceback.print_exc()
            return False

    def test_sistema_notificaciones_ui(self):
        """Probar la interfaz del sistema de notificaciones"""
        try:
            print("\n🖼️ Probando interfaz de notificaciones...")

            # Configurar sistema de notificaciones
            if self.sistema_notificaciones:
                if self.integracion_model is not None:
                    self.sistema_notificaciones.integracion_model = self.integracion_model
                else:
                    print("[ERROR] 'integracion_model' es None y no se puede asignar")
                    return False
                self.sistema_notificaciones.show()
                print("[CHECK] Sistema de notificaciones mostrado")

                # Actualizar notificaciones
                self.sistema_notificaciones.actualizar_notificaciones()
                print("[CHECK] Notificaciones actualizadas")

                # Verificar notificaciones mostradas
                notif_count = self.sistema_notificaciones.notificaciones_layout.count() if hasattr(self.sistema_notificaciones, 'notificaciones_layout') else 0
                print(f"[CHECK] Se muestran {notif_count} notificaciones en la interfaz")

                # Simular interacción con timeout para no bloquear la interfaz
                QTimer.singleShot(3000, self.app.quit)
                print("⏱️ Mostrando interfaz por 3 segundos...")
                self.app.exec()

                return True
            else:
                print("[ERROR] Sistema de notificaciones no inicializado")
                return False
        except Exception as e:
            print(f"[ERROR] Error en prueba de interfaz: {e}")
            traceback.print_exc()
            return False

    def test_verificar_avance_obras(self):
        """Verificar lógica de avance de obras"""
        try:
            print("\n🚦 Verificando lógica de avance de obras...")

            # Obtener obras
            if not self.integracion_model or not hasattr(self.integracion_model, 'obras_model') or self.integracion_model.obras_model is None:
                print("[ERROR] El modelo de integración o su atributo 'obras_model' no está inicializado correctamente")
                return False
            obras = self.integracion_model.obras_model.obtener_obras()
            if not obras:
                print("[WARN] No hay obras registradas para probar")
                return False

            # Encontrar una obra para probar
            id_obra = None
            for obra in obras:
                id_obra = obra[0] if isinstance(obra, tuple) else obra['id'] if isinstance(obra, dict) else None
                if id_obra:
                    break

            if not id_obra:
                print("[ERROR] No se pudo identificar una obra para pruebas")
                return False

            print(f"🔍 Verificando avance de obra ID {id_obra}...")

            # Verificar estado inicial
            estado_inicial = self.integracion_model.verificar_estado_completo_obra(id_obra)
            puede_avanzar = estado_inicial.get('puede_avanzar', False)

            print(f"  [CHART] Estado actual: {estado_inicial['estado_general']}")
            print(f"  🚦 Puede avanzar: {puede_avanzar}")

            if puede_avanzar:
                print("  [CHECK] La obra puede avanzar - Validación correcta")
            else:
                print("  [WARN] La obra no puede avanzar - Verificando motivos...")

                # Verificar pendientes por módulo
                pendientes = []
                for modulo, info in estado_inicial['modulos'].items():
                    if info['pendientes'] > 0:
                        pendientes.append(f"{modulo} ({info['pendientes']} pendientes)")

                if pendientes:
                    print(f"  [ERROR] Motivos que impiden avance: {', '.join(pendientes)}")
                    print("  [CHECK] Verificación de bloqueo correcta")
                else:
                    print("  [WARN] No se identificaron pendientes claros que impidan el avance")

            return True
        except Exception as e:
            print(f"[ERROR] Error al verificar avance: {e}")
            traceback.print_exc()
            return False

    def teardown(self):
        """Limpiar recursos después de las pruebas"""
        try:
            if self.sistema_notificaciones:
                self.sistema_notificaciones.close()

            if self.db:
                self.db.cerrar_conexion()
                print("[CHECK] Conexión cerrada")
        except Exception as e:
            print(f"[WARN] Error en teardown: {e}")

    def ejecutar_tests(self):
        """Ejecutar todas las pruebas"""
        print("[ROCKET] INICIANDO VERIFICACIÓN DEL SISTEMA DE NOTIFICACIONES")
        print("=" * 70)

        try:
            # Setup
            if not self.setup():
                print("[ERROR] Falló la configuración inicial")
                return False

            # Test 1: Verificar obras y notificaciones
            test1_ok = self.test_verificar_obras()

            # Test 2: Verificar interfaz de notificaciones
            test2_ok = self.test_sistema_notificaciones_ui()

            # Test 3: Verificar lógica de avance de obras
            test3_ok = self.test_verificar_avance_obras()

            # Resumen
            print("\n📋 RESUMEN DE VERIFICACIÓN")
            print("=" * 70)
            print(f"🔍 Verificación de obras y notificaciones: {'[CHECK] PASS' if test1_ok else '[ERROR] FAIL'}")
            print(f"🖼️ Interfaz del sistema de notificaciones: {'[CHECK] PASS' if test2_ok else '[ERROR] FAIL'}")
            print(f"🚦 Lógica de avance de obras: {'[CHECK] PASS' if test3_ok else '[ERROR] FAIL'}")

            overall_status = all([test1_ok, test2_ok, test3_ok])
            print("\n🏁 RESULTADO FINAL")
            print("=" * 70)
            if overall_status:
                print("[CHECK] SISTEMA DE NOTIFICACIONES FUNCIONANDO CORRECTAMENTE")
            else:
                print("[ERROR] SE DETECTARON PROBLEMAS EN EL SISTEMA DE NOTIFICACIONES")

            return overall_status
        finally:
            self.teardown()

if __name__ == "__main__":
    test = TestSistemaNotificaciones()
    test.ejecutar_tests()
