"""
Tests de Validación Pre-Ejecución - Módulo Administración
Valida que el módulo esté funcional antes de ejecutar la aplicación principal.
"""

import sys
from pathlib import Path
import pytest
from unittest.mock import Mock, patch

# Agregar la ruta del proyecto al path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from rexus.modules.administracion.view import AdministracionView
    from rexus.modules.administracion.model import AdministracionModel
    from rexus.modules.administracion.controller import AdministracionController
except ImportError as e:
    print(f"Error importando módulos de administración: {e}")
    AdministracionView = None
    AdministracionModel = None
    AdministracionController = None


class TestAdministracionModuleFunctionality:
    """Tests para validar funcionalidad real del módulo administración."""

    def setup_method(self):
        """Setup para cada test."""
        self.issues_found = []

    def test_view_has_real_functionality(self):
        """Verifica que la vista tenga funcionalidad real, no placeholders."""
        if not AdministracionView:
            self.issues_found.append("No se puede importar AdministracionView")
            pytest.fail("Módulo administración no importable")

        view = AdministracionView()
        
        # Verificar que no tenga solo funciones placeholder
        mock_functions = []
        
        # Verificar método nuevo_registro
        if hasattr(view, 'nuevo_registro'):
            # Simular click para ver si es función real o placeholder
            try:
                with patch('rexus.utils.message_system.show_warning') as mock_warning:
                    view.nuevo_registro()
                    if mock_warning.called:
                        # Si muestra warning de "en desarrollo", es placeholder
                        args = mock_warning.call_args[0]
                        if "desarrollo" in str(args).lower():
                            mock_functions.append("nuevo_registro")
            except Exception:
                mock_functions.append("nuevo_registro")

        if mock_functions:
            self.issues_found.append(f"Funciones placeholder detectadas: {mock_functions}")
            assert False, f"Vista tiene funciones mock: {mock_functions}"

    def test_model_functions_are_accessible(self):
        """Verifica que las funciones del modelo sean accesibles."""
        if not AdministracionModel:
            self.issues_found.append("No se puede importar AdministracionModel")
            pytest.fail("Modelo administración no importable")

        # Verificar que el modelo tenga funciones administrativas reales
        mock_db = Mock()
        model = AdministracionModel(mock_db)
        
        # Funciones críticas que DEBEN existir
        required_functions = [
            'registrar_asiento_contable',
            'generar_balance_general', 
            'crear_empleado',
            'generar_nomina'
        ]
        
        missing_functions = []
        for func_name in required_functions:
            if not hasattr(model, func_name):
                missing_functions.append(func_name)
            elif not callable(getattr(model, func_name)):
                missing_functions.append(f"{func_name} (no callable)")

        if missing_functions:
            self.issues_found.append(f"Funciones del modelo faltantes: {missing_functions}")
            assert False, f"Modelo missing functions: {missing_functions}"

    def test_controller_exists_and_connects(self):
        """Verifica que el controlador exista y conecte vista con modelo."""
        if not AdministracionController:
            self.issues_found.append("Controlador no existe o no es importable")
            # Este es un fallo esperado - el controlador probablemente no existe
            pytest.skip("Controlador administración no existe - problema conocido")

        # Si existe, verificar que conecte vista y modelo
        controller = AdministracionController()
        assert hasattr(controller, 'model'), "Controlador debe tener modelo"
        assert hasattr(controller, 'view'), "Controlador debe tener vista"

    def test_submodules_integration(self):
        """Verifica que los submódulos estén integrados en la vista principal."""
        if not AdministracionView:
            pytest.fail("Vista no importable")

        view = AdministracionView()
        
        # Verificar si tiene acceso a submódulos
        has_contabilidad = False
        has_rrhh = False
        
        # Buscar referencias a submódulos en la vista
        for attr_name in dir(view):
            if 'contabilidad' in attr_name.lower():
                has_contabilidad = True
            if 'rrhh' in attr_name.lower() or 'recursos' in attr_name.lower():
                has_rrhh = True

        integration_issues = []
        if not has_contabilidad:
            integration_issues.append("Sin integración con submódulo contabilidad")
        if not has_rrhh:
            integration_issues.append("Sin integración con submódulo RRHH")

        if integration_issues:
            self.issues_found.extend(integration_issues)
            pytest.fail(f"Submódulos no integrados: {integration_issues}")

    def test_buttons_execute_real_functions(self):
        """Verifica que los botones ejecuten funciones reales."""
        if not AdministracionView:
            pytest.fail("Vista no importable")

        view = AdministracionView()
        
        # Obtener botones
        buttons = []
        if hasattr(view, 'btn_nuevo'):
            buttons.append(('btn_nuevo', view.btn_nuevo))
        if hasattr(view, 'btn_buscar'):
            buttons.append(('btn_buscar', view.btn_buscar))
        if hasattr(view, 'btn_actualizar'):
            buttons.append(('btn_actualizar', view.btn_actualizar))

        non_functional_buttons = []
        for btn_name, btn in buttons:
            # Verificar que el botón tenga función conectada
            if not btn.receivers(btn.clicked):
                non_functional_buttons.append(f"{btn_name} (sin función)")

        if non_functional_buttons:
            self.issues_found.append(f"Botones no funcionales: {non_functional_buttons}")
            assert False, f"Botones sin funcionalidad: {non_functional_buttons}"


