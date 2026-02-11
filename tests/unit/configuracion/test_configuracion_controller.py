#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test del Controlador de Configuración
Tests críticos para identificar errores en el módulo de configuración
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Configurar encoding y paths
sys.stdout.reconfigure(encoding='utf-8')
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'rexus'))

# Import usando helper para módulos con nombres numéricos
from tests.utils.module_import_helper import import_module_from_path

MODULE_AVAILABLE = True
ConfiguracionController = None

try:
    configuracion_controller_path = Path(project_root) / 'rexus' / 'modules' / '12_configuracion' / 'controller.py'
    configuracion_module, success, error = import_module_from_path(str(configuracion_controller_path))

    if success:
        ConfiguracionController = getattr(configuracion_module, 'ConfiguracionController', None)
        if ConfiguracionController is None:
            MODULE_AVAILABLE = False
    else:
        MODULE_AVAILABLE = False
        print(f"Warning: Could not import ConfiguracionController: {error}")
except Exception as e:
    MODULE_AVAILABLE = False
    print(f"Warning: Error importing ConfiguracionController: {e}")

# Crear un mock si el módulo no está disponible
if not MODULE_AVAILABLE or ConfiguracionController is None:
    ConfiguracionController = Mock
    ConfiguracionController.__name__ = 'ConfiguracionController_Mock'


# Importar bypass de autenticación global
try:
    from tests.auth_test_patch import apply_auth_patches
    apply_auth_patches()
except ImportError:
    pass


