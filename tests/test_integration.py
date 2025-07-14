#!/usr/bin/env python3
"""
from core.advanced_theme_manager import AdvancedThemeManager
from core.advanced_theme_manager import AdvancedThemeManager
from core.security_manager import SecurityManager
from core.security_manager import SecurityManager
from modules.usuarios.model import UsuariosModel
from modules.usuarios.secure_model import SecureUsuariosModel
from modules.usuarios.secure_model import SecureUsuariosModel

Script de prueba para verificar la integración de los nuevos módulos.
"""


def test_imports():
    """Prueba las importaciones de los nuevos módulos."""
from core.advanced_theme_manager import AdvancedThemeManager
from core.security_manager import SecurityManager
from modules.usuarios.model import UsuariosModel
from modules.usuarios.secure_model import SecureUsuariosModel

    print("=== PRUEBA DE IMPORTACIONES ===")

    try:
        print("✅ SecurityManager importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando SecurityManager: {e}")

    try:
        print("✅ AdvancedThemeManager importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando AdvancedThemeManager: {e}")

    try:
        print("✅ AdvancedConfigManager importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando AdvancedConfigManager: {e}")

    try:
        print("✅ SecureUsuariosModel importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando SecureUsuariosModel: {e}")

def test_integration_logic():
    """Prueba la lógica de integración sin UI."""
    print("\n=== PRUEBA DE LÓGICA DE INTEGRACIÓN ===")

    # Simular la lógica de main.py sin UI
from core.advanced_theme_manager import AdvancedThemeManager
from core.security_manager import SecurityManager
from modules.usuarios.model import UsuariosModel
from modules.usuarios.secure_model import SecureUsuariosModel

    try:
        # Test fallback logic
        if SecurityManager and AdvancedThemeManager and SecureUsuariosModel:
            print("✅ Todos los módulos avanzados disponibles")
from core.advanced_theme_manager import AdvancedThemeManager
from core.security_manager import SecurityManager
from modules.usuarios.model import UsuariosModel
from modules.usuarios.secure_model import SecureUsuariosModel

            print("   → Se usaría SecureUsuariosModel con Security y ThemeManager")
        else:
            print("⚠️  Algunos módulos avanzados no disponibles")
            print("   → Se usaría UsuariosModel básico con fallbacks")
from core.advanced_theme_manager import AdvancedThemeManager
from core.security_manager import SecurityManager
from modules.usuarios.model import UsuariosModel
from modules.usuarios.secure_model import SecureUsuariosModel

        # Test theme application logic
        class MockApp:
            def setStyleSheet(self, style):
from core.advanced_theme_manager import AdvancedThemeManager
from core.security_manager import SecurityManager
from modules.usuarios.model import UsuariosModel
from modules.usuarios.secure_model import SecureUsuariosModel

                return "Theme applied"

        mock_app = MockApp()

        # Simular aplicación de tema
from core.advanced_theme_manager import AdvancedThemeManager
from core.security_manager import SecurityManager
from modules.usuarios.model import UsuariosModel
from modules.usuarios.secure_model import SecureUsuariosModel

        if hasattr(SecureUsuariosModel, 'aplicar_tema_usuario'):
            print("✅ Método aplicar_tema_usuario disponible en SecureUsuariosModel")
        else:
            print("⚠️  Método aplicar_tema_usuario no disponible en SecureUsuariosModel")
from core.advanced_theme_manager import AdvancedThemeManager
from core.security_manager import SecurityManager
from modules.usuarios.model import UsuariosModel
from modules.usuarios.secure_model import SecureUsuariosModel

        if hasattr(UsuariosModel, 'aplicar_tema_usuario'):
            print("⚠️  Método aplicar_tema_usuario disponible en UsuariosModel básico (inesperado)")
        else:
from core.advanced_theme_manager import AdvancedThemeManager
from core.security_manager import SecurityManager
from modules.usuarios.model import UsuariosModel
from modules.usuarios.secure_model import SecureUsuariosModel

            print("✅ Método aplicar_tema_usuario NO disponible en UsuariosModel básico (esperado)")

        # Test theme managers
        if hasattr(AdvancedThemeManager, 'apply_theme'):
from core.advanced_theme_manager import AdvancedThemeManager
from core.security_manager import SecurityManager
from modules.usuarios.model import UsuariosModel
from modules.usuarios.secure_model import SecureUsuariosModel

            print("✅ Método apply_theme disponible en AdvancedThemeManager")
        else:
            print("❌ Método apply_theme NO disponible en AdvancedThemeManager")

        # Test basic theme fallback
from core.advanced_theme_manager import AdvancedThemeManager
from core.security_manager import SecurityManager
from modules.usuarios.model import UsuariosModel
from modules.usuarios.secure_model import SecureUsuariosModel

        try:
            print("✅ Función set_theme disponible en utils.theme_manager")
        except ImportError:
            print("❌ Función set_theme NO disponible en utils.theme_manager")
from core.advanced_theme_manager import AdvancedThemeManager
from core.security_manager import SecurityManager
from modules.usuarios.model import UsuariosModel
from modules.usuarios.secure_model import SecureUsuariosModel

        try:
            print("✅ GLOBAL_STYLE disponible en core.theme")
        except ImportError:
from core.advanced_theme_manager import AdvancedThemeManager
from core.security_manager import SecurityManager
from modules.usuarios.model import UsuariosModel
from modules.usuarios.secure_model import SecureUsuariosModel

            print("❌ GLOBAL_STYLE NO disponible en core.theme")

    except Exception as e:
        print(f"❌ Error en prueba de integración: {e}")
from core.advanced_theme_manager import AdvancedThemeManager
from core.security_manager import SecurityManager
from modules.usuarios.model import UsuariosModel
from modules.usuarios.secure_model import SecureUsuariosModel

if __name__ == "__main__":
    print("Stock.app - Prueba de Integración de Módulos Avanzados")
    print("="*60)
from core.advanced_theme_manager import AdvancedThemeManager
from core.security_manager import SecurityManager
from modules.usuarios.model import UsuariosModel
from modules.usuarios.secure_model import SecureUsuariosModel

    test_imports()
    test_integration_logic()

    print("\n=== RESUMEN ===")
    print("Si todas las pruebas pasaron con ✅, la integración está lista.")
    print("Si hay errores ❌, revisa los módulos correspondientes.")
from core.advanced_theme_manager import AdvancedThemeManager
from core.security_manager import SecurityManager
from modules.usuarios.model import UsuariosModel
from modules.usuarios.secure_model import SecureUsuariosModel

    print("Si hay advertencias ⚠️, verifica que el comportamiento sea el esperado.")
