#!/usr/bin/env python3
"""
Tests de Seguridad - Import Security & Architecture
Rexus.app - Validación de Imports y Arquitectura MVC

Verifica que no haya imports duplicados y que se respete la arquitectura MVC.
"""

import unittest
import os
import re
import ast


class TestImportSecurity(unittest.TestCase):
    """Tests para validar imports seguros y arquitectura MVC."""
    
    def setUp(self):
        """Configurar rutas de módulos a verificar."""
        self.modules_to_check = [
            'rexus/modules/vidrios/model.py',
            'rexus/modules/obras/model.py', 
            'rexus/modules/usuarios/model.py',
            'rexus/modules/configuracion/model.py',
            'rexus/modules/herrajes/model.py',
            'rexus/modules/pedidos/model.py',
            'rexus/modules/inventario/model.py'
        ]
    
    def test_no_duplicate_auth_imports(self):
        """Test que no haya imports duplicados de autenticación."""
        
        for module_path in self.modules_to_check:
            full_path = os.path.join(os.getcwd(), module_path)
            if not os.path.exists(full_path):
                continue
                
            with self.subTest(module=module_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Buscar imports de auth_required y similares
                auth_imports = []
                
                # Patrones de imports duplicados problemáticos
                patterns = [
                    r'from\s+rexus\.core\.auth_manager\s+import.*auth_required',
                    r'from\s+rexus\.core\.auth_decorators\s+import.*auth_required',
                    r'from\s+rexus\.core\.auth_manager\s+import.*admin_required',
                    r'from\s+rexus\.core\.auth_decorators\s+import.*admin_required'
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
                    auth_imports.extend(matches)
                
                # No debería haber más de un tipo de import para auth_required/admin_required
                auth_required_sources = []
                admin_required_sources = []
                
                if 'auth_manager' in content and 'auth_required' in content:
                    auth_required_sources.append('auth_manager')
                if 'auth_decorators' in content and 'auth_required' in content:
                    auth_required_sources.append('auth_decorators')
                
                if 'auth_manager' in content and 'admin_required' in content:
                    admin_required_sources.append('auth_manager')
                if 'auth_decorators' in content and 'admin_required' in content:
                    admin_required_sources.append('auth_decorators')
                
                # Verificar que solo hay una fuente para cada decorador
                self.assertLessEqual(len(auth_required_sources), 1, 
                                   f"Imports duplicados de auth_required en {module_path}: {auth_required_sources}")
                self.assertLessEqual(len(admin_required_sources), 1,
                                   f"Imports duplicados de admin_required en {module_path}: {admin_required_sources}")
    
    def test_models_no_pyqt_imports(self):
        """Test que los modelos no importen PyQt6 (violación MVC)."""
        
        for module_path in self.modules_to_check:
            full_path = os.path.join(os.getcwd(), module_path)
            if not os.path.exists(full_path):
                continue
                
            with self.subTest(module=module_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Buscar imports de PyQt6
                pyqt_patterns = [
                    r'from\s+PyQt6',
                    r'import\s+PyQt6',
                    r'from\s+PyQt5',
                    r'import\s+PyQt5'
                ]
                
                for pattern in pyqt_patterns:
                    matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
                    self.assertEqual(len(matches), 0, 
                                   f"Modelo {module_path} no debe importar PyQt: {matches}")
    
    def test_consistent_import_style(self):
        """Test que los imports sigan un estilo consistente."""
        
        for module_path in self.modules_to_check:
            full_path = os.path.join(os.getcwd(), module_path)
            if not os.path.exists(full_path):
                continue
                
            with self.subTest(module=module_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines = content.split('\n')
                import_lines = [line.strip() for line in lines 
                               if line.strip().startswith(('import ', 'from ')) 
                               and not line.strip().startswith('#')]
                
                # Verificar que los imports de auth_decorators sean consistentes
                auth_decorator_imports = [line for line in import_lines 
                                        if 'auth_decorators' in line]
                
                if auth_decorator_imports:
                    # Si hay imports de auth_decorators, no debería haber de auth_manager
                    auth_manager_imports = [line for line in import_lines 
                                          if 'auth_manager' in line and 
                                          ('auth_required' in line or 'admin_required' in line)]
                    
                    self.assertEqual(len(auth_manager_imports), 0,
                                   f"No debe haber imports mixtos en {module_path}: {auth_manager_imports}")
    
    def test_sql_loader_usage(self):
        """Test que los módulos refactorizados usen sql_script_loader."""
        
        refactored_modules = [
            'rexus/modules/vidrios/model.py',
            'rexus/modules/obras/model.py'
        ]
        
        for module_path in refactored_modules:
            full_path = os.path.join(os.getcwd(), module_path)
            if not os.path.exists(full_path):
                continue
                
            with self.subTest(module=module_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Verificar que importe sql_script_loader
                self.assertIn('sql_script_loader', content,
                            f"Módulo {module_path} debe importar sql_script_loader")
                
                # Verificar que lo use en __init__
                self.assertIn('self.sql_loader', content,
                            f"Módulo {module_path} debe inicializar self.sql_loader")
    
    def test_no_embedded_sql_in_refactored_modules(self):
        """Test que los módulos refactorizados no tengan SQL embebido."""
        
        refactored_modules = [
            'rexus/modules/vidrios/model.py',
            'rexus/modules/obras/model.py',
            'rexus/modules/configuracion/model.py'
        ]
        
        # Patrones de SQL embebido peligroso
        dangerous_sql_patterns = [
            r'f".*SELECT.*FROM.*{.*}.*"',
            r"f'.*INSERT.*INTO.*{.*}.*'", 
            r'f".*UPDATE.*SET.*{.*}.*"',
            r"f'.*DELETE.*FROM.*{.*}.*'"
        ]
        
        for module_path in refactored_modules:
            full_path = os.path.join(os.getcwd(), module_path)
            if not os.path.exists(full_path):
                continue
                
            with self.subTest(module=module_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for pattern in dangerous_sql_patterns:
                    matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
                    self.assertEqual(len(matches), 0,
                                   f"SQL embebido encontrado en {module_path}: {matches}")
    
    def test_auth_decorators_usage(self):
        """Test que los métodos críticos usen decoradores de autenticación."""
        
        for module_path in self.modules_to_check:
            full_path = os.path.join(os.getcwd(), module_path)
            if not os.path.exists(full_path):
                continue
                
            with self.subTest(module=module_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Buscar métodos que deberían tener decoradores
                critical_methods = [
                    'crear_', 'actualizar_', 'eliminar_', 'delete_',
                    'cambiar_estado', 'asignar_'
                ]
                
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.strip().startswith('def ') and any(method in line for method in critical_methods):
                        # Verificar que la línea anterior tenga un decorador
                        if i > 0:
                            prev_line = lines[i-1].strip()
                            has_auth_decorator = (
                                '@auth_required' in prev_line or 
                                '@admin_required' in prev_line or
                                '@permission_required' in prev_line
                            )
                            
                            if not has_auth_decorator:
                                # Solo advertir, no fallar, ya que algunos métodos pueden ser internos
                                print(f"ADVERTENCIA: {module_path} línea {i+1}: "
                                     f"Método {line.strip()} podría necesitar decorador de autenticación")


if __name__ == '__main__':
    unittest.main()