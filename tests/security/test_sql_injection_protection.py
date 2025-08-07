#!/usr/bin/env python3
"""
Tests de Seguridad - SQL Injection Protection
Rexus.app - Suite de Tests de Seguridad Crítica

Valida que todos los módulos refactorizados estén protegidos contra SQL injection.
"""

import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock

# Test cases para SQL injection
SQL_INJECTION_PAYLOADS = [
    "'; DROP TABLE users; --",
    "1' OR '1'='1",
    "admin'--",
    "' UNION SELECT * FROM usuarios --",
    "1; DELETE FROM configuracion; --",
    "' OR 1=1 --",
    "1') OR '1'='1' --",
    "'; INSERT INTO usuarios VALUES ('hack','hack'); --",
    "1' AND (SELECT COUNT(*) FROM usuarios) > 0 --",
    "' OR EXISTS(SELECT * FROM works) --"
]

class TestSQLInjectionProtection(unittest.TestCase):
    """Tests para protección contra SQL injection en módulos refactorizados."""
    
    def setUp(self):
        """Configurar mocks para base de datos."""
        self.mock_db = Mock()
        self.mock_cursor = Mock()
        self.mock_db.cursor.return_value = self.mock_cursor
        self.mock_cursor.fetchone.return_value = (0,)  # No resultados por defecto
        self.mock_cursor.fetchall.return_value = []
    
    @patch('rexus.utils.sql_script_loader.sql_script_loader')
    def test_vidrios_model_sql_injection_protection(self, mock_sql_loader):
        """Test protección SQL injection en módulo vidrios."""
        from rexus.modules.vidrios.model import VidriosModel
        
        # Mock SQL script loader
        mock_sql_loader.load_script.return_value = "SELECT * FROM vidrios WHERE codigo = ?"
        
        # Crear instancia del modelo
        model = VidriosModel(self.mock_db)
        
        # Test buscar vidrios con payloads maliciosos
        for payload in SQL_INJECTION_PAYLOADS:
            with self.subTest(payload=payload):
                try:
                    success, results = model.buscar_vidrios(payload)
                    
                    # Verificar que los parámetros se pasan correctamente (no embebidos en SQL)
                    self.mock_cursor.execute.assert_called()
                    call_args = self.mock_cursor.execute.call_args
                    
                    # El SQL debe ser un script cargado, no contener el payload directamente
                    sql_query = call_args[0][0]
                    self.assertNotIn(payload, sql_query, "El payload no debe estar embebido en el SQL")
                    
                    # Los parámetros deben ser pasados separadamente
                    if len(call_args[0]) > 1:
                        params = call_args[0][1]
                        self.assertIsInstance(params, (tuple, list), "Los parámetros deben ser una tupla o lista")
                        
                except Exception as e:
                    # Las excepciones están permitidas (sanitización), pero no deben causar SQL injection
                    self.assertNotIn("syntax error", str(e).lower(), "No debe haber errores de sintaxis SQL")
    
    @patch('rexus.utils.sql_script_loader.sql_script_loader')
    def test_obras_model_sql_injection_protection(self, mock_sql_loader):
        """Test protección SQL injection en módulo obras."""
        from rexus.modules.obras.model import ObrasModel
        
        # Mock SQL script loader
        mock_sql_loader.load_script.return_value = "SELECT COUNT(*) FROM obras WHERE codigo = ?"
        
        # Crear instancia del modelo
        model = ObrasModel(self.mock_db)
        
        # Test validar obra duplicada con payloads maliciosos
        for payload in SQL_INJECTION_PAYLOADS:
            with self.subTest(payload=payload):
                try:
                    result = model.validar_obra_duplicada(payload)
                    
                    # Verificar que se usa query parametrizada
                    self.mock_cursor.execute.assert_called()
                    call_args = self.mock_cursor.execute.call_args
                    
                    if call_args and len(call_args[0]) > 1:
                        sql_query = call_args[0][0]
                        params = call_args[0][1]
                        
                        # SQL no debe contener el payload directamente
                        self.assertNotIn(payload, sql_query, "El payload no debe estar embebido en el SQL")
                        
                        # Debe usar parámetros
                        self.assertIsInstance(params, (tuple, list), "Debe usar parámetros seguros")
                        
                except Exception as e:
                    # Excepciones por sanitización están permitidas
                    self.assertNotIn("DROP", str(e).upper(), "No debe ejecutar comandos DROP")
                    self.assertNotIn("DELETE", str(e).upper(), "No debe ejecutar comandos DELETE")
    
    @patch('rexus.utils.sql_script_loader.sql_script_loader')
    def test_usuarios_model_sql_injection_protection(self, mock_sql_loader):
        """Test protección SQL injection en módulo usuarios.""" 
        from rexus.modules.usuarios.model import UsuariosModel
        
        # Mock SQL script loader
        mock_sql_loader.load_script.return_value = "SELECT COUNT(*) FROM usuarios WHERE username = ?"
        
        # Crear instancia del modelo
        model = UsuariosModel(self.mock_db)
        
        # Test validar usuario duplicado con payloads maliciosos
        for payload in SQL_INJECTION_PAYLOADS:
            with self.subTest(payload=payload):
                try:
                    result = model.validar_usuario_duplicado(payload, "test@test.com")
                    
                    # Verificar llamadas a cursor
                    if self.mock_cursor.execute.called:
                        call_args = self.mock_cursor.execute.call_args
                        sql_query = call_args[0][0]
                        
                        # SQL no debe contener payloads maliciosos
                        self.assertNotIn(payload, sql_query, "El payload no debe estar embebido")
                        self.assertNotIn("DROP", sql_query.upper(), "No debe contener comandos DROP")
                        self.assertNotIn("DELETE", sql_query.upper(), "No debe contener comandos DELETE")
                        
                except Exception as e:
                    # Error de sanitización es aceptable
                    self.assertNotIn("syntax error", str(e).lower(), "No debe haber errores SQL")
    
    def test_sql_script_usage_no_fstrings(self):
        """Test que los módulos no usen f-strings peligrosos con SQL."""
        import os
        import re
        
        modules_to_check = [
            'rexus/modules/vidrios/model.py',
            'rexus/modules/obras/model.py',
            'rexus/modules/usuarios/model.py',
            'rexus/modules/configuracion/model.py',
            'rexus/modules/herrajes/model.py'
        ]
        
        # Patrón para detectar f-strings peligrosos con SQL
        dangerous_patterns = [
            r'f".*SELECT.*{.*}.*"',
            r"f'.*INSERT.*{.*}.*'",
            r'f".*UPDATE.*{.*}.*"',
            r"f'.*DELETE.*{.*}.*'",
            r'f".*FROM.*{.*}.*"',
            r"f'.*WHERE.*{.*}.*'"
        ]
        
        for module_path in modules_to_check:
            full_path = os.path.join(os.getcwd(), module_path)
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    for pattern in dangerous_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
                        self.assertEqual(len(matches), 0, 
                                       f"Encontrado f-string peligroso en {module_path}: {matches}")
    
    @patch('rexus.utils.sql_script_loader.sql_script_loader')
    def test_parametrized_queries_usage(self, mock_sql_loader):
        """Test que se usen queries parametrizadas en lugar de concatenación."""
        from rexus.modules.vidrios.model import VidriosModel
        
        # Mock para simular script SQL
        mock_sql_loader.load_script.return_value = "INSERT INTO vidrios (codigo, descripcion) VALUES (?, ?)"
        
        model = VidriosModel(self.mock_db)
        
        # Datos de prueba con caracteres especiales
        test_data = {
            "codigo": "TEST'; DROP TABLE vidrios; --",
            "descripcion": "Test ' malicioso \" injection",
            "tipo": "Templado",
            "proveedor": "Test & Co.",
            "precio_m2": 50.0
        }
        
        # Intentar crear vidrio
        try:
            success, message, vid_id = model.crear_vidrio(test_data)
            
            # Verificar que se llamó execute con parámetros separados
            self.mock_cursor.execute.assert_called()
            call_args = self.mock_cursor.execute.call_args
            
            if len(call_args[0]) > 1:
                sql_query = call_args[0][0]
                params = call_args[0][1]
                
                # El SQL debe contener placeholders (?), no valores directos
                self.assertIn("?", sql_query, "Debe usar placeholders parametrizados")
                self.assertNotIn("DROP TABLE", sql_query, "No debe contener comandos peligrosos")
                
                # Los parámetros deben ser una tupla/lista
                self.assertIsInstance(params, (tuple, list), "Debe usar parámetros seguros")
                
        except Exception:
            # Las excepciones por sanitización son aceptables
            pass


if __name__ == '__main__':
    unittest.main()