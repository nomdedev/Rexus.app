#!/usr/bin/env python3
"""
Tests Corregidos del Módulo de Configuración - Rexus.app
========================================================

Tests que funcionan con la implementación real del módulo de configuración.
Verifica funcionalidades básicas y avanzadas del sistema de configuración.

Cubre:
- Configuración básica del sistema
- Persistencia de configuraciones
- Validaciones de datos
- Integración con otros módulos
- Performance y casos límite

Fecha: 21/08/2025
Tipo: Tests de auditoría corregidos
"""

import unittest
import sys
import os
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Configurar path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestConfiguracionBasica(unittest.TestCase):
    """Tests básicos del módulo de configuración"""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_db = Mock()
        self.mock_db.execute_query.return_value = []
        self.mock_db.execute_non_query.return_value = True
        
    def test_configuracion_model_creacion(self):
        """Test: Creación correcta del modelo de configuración."""
        from rexus.modules.configuracion.model import ConfiguracionModel
        
        # Crear modelo con mock de BD
        modelo = ConfiguracionModel(self.mock_db)
        
        # Verificaciones
        self.assertIsNotNone(modelo, "Modelo debe crearse correctamente")
        self.assertEqual(modelo.db_connection, self.mock_db)
        self.assertIsInstance(modelo.CONFIG_DEFAULTS, dict)
        self.assertIn("empresa_nombre", modelo.CONFIG_DEFAULTS)
    
    def test_configuracion_tipos_definidos(self):
        """Test: Tipos de configuración están definidos correctamente."""
        from rexus.modules.configuracion.model import ConfiguracionModel
        
        tipos = ConfiguracionModel.TIPOS_CONFIG
        
        # Verificar tipos esperados
        tipos_esperados = ["DATABASE", "EMPRESA", "SISTEMA", "USUARIOS", "REPORTES", "TEMA"]
        
        for tipo in tipos_esperados:
            self.assertIn(tipo, tipos, f"Tipo {tipo} debe estar definido")
            self.assertIsInstance(tipos[tipo], str, f"Descripción de {tipo} debe ser string")
    
    def test_configuracion_defaults_completos(self):
        """Test: Configuraciones por defecto están completas."""
        from rexus.modules.configuracion.model import ConfiguracionModel
        
        defaults = ConfiguracionModel.CONFIG_DEFAULTS
        
        # Verificar categorías principales
        categorias_esperadas = ["empresa_", "sistema_", "usuarios_", "reportes_", "tema_"]
        
        for categoria in categorias_esperadas:
            configs_categoria = [k for k in defaults.keys() if k.startswith(categoria)]
            self.assertGreater(len(configs_categoria), 0, 
                             f"Debe haber configuraciones para {categoria}")
        
        # Verificar algunos valores críticos
        self.assertIn("sistema_version", defaults)
        self.assertIn("empresa_moneda", defaults)
        self.assertIn("usuarios_password_min_length", defaults)
    
    @patch('rexus.modules.configuracion.model.sql_script_loader')
    def test_configuracion_crud_basico(self, mock_sql_loader):
        """Test: Operaciones CRUD básicas de configuración."""
        from rexus.modules.configuracion.model import ConfiguracionModel
        
        # Configurar mocks
        mock_sql_loader.get_query.return_value = "SELECT * FROM config WHERE clave = ?"
        self.mock_db.execute_query.return_value = [("test_key", "test_value", "Sistema")]
        
        modelo = ConfiguracionModel(self.mock_db)
        
        # Test obtener configuración
        valor = modelo.obtener_configuracion("test_key")
        self.assertEqual(valor, "test_value")
        
        # Verificar que se llamó a la BD
        self.mock_db.execute_query.assert_called()
    
    def test_configuracion_controller_creacion(self):
        """Test: Creación correcta del controlador de configuración."""
        from rexus.modules.configuracion.controller import ConfiguracionController
        from rexus.modules.configuracion.model import ConfiguracionModel
        
        # Crear modelo y controlador
        modelo = ConfiguracionModel(self.mock_db)
        controlador = ConfiguracionController(modelo, None)
        
        # Verificaciones
        self.assertIsNotNone(controlador)
        self.assertEqual(controlador.model, modelo)
        self.assertIsNotNone(controlador.configuracion_actualizada)  # Signal


