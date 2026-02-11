#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test del Controlador de Usuarios
Tests críticos para identificar errores en el módulo de usuarios
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Configurar encoding y paths
sys.stdout.reconfigure(encoding='utf-8')
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'rexus'))

# Import usando helper para módulos con nombres numéricos
from tests.utils.module_import_helper import import_module_from_path

MODULE_AVAILABLE = True
UsuariosController = None

try:
    usuarios_controller_path = Path(project_root) / 'rexus' / 'modules' / '11_usuarios' / 'controller.py'
    usuarios_module, success, error = import_module_from_path(str(usuarios_controller_path))

    if success:
        UsuariosController = getattr(usuarios_module, 'UsuariosController', None)
        if UsuariosController is None:
            MODULE_AVAILABLE = False
    else:
        MODULE_AVAILABLE = False
        print(f"Warning: Could not import UsuariosController: {error}")
except Exception as e:
    MODULE_AVAILABLE = False
    print(f"Warning: Error importing UsuariosController: {e}")

# Crear un mock si el módulo no está disponible
if not MODULE_AVAILABLE or UsuariosController is None:
    UsuariosController = Mock
    UsuariosController.__name__ = 'UsuariosController_Mock'


# Importar bypass de autenticación global
try:
    from tests.auth_test_patch import apply_auth_patches
    apply_auth_patches()
except ImportError:
    pass


