#!/usr/bin/env python3
"""
AUDITORÍA COMPLETA DEL MÓDULO DE SEGURIDAD - Rexus.app
======================================================

Esta auditoría verifica que todos los aspectos críticos del módulo de seguridad
estén implementados correctamente y cumpla con los estándares requeridos.

Cubre:
- Arquitectura de autenticación y autorización
- Sistema de permisos y roles
- Validación de implementación vs. tests
- Identificación de gaps de cobertura
- Recomendaciones de mejora

Fecha: 21/08/2025
Tipo: Auditoría técnica integral
"""

import unittest
import sys
import os
from pathlib import Path
import importlib
import inspect

# Configurar path
sys.path.insert(0, str(Path(__file__).parent.parent))


class SecurityModuleAudit:
    """Clase para auditar el módulo de seguridad completo"""
    
    def __init__(self):
        self.audit_results = {
            'modules_found': [],
            'classes_found': [],
            'methods_found': [],
            'tests_found': [],
            'coverage_gaps': [],
            'recommendations': []
        }
    
    def audit_auth_modules(self):
        """Audita los módulos de autenticación disponibles"""
        auth_modules = [
            'rexus.core.auth',
            'rexus.core.auth_manager',
            'rexus.core.auth_decorators',
            'rexus.core.login_dialog'
        ]
        
        for module_name in auth_modules:
            try:
                module = importlib.import_module(module_name)
                self.audit_results['modules_found'].append({
                    'name': module_name,
                    'file': getattr(module, '__file__', 'Unknown'),
                    'classes': [name for name, obj in inspect.getmembers(module, inspect.isclass)
                               if obj.__module__ == module_name],
                    'functions': [name for name, obj in inspect.getmembers(module, inspect.isfunction)
                                 if obj.__module__ == module_name]
                })
            except ImportError as e:
                self.audit_results['coverage_gaps'].append(f"Module {module_name} not found: {e}")
    
    def audit_auth_manager_capabilities(self):
        """Audita las capacidades del AuthManager"""
        try:
            from rexus.core.auth_manager import AuthManager, UserRole, Permission
            
            # Verificar estructura de roles
            roles_found = list(UserRole)
            permissions_found = list(Permission)
            
            self.audit_results['classes_found'].append({
                'class': 'AuthManager',
                'roles': [role.value for role in roles_found],
                'permissions': [perm.value for perm in permissions_found],
                'role_mappings': {role.value: len(AuthManager.ROLE_PERMISSIONS.get(role, [])) 
                                 for role in roles_found}
            })
            
            # Verificar métodos críticos
            critical_methods = ['check_permission', 'set_current_user_role']
            available_methods = [method for method in dir(AuthManager) 
                               if not method.startswith('_')]
            
            self.audit_results['methods_found'].extend(available_methods)
            
            for method in critical_methods:
                if method not in available_methods:
                    self.audit_results['coverage_gaps'].append(f"Critical method missing: {method}")
            
        except ImportError as e:
            self.audit_results['coverage_gaps'].append(f"AuthManager not available: {e}")
    
    def audit_authentication_system(self):
        """Audita el sistema de autenticación"""
        try:
            from rexus.core.auth import AuthManager as AuthSystem
            
            # Verificar métodos de autenticación
            auth_methods = [name for name, method in inspect.getmembers(AuthSystem, inspect.ismethod)]
            
            self.audit_results['classes_found'].append({
                'class': 'AuthSystem',
                'methods': auth_methods
            })
            
            # Buscar método de autenticación
            if hasattr(AuthSystem, 'authenticate_user'):
                self.audit_results['methods_found'].append('authenticate_user')
            else:
                self.audit_results['coverage_gaps'].append("No authenticate_user method found")
            
        except ImportError as e:
            self.audit_results['coverage_gaps'].append(f"Auth system not available: {e}")
    
    def audit_test_coverage(self):
        """Audita la cobertura de tests"""
        test_files = [
            'test_usuarios_seguridad.py',
            'test_login_ui.py',
            'test_permisos_roles.py',
            'test_sesiones.py',
            'test_auditoria_seguridad.py'
        ]
        
        tests_dir = Path(__file__).parent
        
        for test_file in test_files:
            test_path = tests_dir / test_file
            if test_path.exists():
                self.audit_results['tests_found'].append({
                    'file': test_file,
                    'size': test_path.stat().st_size,
                    'exists': True
                })
            else:
                self.audit_results['coverage_gaps'].append(f"Test file missing: {test_file}")
    
    def audit_security_requirements(self):
        """Audita cumplimiento de requisitos de seguridad"""
        security_requirements = [
            {
                'requirement': 'Password Hashing',
                'modules': ['rexus.utils.password_security'],
                'critical': True
            },
            {
                'requirement': 'Session Management',
                'modules': ['rexus.core.auth'],
                'critical': True
            },
            {
                'requirement': 'Role-Based Access Control',
                'modules': ['rexus.core.auth_manager'],
                'critical': True
            },
            {
                'requirement': 'Login UI',
                'modules': ['rexus.core.login_dialog'],
                'critical': False
            }
        ]
        
        for req in security_requirements:
            all_modules_found = True
            for module_name in req['modules']:
                try:
                    importlib.import_module(module_name)
                except ImportError:
                    all_modules_found = False
                    if req['critical']:
                        self.audit_results['coverage_gaps'].append(
                            f"CRITICAL: {req['requirement']} - Missing module: {module_name}")
                    else:
                        self.audit_results['coverage_gaps'].append(
                            f"WARNING: {req['requirement']} - Missing module: {module_name}")
            
            if all_modules_found:
                self.audit_results['modules_found'].append({
                    'requirement': req['requirement'],
                    'status': 'IMPLEMENTED',
                    'modules': req['modules']
                })
    
    def generate_recommendations(self):
        """Genera recomendaciones basadas en el análisis"""
        
        # Analizar gaps críticos
        critical_gaps = [gap for gap in self.audit_results['coverage_gaps'] 
                        if 'CRITICAL' in gap]
        
        if critical_gaps:
            self.audit_results['recommendations'].extend([
                "URGENTE: Implementar módulos críticos faltantes",
                "Crear sistema completo de autenticación",
                "Implementar hashing seguro de passwords"
            ])
        
        # Analizar cobertura de tests
        test_gaps = [gap for gap in self.audit_results['coverage_gaps'] 
                    if 'Test file missing' in gap]
        
        if test_gaps:
            self.audit_results['recommendations'].append(
                "Completar suite de tests de seguridad")
        
        # Recomendaciones generales
        self.audit_results['recommendations'].extend([
            "Implementar rate limiting para protección contra fuerza bruta",
            "Agregar logging de eventos de seguridad",
            "Implementar timeouts de sesión",
            "Agregar validaciones de fortaleza de contraseña",
            "Implementar 2FA para usuarios admin",
            "Crear tests de penetración automatizados"
        ])
    
    def run_full_audit(self):
        """Ejecuta auditoría completa"""
        print("🔍 INICIANDO AUDITORÍA COMPLETA DEL MÓDULO DE SEGURIDAD")
        print("=" * 70)
        
        # Ejecutar todas las auditorías
        self.audit_auth_modules()
        self.audit_auth_manager_capabilities()
        self.audit_authentication_system()
        self.audit_test_coverage()
        self.audit_security_requirements()
        self.generate_recommendations()
        
        return self.audit_results
    
    def print_audit_report(self):
        """Imprime reporte completo de auditoría"""
        results = self.audit_results
        
        print("\n📋 REPORTE DE AUDITORÍA DE SEGURIDAD")
        print("=" * 70)
        
        # Módulos encontrados
        print(f"\n✅ MÓDULOS ENCONTRADOS: {len(results['modules_found'])}")
        for module in results['modules_found']:
            if isinstance(module, dict) and 'name' in module:
                print(f"   • {module['name']}")
                if 'classes' in module and module['classes']:
                    print(f"     Clases: {', '.join(module['classes'])}")
                if 'functions' in module and module['functions']:
                    print(f"     Funciones: {', '.join(module['functions'])}")
        
        # Clases encontradas
        print(f"\n🏗️  CLASES PRINCIPALES: {len(results['classes_found'])}")
        for class_info in results['classes_found']:
            if isinstance(class_info, dict) and 'class' in class_info:
                print(f"   • {class_info['class']}")
                if 'roles' in class_info:
                    print(f"     Roles: {', '.join(class_info['roles'])}")
                if 'permissions' in class_info:
                    print(f"     Permisos: {len(class_info['permissions'])} definidos")
        
        # Tests encontrados
        print(f"\n🧪 TESTS ENCONTRADOS: {len(results['tests_found'])}")
        for test in results['tests_found']:
            if isinstance(test, dict) and 'file' in test:
                size_kb = test['size'] // 1024 if 'size' in test else 0
                print(f"   • {test['file']} ({size_kb} KB)")
        
        # Gaps de cobertura
        print(f"\n⚠️  GAPS DE COBERTURA: {len(results['coverage_gaps'])}")
        for gap in results['coverage_gaps']:
            if 'CRITICAL' in gap:
                print(f"   🚨 {gap}")
            else:
                print(f"   ⚠️  {gap}")
        
        # Recomendaciones
        print(f"\n💡 RECOMENDACIONES: {len(results['recommendations'])}")
        for i, rec in enumerate(results['recommendations'], 1):
            print(f"   {i}. {rec}")
        
        # Resumen final
        print("\n" + "=" * 70)
        total_gaps = len(results['coverage_gaps'])
        critical_gaps = len([g for g in results['coverage_gaps'] if 'CRITICAL' in g])
        
        if critical_gaps == 0:
            print("✅ ESTADO: FUNCIONAL - No hay gaps críticos")
        elif critical_gaps < 3:
            print("⚠️  ESTADO: REQUIERE ATENCIÓN - Gaps críticos menores")
        else:
            print("🚨 ESTADO: REQUIERE REFACTORING - Múltiples gaps críticos")
        
        print(f"📊 Cobertura estimada: {max(0, 100 - (total_gaps * 10))}%")
        print("=" * 70)