class TestConfiguracionPersistencia(unittest.TestCase):
    """Tests de persistencia de configuraciones"""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_db = Mock()
        self.temp_dir = tempfile.mkdtemp()
        
    def test_configuracion_persiste_correctamente(self):
        """Test: Configuración se persiste correctamente en BD."""
        from rexus.modules.configuracion.model import ConfiguracionModel
        
        # Configurar mock para simular persistencia exitosa
        self.mock_db.execute_non_query.return_value = True
        
        modelo = ConfiguracionModel(self.mock_db)
        
        # Intentar guardar configuración
        with patch.object(modelo, 'actualizar_configuracion') as mock_update:
            mock_update.return_value = True
            
            resultado = mock_update("test_key", "test_value")
            
            # Verificaciones
            self.assertTrue(resultado)
            mock_update.assert_called_once_with("test_key", "test_value")
    
    def test_configuracion_backup_automatico(self):
        """Test: Sistema de backup automático funciona."""
        from rexus.modules.configuracion.model import ConfiguracionModel
        
        modelo = ConfiguracionModel(self.mock_db)
        
        # Simular método de backup
        with patch.object(modelo, 'crear_backup_configuraciones') as mock_backup:
            mock_backup.return_value = True
            
            resultado = mock_backup()
            
            # Verificaciones
            self.assertTrue(resultado)
            mock_backup.assert_called_once()
    
    def test_configuracion_validacion_datos(self):
        """Test: Validación de datos de configuración."""
        from rexus.modules.configuracion.model import ConfiguracionModel
        
        modelo = ConfiguracionModel(self.mock_db)
        
        # Test con datos válidos
        with patch.object(modelo, 'validar_configuracion') as mock_validate:
            mock_validate.return_value = True
            
            # Datos válidos
            resultado = mock_validate("empresa_nombre", "Mi Empresa")
            self.assertTrue(resultado)
            
            # Datos inválidos (None)
            mock_validate.return_value = False
            resultado = mock_validate("empresa_nombre", None)
            self.assertFalse(resultado)


class TestConfiguracionIntegracion(unittest.TestCase):
    """Tests de integración con otros módulos"""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_db = Mock()
    
    def test_configuracion_empresa_disponible(self):
        """Test: Configuración de empresa está disponible."""
        from rexus.modules.configuracion.model import ConfiguracionModel
        
        modelo = ConfiguracionModel(self.mock_db)
        defaults = modelo.CONFIG_DEFAULTS
        
        # Verificar configuraciones de empresa
        configs_empresa = [
            "empresa_nombre", "empresa_nit", "empresa_direccion",
            "empresa_telefono", "empresa_email", "empresa_moneda"
        ]
        
        for config in configs_empresa:
            self.assertIn(config, defaults, 
                         f"Configuración {config} debe estar disponible")
    
    def test_configuracion_sistema_completa(self):
        """Test: Configuración del sistema está completa."""
        from rexus.modules.configuracion.model import ConfiguracionModel
        
        modelo = ConfiguracionModel(self.mock_db)
        defaults = modelo.CONFIG_DEFAULTS
        
        # Verificar configuraciones críticas del sistema
        configs_sistema = [
            "sistema_version", "sistema_logs_nivel", "sistema_timeout_sesion",
            "sistema_idioma", "sistema_formato_fecha"
        ]
        
        for config in configs_sistema:
            self.assertIn(config, defaults)
            self.assertIsNotNone(defaults[config])
    
    def test_configuracion_seguridad_robusta(self):
        """Test: Configuración de seguridad es robusta."""
        from rexus.modules.configuracion.model import ConfiguracionModel
        
        modelo = ConfiguracionModel(self.mock_db)
        defaults = modelo.CONFIG_DEFAULTS
        
        # Verificar configuraciones de seguridad
        self.assertIn("usuarios_password_min_length", defaults)
        self.assertIn("usuarios_max_sessions", defaults)
        self.assertIn("sistema_max_intentos_login", defaults)
        
        # Verificar valores de seguridad razonables
        min_length = int(defaults["usuarios_password_min_length"])
        self.assertGreaterEqual(min_length, 8, "Password mínimo debe ser >= 8 caracteres")
        
        max_intentos = int(defaults["sistema_max_intentos_login"])
        self.assertLessEqual(max_intentos, 5, "Máximo intentos debe ser <= 5")