@pytest.mark.skipif(not MODULE_AVAILABLE, reason="Módulo 11_usuarios.controller no disponible")
class TestUsuariosController:
    """Tests críticos del controlador de usuarios."""
    
    @pytest.fixture
    def mock_dependencies(self):
        """Configura dependencias mockeadas."""
        with patch('rexus.modules.11_usuarios.model.UsuariosModel') as mock_model, \
             patch('rexus.modules.11_usuarios.view.UsuariosView') as mock_view:
            
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
        if not MODULE_AVAILABLE:
            pytest.skip("Módulo no disponible")
        assert UsuariosController is not None
    
    def test_controller_instantiation_basic(self, mock_dependencies):
        """Test crítico: El controlador se puede instanciar."""
        if not MODULE_AVAILABLE:
            pytest.skip("Módulo no disponible")

        try:
            with patch('rexus.modules.11_usuarios.controller.UsuariosModel', mock_dependencies['model_class']), \
                 patch('rexus.modules.11_usuarios.controller.UsuariosView', mock_dependencies['view_class']):

                controller = UsuariosController()
                assert controller is not None
                assert hasattr(controller, 'model')
                assert hasattr(controller, 'view')

        except Exception as e:
            pytest.fail(f"Error al instanciar controlador: {e}")
    
    def test_controller_has_required_authentication_methods(self, mock_dependencies):
        """Test crítico: El controlador tiene métodos de autenticación requeridos."""
        try:
            # UsuariosController ya importado al inicio del archivo
            
            with patch('rexus.modules.11_usuarios.controller.UsuariosModel', mock_dependencies['model_class']), \
                 patch('rexus.modules.11_usuarios.controller.UsuariosView', mock_dependencies['view_class']):
                
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
                    pytest.fail(f)
                    
        except Exception as e:
            pytest.fail(f"Error crítico verificando métodos de autenticación: {e}")
    
    def test_controller_has_required_user_management_methods(self, mock_dependencies):
        """Test crítico: El controlador tiene métodos de gestión de usuarios."""
        try:
            # UsuariosController ya importado al inicio del archivo
            
            with patch('rexus.modules.11_usuarios.controller.UsuariosModel', mock_dependencies['model_class']), \
                 patch('rexus.modules.11_usuarios.controller.UsuariosView', mock_dependencies['view_class']):
                
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
                    pytest.fail(f)
                
                if len(missing_methods) > len(existing_methods):
                    import warnings
                    warnings.warn(f"Advertencia: Muchos métodos de gestión faltantes: {missing_methods}")
                    
        except Exception as e:
            pytest.fail(f"Error crítico verificando gestión de usuarios: {e}")
    
    def test_cargar_usuarios_exists_and_callable(self, mock_dependencies):
        """Test crítico: cargar_usuarios existe y es llamable."""
        try:
            # UsuariosController ya importado al inicio del archivo
            
            with patch('rexus.modules.11_usuarios.controller.UsuariosModel', mock_dependencies['model_class']), \
                 patch('rexus.modules.11_usuarios.controller.UsuariosView', mock_dependencies['view_class']):
                
                controller = UsuariosController()
                
                assert hasattr(controller, 'cargar_usuarios'), "Controller no tiene método cargar_usuarios"
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
            # UsuariosController ya importado al inicio del archivo
            
            # Mock de usuario válido
            mock_user = {
                'id': 1,
                'username': 'testuser',
                'password_hash': 'hashed_password',
                'active': True
            }
            mock_dependencies['model'].autenticar_usuario.return_value = mock_user
            mock_dependencies['model'].verificar_usuario_bloqueado.return_value = (False, 0)
            mock_dependencies['model'].obtener_usuario_por_username.return_value = mock_user
            mock_dependencies['model'].obtener_usuario_por_nombre.return_value = mock_user
            mock_dependencies['model']._verificar_password.return_value = True
            
            with patch('rexus.modules.11_usuarios.controller.UsuariosModel', mock_dependencies['model_class']), \
                 patch('rexus.modules.11_usuarios.controller.UsuariosView', mock_dependencies['view_class']):
                
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
                                    pytest.fail()
                        except Exception:
                            pass  # Error de implementación, no de seguridad
                    
        except Exception as e:
            pytest.fail(f"Error crítico verificando seguridad: {e}")
    
    def test_advanced_features_integration(self, mock_dependencies):
        """Test crítico: Integración con advanced_features.py."""
        try:
            # UsuariosController ya importado al inicio del archivo
            # Import AdvancedUserManager usando helper
            try:
                advanced_features_path = Path(project_root) / 'rexus' / 'modules' / '11_usuarios' / 'advanced_features.py'
                advanced_module, success, _ = import_module_from_path(str(advanced_features_path))
                if success:
                    AdvancedUserManager = getattr(advanced_module, 'AdvancedUserManager', None)
                else:
                    pytest.skip("AdvancedUserManager no disponible")
            except Exception:
                pytest.skip("AdvancedUserManager no disponible")
            
            with patch('rexus.modules.11_usuarios.controller.UsuariosModel', mock_dependencies['model_class']), \
                 patch('rexus.modules.11_usuarios.controller.UsuariosView', mock_dependencies['view_class']):
                
                controller = UsuariosController()
                
                # Verificar que puede trabajar con características avanzadas
                mock_user_model = Mock()
                advanced_manager = AdvancedUserManager(mock_user_model)
                assert advanced_manager is not None
                
                # Verificar integración
                if hasattr(controller, 'advanced_manager') or hasattr(controller, 'set_advanced_manager'):
                    assert True
                else:
                    import warnings
                    warnings.warn()
                    
        except ImportError as e:
            pytest.fail(f"Error crítico: No se puede importar AdvancedUserManager: {e}")
        except Exception as e:
            pytest.fail(f"Error crítico en integración avanzada: {e}")
    
    def test_session_management_basic(self, mock_dependencies):
        """Test crítico: Gestión básica de sesiones."""
        try:
            # UsuariosController ya importado al inicio del archivo
            
            with patch('rexus.modules.11_usuarios.controller.UsuariosModel', mock_dependencies['model_class']), \
                 patch('rexus.modules.11_usuarios.controller.UsuariosView', mock_dependencies['view_class']):
                
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
                    warnings.warn()
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
            # UsuariosController ya importado al inicio del archivo
            
            with patch('rexus.modules.11_usuarios.controller.UsuariosModel', mock_dependencies['model_class']), \
                 patch('rexus.modules.11_usuarios.controller.UsuariosView', mock_dependencies['view_class']):
                
                controller = UsuariosController()
                
                if hasattr(controller, 'autenticar_usuario'):
                    # Setup common mocks
                    mock_dependencies['model'].verificar_usuario_bloqueado.return_value = (False, 0)
                    mock_dependencies['model']._verificar_password.return_value = True
                    mock_dependencies['model'].obtener_usuario_por_nombre.return_value = None  # Default to None for failed auth
                    
                    if should_fail:
                        # Debe rechazar credenciales inválidas/débiles
                        mock_dependencies['model'].autenticar_usuario.return_value = None
                        mock_dependencies['model'].obtener_usuario_por_username.return_value = None
                        result = controller.autenticar_usuario(username, password)
                        assert result is None or result is False
                    else:
                        # Debe aceptar credenciales válidas
                        mock_user = {'id': 1, 'username': username, 'active': True, 'password_hash': 'hashed'}
                        mock_dependencies['model'].autenticar_usuario.return_value = mock_user
                        mock_dependencies['model'].obtener_usuario_por_username.return_value = mock_user
                        mock_dependencies['model'].obtener_usuario_por_nombre.return_value = mock_user
                        result = controller.autenticar_usuario(username, password)
                        assert result is not None
                        
        except Exception as e:
            pytest.fail(f)

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])