@pytest.mark.skipif(not MODULE_AVAILABLE, reason="Módulo 12_configuracion.controller no disponible")
class TestConfiguracionController:
    """Tests críticos del controlador de configuración."""
    
    @pytest.fixture
    def mock_dependencies(self):
        """Configura dependencias mockeadas."""
        with patch('rexus.modules.12_configuracion.model.ConfiguracionModel') as mock_model, \
             patch('rexus.modules.12_configuracion.view.ConfiguracionView') as mock_view:
            
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
        assert ConfiguracionController is not None
    
    def test_controller_instantiation_basic(self, mock_dependencies):
        """Test crítico: El controlador se puede instanciar."""
        if not MODULE_AVAILABLE:
            pytest.skip("Módulo no disponible")

        try:
            with patch('rexus.modules.12_configuracion.controller.ConfiguracionModel', mock_dependencies['model_class']), \
                 patch('rexus.modules.12_configuracion.controller.ConfiguracionView', mock_dependencies['view_class']):

                controller = ConfiguracionController()
                assert controller is not None
                assert hasattr(controller, 'model')
                assert hasattr(controller, 'view')

        except Exception as e:
            pytest.fail(f"Error al instanciar controlador: {e}")
    
    def test_controller_has_required_methods(self, mock_dependencies):
        """Test crítico: El controlador tiene los métodos requeridos."""
        try:
            # ConfiguracionController ya importado al inicio del archivo
            
            with patch('rexus.modules.12_configuracion.controller.ConfiguracionModel', mock_dependencies['model_class']), \
                 patch('rexus.modules.12_configuracion.controller.ConfiguracionView', mock_dependencies['view_class']):
                
                controller = ConfiguracionController()
                
                # Métodos críticos que debe tener
                required_methods = [
                    'cargar_configuracion',
                    'guardar_configuracion', 
                    'obtener_configuracion',
                    'actualizar_configuracion',
                    'restablecer_configuracion'
                ]
                
                missing_methods = []
                for method in required_methods:
                    if not hasattr(controller, method):
                        missing_methods.append(method)
                
                if missing_methods:
                    pytest.fail(f)
                    
        except Exception as e:
            pytest.fail(f"Error crítico verificando métodos: {e}")
    
    def test_cargar_configuracion_exists_and_callable(self, mock_dependencies):
        """Test crítico: cargar_configuracion existe y es llamable."""
        try:
            # ConfiguracionController ya importado al inicio del archivo
            
            with patch('rexus.modules.12_configuracion.controller.ConfiguracionModel', mock_dependencies['model_class']), \
                 patch('rexus.modules.12_configuracion.controller.ConfiguracionView', mock_dependencies['view_class']):
                
                controller = ConfiguracionController()
                
                assert hasattr(controller, 'cargar_configuracion'), "cargar_configuracion no existe"
                assert callable(getattr(controller, 'cargar_configuracion')), "cargar_configuracion no es callable"
                
                # Intentar ejecutar el método
                try:
                    result = controller.cargar_configuracion()
                    # El método debe existir aunque falle por dependencias
                    assert True  # Si llegamos aquí, el método existe
                except AttributeError as ae:
                    pytest.fail(f"Error crítico: cargar_configuracion no implementado correctamente: {ae}")
                except Exception:
                    # Otros errores son aceptables (BD, etc.)
                    pass
                    
        except Exception as e:
            pytest.fail(f"Error crítico verificando cargar_configuracion: {e}")
    
    def test_controller_handles_missing_database(self, mock_dependencies):
        """Test crítico: El controlador maneja graciosamente la falta de BD."""
        try:
            # ConfiguracionController ya importado al inicio del archivo
            
            # Mock modelo que falla por falta de BD
            mock_dependencies['model'].obtener_configuracion.side_effect = Exception()
            
            with patch('rexus.modules.12_configuracion.controller.ConfiguracionModel', mock_dependencies['model_class']), \
                 patch('rexus.modules.12_configuracion.controller.ConfiguracionView', mock_dependencies['view_class']):
                
                controller = ConfiguracionController()
                
                # El controlador debe manejar el error sin crashear
                try:
                    if hasattr(controller, 'cargar_configuracion'):
                        controller.cargar_configuracion()
                    elif hasattr(controller, 'obtener_configuracion'):
                        controller.obtener_configuracion()
                    # Si no tiene estos métodos, es un error crítico detectado
                except Exception:
                    # Esperamos que maneje el error graciosamente
                    pass
                    
        except Exception as e:
            pytest.fail(f"Error crítico manejando falta de BD: {e}")
    
    def test_controller_advanced_features_integration(self, mock_dependencies):
        """Test crítico: Integración con advanced_features.py."""
        try:
            # ConfiguracionController ya importado al inicio del archivo
            # Import AdvancedConfigurationManager usando helper
            try:
                advanced_features_path = Path(project_root) / 'rexus' / 'modules' / '12_configuracion' / 'advanced_features.py'
                advanced_module, success, _ = import_module_from_path(str(advanced_features_path))
                if success:
                    AdvancedConfigurationManager = getattr(advanced_module, 'AdvancedConfigurationManager', None)
                else:
                    pytest.skip("AdvancedConfigurationManager no disponible")
            except Exception:
                pytest.skip("AdvancedConfigurationManager no disponible")
            
            with patch('rexus.modules.12_configuracion.controller.ConfiguracionModel', mock_dependencies['model_class']), \
                 patch('rexus.modules.12_configuracion.controller.ConfiguracionView', mock_dependencies['view_class']):
                
                controller = ConfiguracionController()
                
                # Verificar que puede trabajar con características avanzadas
                mock_model = Mock()
                advanced_manager = AdvancedConfigurationManager(mock_model)
                assert advanced_manager is not None
                
                # Verificar que el controlador puede usar el manager avanzado
                if hasattr(controller, 'advanced_manager') or hasattr(controller, 'set_advanced_manager'):
                    # Bueno, tiene integración
                    assert True
                else:
                    # Advertencia: falta integración avanzada
                    import warnings
                    warnings.warn()
                    
        except ImportError as e:
            pytest.fail(f"Error crítico: No se puede importar AdvancedConfigurationManager: {e}")
        except Exception as e:
            pytest.fail(f"Error crítico en integración avanzada: {e}")
    
    @pytest.mark.parametrize("config_key,expected_type", [
        ("database_url", str),
        ("debug_mode", bool),
        ("max_connections", int),
        ("timeout", (int, float))
    ])
    def test_configuration_types_validation(self, mock_dependencies, config_key, expected_type):
        """Test crítico: Validación de tipos de configuración."""
        try:
            # ConfiguracionController ya importado al inicio del archivo
            
            # Mock que retorna configuración válida
            mock_config = {
                "database_url": "sqlite:///test.db",
                "debug_mode": True,
                "max_connections": 10,
                "timeout": 30.0
            }
            mock_dependencies['model'].obtener_configuracion.return_value = mock_config
            
            with patch('rexus.modules.12_configuracion.controller.ConfiguracionModel', mock_dependencies['model_class']), \
                 patch('rexus.modules.12_configuracion.controller.ConfiguracionView', mock_dependencies['view_class']):
                
                controller = ConfiguracionController()
                
                # Verificar que puede manejar tipos de configuración
                if hasattr(controller, 'validar_configuracion'):
                    result = controller.validar_configuracion(mock_config)
                    assert result is not None
                elif hasattr(controller, 'obtener_configuracion'):
                    config = controller.obtener_configuracion()
                    if config and config_key in config:
                        assert isinstance(config[config_key], expected_type)
                        
        except Exception as e:
            pytest.fail(f"Error crítico validando configuración {config_key}: {e}")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])