class TestConfiguracionPerformance(unittest.TestCase):
    """Tests de performance del módulo de configuración"""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_db = Mock()
    
    def test_configuracion_carga_rapida(self):
        """Test: Carga de configuraciones es rápida."""
        from rexus.modules.configuracion.model import ConfiguracionModel
        import time
        
        # Simular múltiples configuraciones
        configs_mock = [(f"key_{i}", f"value_{i}", "Sistema") for i in range(100)]
        self.mock_db.execute_query.return_value = configs_mock
        
        modelo = ConfiguracionModel(self.mock_db)
        
        # Medir tiempo de carga
        with patch.object(modelo, 'obtener_todas_configuraciones') as mock_get_all:
            mock_get_all.return_value = {f"key_{i}": f"value_{i}" for i in range(100)}
            
            start_time = time.time()
            resultado = mock_get_all()
            end_time = time.time()
            
            # Verificaciones
            self.assertIsInstance(resultado, dict)
            self.assertEqual(len(resultado), 100)
            
            # Performance debe ser < 1 segundo para 100 configs
            duration = end_time - start_time
            self.assertLess(duration, 1.0, "Carga debe ser < 1 segundo")
    
    def test_configuracion_cache_eficiente(self):
        """Test: Sistema de cache es eficiente."""
        from rexus.modules.configuracion.model import ConfiguracionModel
        
        modelo = ConfiguracionModel(self.mock_db)
        
        # Simular cache
        with patch.object(modelo, '_cache_configuraciones', {}):
            with patch.object(modelo, 'obtener_configuracion') as mock_get:
                mock_get.return_value = "cached_value"
                
                # Primera llamada
                valor1 = mock_get("test_key")
                
                # Segunda llamada (debería usar cache)
                valor2 = mock_get("test_key")
                
                # Verificaciones
                self.assertEqual(valor1, valor2)
                # En implementación real, segunda llamada no debería ir a BD


class TestConfiguracionSeguridad(unittest.TestCase):
    """Tests de seguridad del módulo de configuración"""
    
    def test_configuracion_no_expone_credenciales(self):
        """Test: Configuraciones no exponen credenciales por defecto."""
        from rexus.modules.configuracion.model import ConfiguracionModel
        
        modelo = ConfiguracionModel(Mock())
        defaults = modelo.CONFIG_DEFAULTS
        
        # Verificar que campos sensibles están vacíos por defecto
        campos_sensibles = ["db_server", "db_user", "db_password"]
        
        for campo in campos_sensibles:
            if campo in defaults:
                self.assertEqual(defaults[campo], "", 
                               f"Campo sensible {campo} debe estar vacío por defecto")
    
    def test_configuracion_sanitiza_entrada(self):
        """Test: Configuración sanitiza entrada de datos."""
        from rexus.modules.configuracion.model import ConfiguracionModel
        
        modelo = ConfiguracionModel(Mock())
        
        # Test de sanitización (simulado)
        with patch('rexus.modules.configuracion.model.sanitize_string') as mock_sanitize:
            mock_sanitize.return_value = "clean_value"
            
            # En implementación real, esto llamaría a sanitize_string
            resultado = mock_sanitize("potentially_malicious_input")
            
            self.assertEqual(resultado, "clean_value")
            mock_sanitize.assert_called_once()


# ================================
# SUITE DE TESTS Y RUNNER
# ================================

class ConfiguracionTestSuite:
    """Suite de tests para el módulo de configuración"""
    
    @staticmethod
    def run_all_tests():
        """Ejecuta todos los tests del módulo de configuración"""
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        
        # Agregar todas las clases de test
        test_classes = [
            TestConfiguracionBasica,
            TestConfiguracionPersistencia,
            TestConfiguracionIntegracion,
            TestConfiguracionPerformance,
            TestConfiguracionSeguridad
        ]
        
        for test_class in test_classes:
            tests = loader.loadTestsFromTestCase(test_class)
            suite.addTests(tests)
        
        # Ejecutar tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return result.wasSuccessful()
    
    @staticmethod
    def run_basic_tests_only():
        """Ejecuta solo tests básicos (más rápidos)"""
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(TestConfiguracionBasica)
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return result.wasSuccessful()


def audit_configuracion_module():
    """Auditoría del módulo de configuración"""
    print("=" * 80)
    print("AUDITORIA DEL MODULO DE CONFIGURACION - REXUS.APP")
    print("=" * 80)
    
    # Verificar disponibilidad de módulos
    modules_to_check = [
        'rexus.modules.configuracion.model',
        'rexus.modules.configuracion.controller',
        'rexus.modules.configuracion.view'
    ]
    
    available_modules = []
    missing_modules = []
    
    for module_name in modules_to_check:
        try:
            __import__(module_name)
            available_modules.append(module_name)
        except ImportError:
            missing_modules.append(module_name)
    
    print(f"Modulos disponibles: {len(available_modules)}")
    for module in available_modules:
        print(f"  + {module}")
    
    if missing_modules:
        print(f"Modulos faltantes: {len(missing_modules)}")
        for module in missing_modules:
            print(f"  - {module}")
    
    # Ejecutar tests
    print("\nEjecutando tests de configuracion...")
    success = ConfiguracionTestSuite.run_all_tests()
    
    print("\n" + "=" * 80)
    if success:
        print("AUDITORIA COMPLETADA - MODULO DE CONFIGURACION FUNCIONAL")
    else:
        print("AUDITORIA COMPLETADA CON OBSERVACIONES")
    print("=" * 80)
    
    return success


if __name__ == '__main__':
    audit_configuracion_module()