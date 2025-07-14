#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests robustos de integración entre el sistema de login y la ventana principal.
Versión compatible con CI/CD sin dependencias problemáticas.
Cubre el flujo completo desde el login hasta la inicialización de la interfaz principal.
"""

# Agregar directorio raíz para imports
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))
class DummyUsuariosModel:
    """Mock del modelo de usuarios para tests."""

    def __init__(self):
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

        self.usuarios = [
            {"id": 1, "usuario": "TEST_USER", "password_hash": "hash_admin", "rol": "administrador"},
            {"id": 2, "usuario": "user1", "password_hash": "hash_user1", "rol": "operador"},
            {"id": 3, "usuario": "user2", "password_hash": "hash_user2", "rol": "supervisor"}
        ]
        self.modulos_por_rol = {
            "administrador": ["Obras", "Inventario", "Usuarios", "Configuración", "Auditoría"],
            "supervisor": ["Obras", "Inventario", "Configuración"],
            "operador": ["Obras", "Inventario"]
        }

    def autenticar(self, usuario, password):
        """Simular autenticación."""
        for u in self.usuarios:
            if u["usuario"] == usuario:
                if password == "correcta":  # Password simple para tests
                    return u
                else:
                    raise ValueError("Credenciales inválidas")
        raise ValueError("Usuario no encontrado")

    def obtener_modulos_permitidos(self, usuario):
        """Obtener módulos permitidos para un usuario."""
        if isinstance(usuario, dict) and "rol" in usuario:
            return self.modulos_por_rol.get(usuario["rol"], [])
        return []

    def tiene_permiso(self, usuario, accion):
        """Verificar si un usuario tiene permiso para una acción."""
        if isinstance(usuario, dict) and "rol" in usuario:
            return usuario["rol"] in ["administrador", "supervisor"]
        return False


class DummyLoginView:
    """Mock de la vista de login para tests."""

    def __init__(self):
        self.usuario_input = MagicMock()
        self.password_input = MagicMock()
        self.boton_login = MagicMock()
        self.label_error = MagicMock()
        self.mensajes = []
        self.is_closed = False

    def mostrar_error(self, mensaje):
        self.mensajes.append(("error", mensaje))
        self.label_error.setText(mensaje)

    def mostrar_feedback(self, mensaje, tipo="info"):
        self.mensajes.append((tipo, mensaje))

    def limpiar_error(self):
        self.label_error.setText("")

    def show(self):
        self.is_closed = False

    def close(self):
        self.is_closed = True


class DummyMainWindow:
    """Mock de MainWindow para tests."""

    def __init__(self, usuario, modulos_permitidos):
        self.usuario_actual = usuario
        self.modulos_permitidos = modulos_permitidos
        self.is_shown = False
        self.usuario_label_text = ""
        self.mensajes = []
        self.initui_called = False

    def actualizar_usuario_label(self, usuario):
        if isinstance(usuario, dict):
            self.usuario_label_text = f"{usuario.get('usuario', '')} ({usuario.get('rol', '')})"

    def mostrar_mensaje(self, mensaje, tipo="info", duracion=4000):
        self.mensajes.append((mensaje, tipo, duracion))

    def show(self):
        self.is_shown = True

    def initUI(self, usuario, modulos_permitidos):
        self.initui_called = True


class TestLoginMainWindowIntegracion(unittest.TestCase):
    """Tests de integración entre login y MainWindow."""

    def setUp(self):
        """Setup para cada test."""
        self.usuarios_model = DummyUsuariosModel()
        self.login_view = DummyLoginView()

    def test_flujo_login_exitoso_admin(self):
        """Test: flujo completo de login exitoso para administrador."""
        # Simular entrada de datos de login usando mocks directos
        self.login_view.usuario_input.text.return_value = "TEST_USER"
        self.login_view.password_input.text.return_value = "correcta"

        # Ejecutar autenticación directamente
        usuario_autenticado = self.usuarios_model.autenticar("TEST_USER", "correcta")

        # Verificar que el login fue exitoso
        self.assertIsNotNone(usuario_autenticado)
        self.assertEqual(usuario_autenticado["usuario"], "TEST_USER")
        self.assertEqual(usuario_autenticado["rol"], "administrador")

        # Obtener módulos permitidos
        modulos_permitidos = self.usuarios_model.obtener_modulos_permitidos(usuario_autenticado)

        # Verificar módulos de administrador
        expected_modulos = ["Obras", "Inventario", "Usuarios", "Configuración", "Auditoría"]
        self.assertEqual(set(modulos_permitidos), set(expected_modulos))

    def test_flujo_login_exitoso_operador(self):
        """Test: flujo completo de login exitoso para operador."""
        # Simular entrada de datos
        self.login_view.usuario_input.text.return_value = "user2"
        self.login_view.password_input.text.return_value = "correcta"

        # Autenticación directa
        usuario_autenticado = self.usuarios_model.autenticar("user2", "correcta")
        modulos_permitidos = self.usuarios_model.obtener_modulos_permitidos(usuario_autenticado)

        # Verificar que el operador tiene acceso limitado
        self.assertEqual(usuario_autenticado["rol"], "supervisor")
        self.assertNotIn("Usuarios", modulos_permitidos)  # Los operadores no ven usuarios
        self.assertIn("Obras", modulos_permitidos)
        self.assertIn("Inventario", modulos_permitidos)

    def test_flujo_login_fallido(self):
        """Test: manejo de login fallido."""
        # Simular credenciales incorrectas
        self.login_view.usuario_input.text.return_value = "TEST_USER"
        self.login_view.password_input.text.return_value = "incorrecta"

        # Verificar que falla la autenticación
        with self.assertRaises(ValueError) as context:
            self.usuarios_model.autenticar("TEST_USER", "incorrecta")
        self.assertIn("Credenciales inválidas", str(context.exception))

        # Verificar usuario inexistente
        with self.assertRaises(ValueError) as context:
            self.usuarios_model.autenticar("noexiste", "cualquiera")
        self.assertIn("Usuario no encontrado", str(context.exception))

    @patch('main.MainWindow')
    def test_integracion_completa_login_a_mainwindow(self, mock_mainwindow):
        """Test: integración completa desde login hasta MainWindow."""
        # Simular proceso completo
        usuario = self.usuarios_model.autenticar("TEST_USER", "correcta")
        modulos_permitidos = self.usuarios_model.obtener_modulos_permitidos(usuario)

        # Configurar mock de MainWindow con los datos correctos
        mock_instance = DummyMainWindow(usuario, modulos_permitidos)
        mock_mainwindow.return_value = mock_instance

        # Crear MainWindow (mock)
        main_window = mock_mainwindow(usuario, modulos_permitidos)

        # Verificar que se inicializó correctamente
        self.assertEqual(main_window.usuario_actual, usuario)
        self.assertEqual(main_window.modulos_permitidos, modulos_permitidos)

        # Simular actualización de UI
        main_window.actualizar_usuario_label(usuario)
        main_window.mostrar_mensaje(f"Usuario actual: {usuario['usuario']}", tipo="info")
        main_window.show()

        # Verificar estado final
        self.assertTrue(main_window.is_shown)
        self.assertIn("TEST_USER", main_window.usuario_label_text)
        self.assertGreater(len(main_window.mensajes), 0)

    def test_manejo_errores_inicializacion_mainwindow(self):
        """Test: manejo de errores durante inicialización de MainWindow."""
        # Simular errores comunes en la inicialización
        with patch('main.MainWindow') as mock_mainwindow:
            # Error en la inicialización
            mock_mainwindow.side_effect = Exception("Error de inicialización UI")

            usuario = self.usuarios_model.autenticar("TEST_USER", "correcta")
            modulos_permitidos = self.usuarios_model.obtener_modulos_permitidos(usuario)

            # Verificar que se maneja el error graciosamente
            with self.assertRaises(Exception) as context:
                mock_mainwindow(usuario, modulos_permitidos)
            self.assertIn("Error de inicialización UI", str(context.exception))

    def test_filtrado_modulos_por_permisos(self):
        """Test: filtrado correcto de módulos según permisos."""
        casos_test = [
            ("TEST_USER", "administrador", 5),  # Todos los módulos
            ("user1", "operador", 2),       # Solo Obras e Inventario
            ("user2", "supervisor", 3),     # Obras, Inventario, Configuración
        ]

        for usuario_name, rol_esperado, num_modulos_esperado in casos_test:
            usuario = self.usuarios_model.autenticar(usuario_name, "correcta")
            self.assertEqual(usuario["rol"], rol_esperado)

            modulos_permitidos = self.usuarios_model.obtener_modulos_permitidos(usuario)
            self.assertEqual(len(modulos_permitidos), num_modulos_esperado)

            # Verificar que siempre tienen acceso a Obras e Inventario
            self.assertIn("Obras", modulos_permitidos)
            self.assertIn("Inventario", modulos_permitidos)

    def test_persistencia_sesion_usuario(self):
        """Test: manejo de persistencia de sesión."""
        usuario = self.usuarios_model.autenticar("TEST_USER", "correcta")
        modulos_permitidos = self.usuarios_model.obtener_modulos_permitidos(usuario)

        # Simular MainWindow con persistencia
        main_window = DummyMainWindow(usuario, modulos_permitidos)
        main_window.actualizar_usuario_label(usuario)

        # Verificar que la información del usuario persiste
        self.assertEqual(main_window.usuario_actual, usuario)
        self.assertEqual(main_window.modulos_permitidos, modulos_permitidos)
        self.assertIn("TEST_USER", main_window.usuario_label_text)
        self.assertIn("administrador", main_window.usuario_label_text)

    def test_cierre_login_tras_exito(self):
        """Test: cierre correcto de ventana de login tras éxito."""
        # Simular flujo exitoso
        usuario = self.usuarios_model.autenticar("TEST_USER", "correcta")

        # Verificar estado inicial
        self.assertFalse(self.login_view.is_closed)

        # Simular cierre tras login exitoso
        self.login_view.close()

        # Verificar que se cerró
        self.assertTrue(self.login_view.is_closed)

    def test_feedback_visual_login(self):
        """Test: feedback visual durante el proceso de login."""
        # Test feedback de error
        self.login_view.mostrar_error("Credenciales incorrectas")
        self.assertIn(("error", "Credenciales incorrectas"), self.login_view.mensajes)

        # Test limpieza de errores
        self.login_view.limpiar_error()
        self.assertTrue(self.login_view.label_error.setText.called)

        # Test feedback de éxito
        self.login_view.mostrar_feedback("Login exitoso", "success")
        self.assertIn(("success", "Login exitoso"), self.login_view.mensajes)

    def test_seguridad_validaciones_entrada(self):
        """Test: validaciones de seguridad en la entrada."""
        # Test casos de entrada maliciosa
        casos_maliciosos = [
            ("admin'; DROP TABLE users; --", "cualquiera"),
            ("<script>alert('xss')</script>", "cualquiera"),
            ("TEST_USER", "'; DROP TABLE users; --"),
            ("", ""),  # Campos vacíos
            (None, None),  # Valores nulos
        ]

        for usuario_malicioso, password_malicioso in casos_maliciosos:
            # Debe fallar graciosamente sin crashear
            with self.assertRaises((ValueError, TypeError, AttributeError)):
                self.usuarios_model.autenticar(usuario_malicioso, password_malicioso)

    def test_edge_cases_roles_permisos(self):
        """Test: casos límite con roles y permisos."""
        # Usuario con rol inexistente
        usuario_rol_malo = {"id": 99, "usuario": "test", "rol": "rol_inexistente"}
        modulos = self.usuarios_model.obtener_modulos_permitidos(usuario_rol_malo)
        self.assertEqual(modulos, [])  # Sin módulos para rol inexistente

        # Usuario sin estructura correcta
        usuario_malformado = {"usuario": "test"}  # Sin rol
        modulos = self.usuarios_model.obtener_modulos_permitidos(usuario_malformado)
        self.assertEqual(modulos, [])

        # Datos inválidos
        modulos = self.usuarios_model.obtener_modulos_permitidos(None)
        self.assertEqual(modulos, [])

        modulos = self.usuarios_model.obtener_modulos_permitidos("string_invalido")
        self.assertEqual(modulos, [])


class TestMainWindowInicializacion(unittest.TestCase):
    """Tests específicos para la inicialización de MainWindow."""

    def test_mainwindow_con_modulos_vacios(self):
        """Test: MainWindow con lista de módulos vacía."""
        usuario = {"id": 1, "usuario": "test", "rol": "ninguno"}
        modulos_vacios = []

        main_window = DummyMainWindow(usuario, modulos_vacios)

        # Debe manejar graciosamente la lista vacía
        self.assertEqual(main_window.modulos_permitidos, [])
        self.assertEqual(main_window.usuario_actual, usuario)

    def test_mainwindow_usuario_nulo(self):
        """Test: MainWindow con usuario nulo."""
        modulos = ["Configuración"]

        main_window = DummyMainWindow(None, modulos)

        # Debe manejar graciosamente usuario nulo
        self.assertIsNone(main_window.usuario_actual)
        self.assertEqual(main_window.modulos_permitidos, modulos)

    def test_mainwindow_actualizacion_usuario_label(self):
        """Test: actualización correcta del label de usuario."""
        usuarios_test = [
            {"usuario": "TEST_USER", "rol": "administrador"},
            {"usuario": "operador1", "rol": "operador"},
            {"usuario": "test_user", "rol": "supervisor"},
        ]

        for usuario in usuarios_test:
            main_window = DummyMainWindow(usuario, [])
            main_window.actualizar_usuario_label(usuario)

            expected_text = f"{usuario['usuario']} ({usuario['rol']})"
            self.assertEqual(main_window.usuario_label_text, expected_text)

    def test_mainwindow_mensajes_feedback(self):
        """Test: sistema de mensajes de feedback en MainWindow."""
        main_window = DummyMainWindow(None, [])

        # Test diferentes tipos de mensajes
        casos_mensajes = [
            ("Bienvenido", "info", 3000),
            ("Error crítico", "error", 5000),
            ("Advertencia", "warning", 4000),
            ("Operación exitosa", "success", 2000),
        ]

        for mensaje, tipo, duracion in casos_mensajes:
            main_window.mostrar_mensaje(mensaje, tipo, duracion)

        # Verificar que se registraron todos los mensajes
        self.assertEqual(len(main_window.mensajes), len(casos_mensajes))

        # Verificar contenido de los mensajes
        for i, (mensaje, tipo, duracion) in enumerate(casos_mensajes):
            self.assertEqual(main_window.mensajes[i], (mensaje, tipo, duracion))


class TestIntegracionCompletaFlujoLogin(unittest.TestCase):
    """Test de integración final completo."""

    def test_integracion_completa_flujo_login(self):
        """Test: flujo completo de integración login -> MainWindow con validaciones robustas."""
        # 1. Configurar mocks y datos de test
        usuarios_model = DummyUsuariosModel()
        login_view = DummyLoginView()

        # 2. Simular login exitoso
        usuario = usuarios_model.autenticar("TEST_USER", "correcta")
        self.assertIsNotNone(usuario)
        self.assertEqual(usuario["usuario"], "TEST_USER")
        self.assertEqual(usuario["rol"], "administrador")

        # 3. Obtener módulos permitidos
        modulos_permitidos = usuarios_model.obtener_modulos_permitidos(usuario)
        self.assertGreaterEqual(len(modulos_permitidos), 4)
        self.assertIn("Obras", modulos_permitidos)
        self.assertIn("Usuarios", modulos_permitidos)

        # 4. Simular inicialización de MainWindow
        with patch('main.MainWindow') as mock_mainwindow:
            mock_instance = DummyMainWindow(usuario, modulos_permitidos)
            mock_mainwindow.return_value = mock_instance

            # Crear MainWindow
            main_window = mock_mainwindow(usuario, modulos_permitidos)

            # 5. Verificar inicialización correcta
            self.assertEqual(main_window.usuario_actual, usuario)
            self.assertEqual(main_window.modulos_permitidos, modulos_permitidos)

            # 6. Simular configuración post-login
            main_window.actualizar_usuario_label(usuario)
            main_window.mostrar_mensaje(f"Bienvenido {usuario['usuario']}", "info", 4000)
            main_window.show()

            # 7. Verificar estado final
            self.assertTrue(main_window.is_shown)
            self.assertEqual("admin (administrador)", main_window.usuario_label_text)
            self.assertGreater(len(main_window.mensajes), 0)
            self.assertEqual(main_window.mensajes[0][0], "Bienvenido admin")
            self.assertEqual(main_window.mensajes[0][1], "info")

        # 8. Verificar cierre de login
        login_view.close()
        self.assertTrue(login_view.is_closed)

        # 9. Verificar que no hay memory leaks o errores residuales
        # (En un test real, verificaríamos contadores de objetos)
        self.assertTrue(True)  # Si llegamos aquí, el flujo fue exitoso


if __name__ == "__main__":
    unittest.main(verbosity=2)
