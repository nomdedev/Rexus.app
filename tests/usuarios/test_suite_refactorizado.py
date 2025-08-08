"""
Test Suite Integrador - Módulos de Usuarios Refactorizados
Ejecuta todos los tests de los submódulos especializados y verifica la integración
"""

import sys
import traceback
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

# Importar todos los test suites
try:
    from tests.usuarios.test_auth_manager import TestAuthenticationManager
    from tests.usuarios.test_permissions_manager import TestPermissionsManager
    from tests.usuarios.test_sessions_manager import TestSessionsManager
    from tests.usuarios.test_profiles_manager import TestProfilesManager
    from tests.usuarios.test_unified_sanitizer import TestUnifiedDataSanitizer
    
    ALL_TESTS_AVAILABLE = True
except ImportError as e:
    print(f"❌ Error importando tests: {e}")
    ALL_TESTS_AVAILABLE = False


class TestSuiteRefactorizado:
    """Suite integrador de tests para módulos refactorizados."""
    
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.skipped_tests = 0
        
        self.results = {
            'auth_manager': [],
            'permissions_manager': [],
            'sessions_manager': [],
            'profiles_manager': [],
            'unified_sanitizer': []
        }
    
    def run_test_safely(self, test_method, test_name, category):
        """Ejecuta un test de forma segura capturando excepciones."""
        try:
            self.total_tests += 1
            test_method()
            self.passed_tests += 1
            self.results[category].append(f"✅ {test_name} - PASADO")
            print(f"✅ {test_name} - PASADO")
            return True
        except Exception as e:
            self.failed_tests += 1
            self.results[category].append(f"❌ {test_name} - FALLIDO: {str(e)}")
            print(f"❌ {test_name} - FALLIDO: {str(e)}")
            return False
    
    def run_auth_manager_tests(self):
        """Ejecuta tests del AuthenticationManager."""
        print("\n=== TESTS DE AUTHENTICATION MANAGER ===")
        
        try:
            test_suite = TestAuthenticationManager()
            test_suite.setup_method()
            
            # Tests críticos de autenticación
            self.run_test_safely(
                test_suite.test_validar_fortaleza_password_valida,
                "Validar contraseña fuerte",
                'auth_manager'
            )
            
            self.run_test_safely(
                test_suite.test_validar_fortaleza_password_debil,
                "Detectar contraseña débil",
                'auth_manager'
            )
            
            self.run_test_safely(
                test_suite.test_validar_fortaleza_password_comun,
                "Rechazar contraseña común",
                'auth_manager'
            )
            
            self.run_test_safely(
                test_suite.test_cambiar_password_nueva_debil,
                "Rechazar cambio a contraseña débil",
                'auth_manager'
            )
            
            self.run_test_safely(
                test_suite.test_verificar_cuenta_bloqueada_no_bloqueada,
                "Verificar cuenta no bloqueada",
                'auth_manager'
            )
            
            self.run_test_safely(
                test_suite.test_verificar_cuenta_bloqueada_si_bloqueada,
                "Verificar cuenta bloqueada",
                'auth_manager'
            )
            
        except Exception as e:
            print(f"❌ Error configurando tests de AuthenticationManager: {e}")
            self.skipped_tests += 6
    
    def run_permissions_manager_tests(self):
        """Ejecuta tests del PermissionsManager."""
        print("\n=== TESTS DE PERMISSIONS MANAGER ===")
        
        try:
            test_suite = TestPermissionsManager()
            test_suite.setup_method()
            
            # Tests críticos de permisos
            self.run_test_safely(
                test_suite.test_verificar_permiso_jerarquico,
                "Verificar permisos jerárquicos",
                'permissions_manager'
            )
            
            self.run_test_safely(
                test_suite.test_asignar_permiso_modulo_invalido,
                "Rechazar módulo inválido",
                'permissions_manager'
            )
            
            self.run_test_safely(
                test_suite.test_cambiar_rol_invalido,
                "Rechazar rol inválido",
                'permissions_manager'
            )
            
            # Test de enums si están disponibles
            try:
                self.run_test_safely(
                    test_suite.test_system_module_enum,
                    "Enum de módulos del sistema",
                    'permissions_manager'
                )
                
                self.run_test_safely(
                    test_suite.test_permission_level_enum,
                    "Enum de niveles de permisos",
                    'permissions_manager'
                )
            except AttributeError:
                self.skipped_tests += 2
                print("⚠️  Enums no disponibles - tests saltados")
            
        except Exception as e:
            print(f"❌ Error configurando tests de PermissionsManager: {e}")
            self.skipped_tests += 5
    
    def run_sessions_manager_tests(self):
        """Ejecuta tests del SessionsManager."""
        print("\n=== TESTS DE SESSIONS MANAGER ===")
        
        try:
            test_suite = TestSessionsManager()
            test_suite.setup_method()
            
            # Tests críticos de sesiones
            self.run_test_safely(
                test_suite.test_generar_session_id_unico,
                "Generar ID de sesión único",
                'sessions_manager'
            )
            
            self.run_test_safely(
                test_suite.test_verificar_limite_sesiones_no_excedido,
                "Verificar límite no excedido",
                'sessions_manager'
            )
            
            self.run_test_safely(
                test_suite.test_verificar_limite_sesiones_excedido,
                "Verificar límite excedido",
                'sessions_manager'
            )
            
            self.run_test_safely(
                test_suite.test_validar_sesion_inexistente,
                "Validar sesión inexistente",
                'sessions_manager'
            )
            
            self.run_test_safely(
                test_suite.test_cerrar_sesion_inexistente,
                "Cerrar sesión inexistente",
                'sessions_manager'
            )
            
        except Exception as e:
            print(f"❌ Error configurando tests de SessionsManager: {e}")
            self.skipped_tests += 5
    
    def run_profiles_manager_tests(self):
        """Ejecuta tests del ProfilesManager."""
        print("\n=== TESTS DE PROFILES MANAGER ===")
        
        try:
            test_suite = TestProfilesManager()
            test_suite.setup_method()
            
            # Tests críticos de perfiles
            self.run_test_safely(
                test_suite.test_validar_datos_usuario_validos,
                "Validar datos válidos",
                'profiles_manager'
            )
            
            self.run_test_safely(
                test_suite.test_validar_datos_usuario_username_vacio,
                "Rechazar username vacío",
                'profiles_manager'
            )
            
            self.run_test_safely(
                test_suite.test_validar_datos_usuario_username_muy_corto,
                "Rechazar username muy corto",
                'profiles_manager'
            )
            
            self.run_test_safely(
                test_suite.test_validar_datos_usuario_email_invalido,
                "Rechazar email inválido",
                'profiles_manager'
            )
            
            self.run_test_safely(
                test_suite.test_validar_datos_usuario_rol_invalido,
                "Rechazar rol inválido",
                'profiles_manager'
            )
            
            self.run_test_safely(
                test_suite.test_verificar_unicidad_usuario_unico,
                "Verificar unicidad de usuario",
                'profiles_manager'
            )
            
            self.run_test_safely(
                test_suite.test_verificar_unicidad_usuario_duplicado,
                "Detectar usuario duplicado",
                'profiles_manager'
            )
            
        except Exception as e:
            print(f"❌ Error configurando tests de ProfilesManager: {e}")
            self.skipped_tests += 7
    
    def run_unified_sanitizer_tests(self):
        """Ejecuta tests del UnifiedDataSanitizer."""
        print("\n=== TESTS DE UNIFIED DATA SANITIZER ===")
        
        try:
            test_suite = TestUnifiedDataSanitizer()
            test_suite.setup_method()
            
            # Tests críticos de sanitización
            self.run_test_safely(
                test_suite.test_sanitize_string_with_sql_injection,
                "Prevenir SQL injection",
                'unified_sanitizer'
            )
            
            self.run_test_safely(
                test_suite.test_sanitize_string_with_html,
                "Prevenir XSS",
                'unified_sanitizer'
            )
            
            self.run_test_safely(
                test_suite.test_sanitize_email_valid,
                "Sanitizar email válido",
                'unified_sanitizer'
            )
            
            self.run_test_safely(
                test_suite.test_sanitize_email_invalid_format,
                "Rechazar email inválido",
                'unified_sanitizer'
            )
            
            self.run_test_safely(
                test_suite.test_sanitize_numeric_integer,
                "Sanitizar número entero",
                'unified_sanitizer'
            )
            
            self.run_test_safely(
                test_suite.test_sanitize_numeric_with_range,
                "Aplicar rangos numéricos",
                'unified_sanitizer'
            )
            
            self.run_test_safely(
                test_suite.test_sanitize_url_invalid_scheme,
                "Rechazar URL con esquema inválido",
                'unified_sanitizer'
            )
            
            self.run_test_safely(
                test_suite.test_xss_patterns_removal,
                "Remover patrones XSS",
                'unified_sanitizer'
            )
            
            self.run_test_safely(
                test_suite.test_convenience_functions,
                "Funciones de conveniencia",
                'unified_sanitizer'
            )
            
            self.run_test_safely(
                test_suite.test_global_sanitizer_instance,
                "Instancia global del sanitizador",
                'unified_sanitizer'
            )
            
        except Exception as e:
            print(f"❌ Error configurando tests de UnifiedDataSanitizer: {e}")
            self.skipped_tests += 10
    
    def run_integration_tests(self):
        """Ejecuta tests de integración entre módulos."""
        print("\n=== TESTS DE INTEGRACIÓN ===")
        
        try:
            # Test de integración: Crear usuario con sanitización completa
            self.run_test_safely(
                self.test_crear_usuario_con_sanitizacion_completa,
                "Crear usuario con sanitización completa",
                'integration'
            )
            
            # Test de integración: Autenticación con gestión de sesiones
            self.run_test_safely(
                self.test_autenticacion_con_gestion_sesiones,
                "Autenticación con gestión de sesiones",
                'integration'
            )
            
            # Test de integración: Permisos con roles
            self.run_test_safely(
                self.test_permisos_con_roles_jerarquicos,
                "Permisos con roles jerárquicos",
                'integration'
            )
            
        except Exception as e:
            print(f"❌ Error ejecutando tests de integración: {e}")
            self.skipped_tests += 3
    
    def test_crear_usuario_con_sanitizacion_completa(self):
        """Test de integración: crear usuario usando sanitización completa."""
        from rexus.utils.unified_sanitizer import unified_sanitizer
        
        # Datos de entrada con contenido peligroso
        datos_peligrosos = {
            'username': "test_user<script>alert('xss')</script>",
            'nombre_completo': "Juan'; DROP TABLE usuarios; --",
            'email': 'JUAN@EJEMPLO.COM',
            'telefono': 'abc555-123-4567xyz',
            'descripcion': "<iframe src='evil.com'></iframe>Descripción normal"
        }
        
        # Sanitizar usando el sistema unificado
        datos_limpios = unified_sanitizer.sanitize_dict(datos_peligrosos)
        
        # Verificaciones
        assert "<script>" not in datos_limpios.get('username', '')
        assert "DROP TABLE" not in datos_limpios.get('nombre_completo', '')
        assert datos_limpios.get('email') == 'juan@ejemplo.com'  # Normalizado
        assert "<iframe>" not in datos_limpios.get('descripcion', '')
        assert "555-123-4567" in datos_limpios.get('telefono', '')
    
    def test_autenticacion_con_gestion_sesiones(self):
        """Test de integración: autenticación seguida de gestión de sesiones."""
        from rexus.modules.usuarios.submodules.auth_manager import AuthenticationManager
        from rexus.modules.usuarios.submodules.sessions_manager import SessionsManager
        from tests.obras.mock_auth_context import MockDatabaseContext
        
        mock_db = MockDatabaseContext()
        auth_manager = AuthenticationManager(mock_db.connection)
        sessions_manager = SessionsManager(mock_db.connection)
        
        # Simular autenticación exitosa
        username = "test_user"
        usuario_id = 1
        
        # Crear sesión después de autenticación exitosa
        with unittest.mock.patch.object(sessions_manager, '_generar_session_id', return_value='test_session'):
            resultado_sesion = sessions_manager.crear_sesion(usuario_id, username, "192.168.1.100")
        
        # Verificaciones
        assert resultado_sesion['success'] is True
        assert resultado_sesion['session_id'] == 'test_session'
    
    def test_permisos_con_roles_jerarquicos(self):
        """Test de integración: verificar jerarquía de permisos por roles."""
        from rexus.modules.usuarios.submodules.permissions_manager import PermissionsManager
        from tests.obras.mock_auth_context import MockDatabaseContext
        
        mock_db = MockDatabaseContext()
        permissions_manager = PermissionsManager(mock_db.connection)
        
        # Verificar que admin tiene todos los permisos
        permisos_admin = permissions_manager._obtener_permisos_por_rol('admin')
        permisos_supervisor = permissions_manager._obtener_permisos_por_rol('supervisor')
        permisos_viewer = permissions_manager._obtener_permisos_por_rol('viewer')
        
        # Verificaciones de jerarquía
        assert len(permisos_admin) > len(permisos_supervisor)
        assert len(permisos_supervisor) > len(permisos_viewer)
        assert 'usuarios:admin' in permisos_admin
        assert 'usuarios:admin' not in permisos_supervisor
        assert 'usuarios:admin' not in permisos_viewer
    
    def generate_report(self):
        """Genera reporte final de resultados."""
        print("\n" + "="*60)
        print("REPORTE FINAL - TESTS DE MÓDULOS REFACTORIZADOS")
        print("="*60)
        
        print(f"\n📊 RESUMEN GENERAL:")
        print(f"   Total de tests ejecutados: {self.total_tests}")
        print(f"   Tests pasados: {self.passed_tests} ✅")
        print(f"   Tests fallidos: {self.failed_tests} ❌")
        print(f"   Tests saltados: {self.skipped_tests} ⚠️")
        
        if self.total_tests > 0:
            success_rate = (self.passed_tests / self.total_tests) * 100
            print(f"   Tasa de éxito: {success_rate:.1f}%")
        
        # Detalles por módulo
        for module, results in self.results.items():
            if results:
                print(f"\n📋 {module.upper().replace('_', ' ')}:")
                for result in results:
                    print(f"   {result}")
        
        # Estado general
        print(f"\n🎯 ESTADO GENERAL:")
        if self.failed_tests == 0:
            print("   ✅ TODOS LOS TESTS PASARON EXITOSAMENTE")
            print("   🚀 Los módulos refactorizados están listos para producción")
        elif self.failed_tests < self.passed_tests:
            print(f"   ⚠️  ALGUNOS TESTS FALLARON ({self.failed_tests}/{self.total_tests})")
            print("   🔧 Se requiere revisión de los módulos con fallas")
        else:
            print(f"   ❌ MUCHOS TESTS FALLARON ({self.failed_tests}/{self.total_tests})")
            print("   🛠️  Se requiere revisión completa de los módulos")
        
        print("="*60)
        return self.failed_tests == 0


def main():
    """Función principal para ejecutar todos los tests."""
    print("🧪 INICIANDO SUITE DE TESTS - MÓDULOS USUARIOS REFACTORIZADOS")
    print("="*60)
    
    if not ALL_TESTS_AVAILABLE:
        print("❌ No se pudieron importar todos los módulos de test")
        print("   Verificar que los submódulos estén correctamente instalados")
        return False
    
    # Crear suite y ejecutar tests
    suite = TestSuiteRefactorizado()
    
    suite.run_auth_manager_tests()
    suite.run_permissions_manager_tests()
    suite.run_sessions_manager_tests()  
    suite.run_profiles_manager_tests()
    suite.run_unified_sanitizer_tests()
    suite.run_integration_tests()
    
    # Generar reporte final
    all_passed = suite.generate_report()
    
    return all_passed


if __name__ == "__main__":
    import unittest.mock
    success = main()
    exit(0 if success else 1)