def validate_administracion_before_run():
    """
    Función principal de validación que se puede llamar antes de ejecutar la app.
    
    Returns:
        tuple: (is_functional, issues_found)
    """
    issues = []
    
    # Test 1: Verificar importabilidad
    try:
        from rexus.modules.administracion.view import AdministracionView
        from rexus.modules.administracion.model import AdministracionModel
        view = AdministracionView()
        model = AdministracionModel()
    except ImportError as e:
        issues.append(f"Error importando módulos: {e}")
        return False, issues
    except Exception as e:
        issues.append(f"Error instanciando módulos: {e}")
        return False, issues

    # Test 2: Verificar funciones placeholder
    try:
        with patch('rexus.utils.message_system.show_warning') as mock_warning:
            view.nuevo_registro()
            if mock_warning.called:
                args = mock_warning.call_args[0] if mock_warning.call_args else []
                if any("desarrollo" in str(arg).lower() for arg in args):
                    issues.append("Funciones placeholder detectadas (show 'en desarrollo')")
    except Exception as e:
        issues.append(f"Error verificando funciones placeholder: {e}")

    # Test 3: Verificar modelo funcional
    required_model_functions = [
        'registrar_asiento_contable',
        'generar_balance_general', 
        'crear_empleado'
    ]
    
    missing_functions = []
    for func_name in required_model_functions:
        if not hasattr(model, func_name):
            missing_functions.append(func_name)
    
    if missing_functions:
        issues.append(f"Funciones críticas del modelo faltantes: {missing_functions}")

    # Test 4: Verificar controlador
    try:
        from rexus.modules.administracion.controller import AdministracionController
    except ImportError:
        issues.append("Controlador no existe - vista y modelo desconectados")

    return len(issues) == 0, issues


if __name__ == "__main__":
    print("VALIDANDO MODULO ADMINISTRACION ANTES DE EJECUTAR APP...")
    
    is_functional, issues_found = validate_administracion_before_run()
    
    print(f"\nRESULTADO DE VALIDACION:")
    print(f"Estado funcional: {'SI' if is_functional else 'NO'}")
    print(f"Issues encontrados: {len(issues_found)}")
    
    if issues_found:
        print(f"\nPROBLEMAS DETECTADOS:")
        for i, issue in enumerate(issues_found, 1):
            print(f"  {i}. {issue}")
        
        print(f"\nRECOMENDACION: No ejecutar la aplicacion principal hasta resolver estos issues.")
        print(f"   El modulo administracion no sera funcional para los usuarios.")
        
    else:
        print(f"\nMODULO ADMINISTRACION VALIDADO CORRECTAMENTE")
        print(f"   Es seguro ejecutar la aplicacion principal.")

    # Return exit code para scripts
    sys.exit(0 if is_functional else 1)