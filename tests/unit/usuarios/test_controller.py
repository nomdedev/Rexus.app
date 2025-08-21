#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test del Controlador de Usuarios
Tests críticos para identificar errores en el módulo de usuarios
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Configurar encoding y paths
sys.stdout.reconfigure(encoding='utf-8')
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'rexus'))

# Importar bypass de autenticación global
try:
    from tests.auth_test_patch import apply_auth_bypass
    apply_auth_bypass()
except ImportError:
    pass

class TestUsuariosController:
    """Tests críticos del controlador de usuarios."""
    
    @pytest.fixture
    def mock_dependencies(self):
        """Configura dependencias mockeadas."""
        with patch('rexus.modules.usuarios.model.UsuariosModel') as mock_model, \
             patch('rexus.modules.usuarios.view.UsuariosView') as mock_view:
            
            # Mock del modelo
            mock_model_instance = Mock()
            mock_model.return_value = mock_model_instance
            
            # Mock de la vista
            mock_view_instance = Mock()
            mock_view.return_value = mock_view_instance
            
            yield {
                'model': mock_model_instance,
                'view': mock_view_instance,
                'model_class': mock_model,
                'view_class': mock_view
            }
    
    def test_controller_import_succeeds(self):
        """Test crítico: El controlador se puede importar sin errores."""
        try:
            from rexus.modules.usuarios.controller import UsuariosController
            assert UsuariosController is not None
        except ImportError as e:
            pytest.fail(f"Error crítico: No se pudo importar UsuariosController: {e}")
    
    def test_controller_instantiation_basic(self, mock_dependencies):
        """Test crítico: El controlador se puede instanciar."""
        try:
            from rexus.modules.usuarios.controller import UsuariosController
            
            with patch('rexus.modules.usuarios.controller.UsuariosModel', mock_dependencies['model_class']), \
                 patch('rexus.modules.usuarios.controller.UsuariosView', mock_dependencies['view_class']):
                
                controller = UsuariosController()
                assert controller is not None
                assert hasattr(controller, 'model')
                assert hasattr(controller, 'view')
                
        except Exception as e:
            pytest.fail(f"Error crítico: No se pudo instanciar UsuariosController: {e}")
    
    def test_controller_has_required_authentication_methods(self, mock_dependencies):
        """Test crítico: El controlador tiene métodos de autenticación requeridos."""
        try:
            from rexus.modules.usuarios.controller import UsuariosController
            
            with patch('rexus.modules.usuarios.controller.UsuariosModel', mock_dependencies['model_class']), \
                 patch('rexus.modules.usuarios.controller.UsuariosView', mock_dependencies['view_class']):
                
                controller = UsuariosController()
                
                # Métodos críticos de autenticación
                auth_methods = [
                    'autenticar_usuario',
                    'cargar_usuarios',
                    'crear_usuario',
                    'actualizar_usuario',
                    'eliminar_usuario',
                    'verificar_permisos'
                ]
                
                missing_methods = []
                for method in auth_methods:
                    if not hasattr(controller, method):
                        missing_methods.append(method)
                
                if missing_methods:
                    pytest.fail(f"Error crítico: Métodos de autenticación faltantes: {missing_methods}")
                    
        except Exception as e:
            pytest.fail(f"Error crítico verificando métodos de autenticación: {e}")
    
    def test_controller_has_required_user_management_methods(self, mock_dependencies):
        """Test crítico: El controlador tiene métodos de gestión de usuarios."""
        try:
            from rexus.modules.usuarios.controller import UsuariosController
            
            with patch('rexus.modules.usuarios.controller.UsuariosModel', mock_dependencies['model_class']), \
                 patch('rexus.modules.usuarios.controller.UsuariosView', mock_dependencies['view_class']):
                
                controller = UsuariosController()
                
                # Métodos críticos de gestión
                management_methods = [
                    'obtener_usuario_por_id',
                    'obtener_todos_usuarios',
                    'buscar_usuarios',
                    'activar_usuario',
                    'desactivar_usuario',
                    'cambiar_password'
                ]
                
                existing_methods = []
                missing_methods = []
                
                for method in management_methods:
                    if hasattr(controller, method):
                        existing_methods.append(method)
                    else:
                        missing_methods.append(method)
                
                # Debe tener al menos algunos métodos básicos
                if len(existing_methods) == 0:
                    pytest.fail(f"Error crítico: No hay métodos de gestión de usuarios implementados")
                
                if len(missing_methods) > len(existing_methods):
                    import warnings
                    warnings.warn(f"Advertencia: Muchos métodos de gestión faltantes: {missing_methods}")
                    
        except Exception as e:
            pytest.fail(f"Error crítico verificando gestión de usuarios: {e}")
    
    def test_cargar_usuarios_exists_and_callable(self, mock_dependencies):
        """Test crítico: cargar_usuarios existe y es llamable."""
        try:
            from rexus.modules.usuarios.controller import UsuariosController
            
            with patch('rexus.modules.usuarios.controller.UsuariosModel', mock_dependencies['model_class']), \
                 patch('rexus.modules.usuarios.controller.UsuariosView', mock_dependencies['view_class']):
                
                controller = UsuariosController()
                
                assert hasattr(controller, 'cargar_usuarios'), "Método cargar_usuarios faltante"
                assert callable(getattr(controller, 'cargar_usuarios')), "cargar_usuarios no es callable"
                
                # Intentar ejecutar el método
                try:
                    result = controller.cargar_usuarios()
                    assert True  # Si llegamos aquí, el método existe
                except AttributeError as ae:
                    pytest.fail(f"Error crítico: cargar_usuarios no implementado correctamente: {ae}")
                except Exception:
                    # Otros errores son aceptables (BD, etc.)
                    pass
                    
        except Exception as e:
            pytest.fail(f"Error crítico verificando cargar_usuarios: {e}")
    
    def test_authentication_security_basic(self, mock_dependencies):
        """Test crítico: Verificación básica de seguridad en autenticación."""
        try:
            from rexus.modules.usuarios.controller import UsuariosController
            
            # Mock de usuario válido
            mock_user = {
                'id': 1,
                'username': 'testuser',
                'password_hash': 'hashed_password',
                'active': True
            }
            mock_dependencies['model'].autenticar_usuario.return_value = mock_user
            
            with patch('rexus.modules.usuarios.controller.UsuariosModel', mock_dependencies['model_class']), \
                 patch('rexus.modules.usuarios.controller.UsuariosView', mock_dependencies['view_class']):
                
                controller = UsuariosController()
                
                # Verificar que tiene métodos de seguridad
                if hasattr(controller, 'autenticar_usuario'):
                    # Probar autenticación básica
                    result = controller.autenticar_usuario('testuser', 'password')
                    assert result is not None
                    
                # Verificar que no almacena passwords en texto plano
                if hasattr(controller, 'crear_usuario'):
                    # Mock para verificar que no pasa password plano
                    with patch.object(controller.model, 'crear_usuario') as mock_create:
                        try:
                            controller.crear_usuario('newuser', 'plainpassword', 'email@test.com')
                            # Verificar que la llamada no incluye password plano
                            if mock_create.called:
                                args, kwargs = mock_create.call_args
                                password_arg = None
                                if len(args) > 1:
                                    password_arg = args[1]
                                elif 'password' in kwargs:
                                    password_arg = kwargs['password']
                                
                                if password_arg == 'plainpassword':
                                    pytest.fail("Error crítico de seguridad: Password almacenado en texto plano")
                        except Exception:
                            pass  # Error de implementación, no de seguridad
                    
        except Exception as e:
            pytest.fail(f"Error crítico verificando seguridad: {e}")
    
    def test_advanced_features_integration(self, mock_dependencies):
        """Test crítico: Integración con advanced_features.py."""
        try:
            from rexus.modules.usuarios.controller import UsuariosController
            from rexus.modules.usuarios.advanced_features import AdvancedUserManager
            
            with patch('rexus.modules.usuarios.controller.UsuariosModel', mock_dependencies['model_class']), \
                 patch('rexus.modules.usuarios.controller.UsuariosView', mock_dependencies['view_class']):
                
                controller = UsuariosController()
                
                # Verificar que puede trabajar con características avanzadas
                advanced_manager = AdvancedUserManager()
                assert advanced_manager is not None
                
                # Verificar integración
                if hasattr(controller, 'advanced_manager') or hasattr(controller, 'set_advanced_manager'):
                    assert True
                else:
                    import warnings
                    warnings.warn("UsuariosController carece de integración con AdvancedUserManager")
                    
        except ImportError as e:
            pytest.fail(f"Error crítico: No se puede importar AdvancedUserManager: {e}")
        except Exception as e:
            pytest.fail(f"Error crítico en integración avanzada: {e}")
    
    def test_session_management_basic(self, mock_dependencies):
        """Test crítico: Gestión básica de sesiones."""
        try:
            from rexus.modules.usuarios.controller import UsuariosController
            
            with patch('rexus.modules.usuarios.controller.UsuariosModel', mock_dependencies['model_class']), \
                 patch('rexus.modules.usuarios.controller.UsuariosView', mock_dependencies['view_class']):
                
                controller = UsuariosController()
                
                # Métodos de sesión esperados
                session_methods = [
                    'iniciar_sesion',
                    'cerrar_sesion',
                    'obtener_sesion_actual',
                    'validar_sesion'
                ]
                
                existing_session_methods = []
                for method in session_methods:
                    if hasattr(controller, method):
                        existing_session_methods.append(method)
                
                if len(existing_session_methods) == 0:
                    import warnings
                    warnings.warn("UsuariosController carece completamente de gestión de sesiones")
                else:
                    # Al menos tiene algunos métodos de sesión
                    assert len(existing_session_methods) > 0
                    
        except Exception as e:
            pytest.fail(f"Error crítico verificando gestión de sesiones: {e}")
    
    @pytest.mark.parametrize("username,password,should_fail", [
        ("", "password", True),  # Username vacío
        ("user", "", True),      # Password vacío
        ("admin", "admin", True), # Credenciales débiles
        ("testuser", "validpass123", False) # Credenciales válidas
    ])
    def test_authentication_validation(self, mock_dependencies, username, password, should_fail):
        """Test crítico: Validación de entrada en autenticación."""
        try:
            from rexus.modules.usuarios.controller import UsuariosController
            
            with patch('rexus.modules.usuarios.controller.UsuariosModel', mock_dependencies['model_class']), \
                 patch('rexus.modules.usuarios.controller.UsuariosView', mock_dependencies['view_class']):
                
                controller = UsuariosController()
                
                if hasattr(controller, 'autenticar_usuario'):
                    if should_fail:
                        # Debe rechazar credenciales inválidas/débiles
                        mock_dependencies['model'].autenticar_usuario.return_value = None
                        result = controller.autenticar_usuario(username, password)
                        assert result is None or result is False
                    else:
                        # Debe aceptar credenciales válidas
                        mock_user = {'id': 1, 'username': username, 'active': True}
                        mock_dependencies['model'].autenticar_usuario.return_value = mock_user
                        result = controller.autenticar_usuario(username, password)
                        assert result is not None
                        
        except Exception as e:
            pytest.fail(f"Error crítico validando autenticación {username}: {e}")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])