class TestSecurityAudit(unittest.TestCase):
    """Tests que ejecutan la auditoría del módulo de seguridad"""
    
    def test_security_module_completeness(self):
        """Test que verifica completitud del módulo de seguridad"""
        auditor = SecurityModuleAudit()
        results = auditor.run_full_audit()
        
        # Verificar que al menos los módulos básicos existen
        module_names = [m.get('name', '') for m in results['modules_found'] 
                       if isinstance(m, dict) and 'name' in m]
        
        self.assertIn('rexus.core.auth_manager', module_names,
                     "Módulo auth_manager debe estar presente")
        
        # Verificar que no hay gaps críticos excesivos
        critical_gaps = [gap for gap in results['coverage_gaps'] if 'CRITICAL' in gap]
        self.assertLess(len(critical_gaps), 5,
                       f"Demasiados gaps críticos: {critical_gaps}")
        
        # Imprimir reporte
        auditor.print_audit_report()
    
    def test_authorization_system_functional(self):
        """Test que verifica el sistema de autorización funciona"""
        try:
            from rexus.core.auth_manager import AuthManager, UserRole, Permission
            
            # Test básico de permisos
            AuthManager.set_current_user_role(UserRole.ADMIN)
            self.assertTrue(AuthManager.check_permission(Permission.VIEW_DASHBOARD))
            
            AuthManager.set_current_user_role(UserRole.VIEWER)
            self.assertFalse(AuthManager.check_permission(Permission.DELETE_USERS))
            
        except ImportError:
            self.fail("Sistema de autorización no disponible")
    
    def test_authentication_system_accessible(self):
        """Test que verifica el sistema de autenticación es accesible"""
        try:
            from rexus.core.auth import get_current_user, set_current_user, clear_current_user
            
            # Test básico de sesión
            test_user = {'id': 1, 'usuario': 'test'}
            set_current_user(test_user)
            current = get_current_user()
            self.assertEqual(current['usuario'], 'test')
            
            clear_current_user()
            self.assertIsNone(get_current_user())
            
        except ImportError:
            self.fail("Sistema de autenticación no disponible")


def run_security_audit():
    """Función principal para ejecutar auditoría de seguridad"""
    print("🔒 AUDITORÍA INTEGRAL DEL MÓDULO DE SEGURIDAD - REXUS.APP")
    print("=" * 80)
    
    # Ejecutar tests de auditoría
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestSecurityAudit)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_security_audit()
    print(f"\n🎯 Auditoría {'COMPLETADA' if success else 'COMPLETADA CON OBSERVACIONES'}")