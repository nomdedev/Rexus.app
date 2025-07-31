import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

from rexus.modules.usuarios.model import UsuariosModel


class TestPermisosBackend(unittest.TestCase):
    """Tests para los permisos de usuarios en backend."""
    
    def test_usuarios_model_security_loaded(self):
        """Verificar que el modelo usuarios tiene seguridad cargada."""
        model = UsuariosModel()
        self.assertTrue(model.security_available)
        self.assertIsNotNone(model.data_sanitizer)
        self.assertIsNotNone(model.sql_validator)
    
    def test_usuarios_model_without_db(self):
        """Verificar que el modelo funciona sin conexión a DB."""
        model = UsuariosModel()
        self.assertIsNone(model.db_connection)
        self.assertTrue(model.security_available)
    
    def test_tabla_nombres_definidos(self):
        """Verificar que los nombres de tabla están definidos correctamente."""
        model = UsuariosModel()
        self.assertEqual(model.tabla_usuarios, "usuarios")
        self.assertEqual(model.tabla_roles, "roles")
        self.assertEqual(model.tabla_permisos, "permisos_usuario")
        self.assertEqual(model.tabla_sesiones, "sesiones_usuario")
    
    def test_roles_definidos(self):
        """Verificar que los roles están correctamente definidos."""
        expected_roles = ["ADMIN", "SUPERVISOR", "OPERADOR", "USUARIO", "INVITADO"]
        for role in expected_roles:
            self.assertIn(role, UsuariosModel.ROLES)
    
    def test_estados_definidos(self):
        """Verificar que los estados están correctamente definidos.""" 
        expected_estados = ["ACTIVO", "INACTIVO", "SUSPENDIDO", "BLOQUEADO"]
        for estado in expected_estados:
            self.assertIn(estado, UsuariosModel.ESTADOS)
    
    def test_modulos_sistema_definidos(self):
        """Verificar que los módulos del sistema están definidos."""
        expected_modules = ["Obras", "Inventario", "Herrajes", "Usuarios"]
        for module in expected_modules:
            self.assertIn(module, UsuariosModel.MODULOS_SISTEMA)


if __name__ == "__main__":
    unittest.main()
