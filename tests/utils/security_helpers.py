#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Security Helpers para Tests - Manejo Seguro de Passwords
NO usar passwords reales o genéricos en tests
"""

import hashlib
import secrets
import os
from typing import Dict, Any

class TestSecurityManager:
    """Gestor de seguridad para tests - NO passwords hardcodeados."""
    
    @staticmethod
    def generate_test_password_hash(identifier: str) -> str:
        """
        Genera hash de password único para tests basado en identificador.
        NO usa passwords reales.
        """
        # Usar salt fijo para tests (solo para tests, nunca en producción)
        test_salt = "test_salt_not_for_production"
        combined = f"{identifier}_{test_salt}_{os.environ.get('TEST_SESSION', 'default')}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    @staticmethod
    def create_mock_user_data(username: str, role: str = 'USER') -> Dict[str, Any]:
        """
        Crea datos de usuario mock seguros para tests.
        """
        # Generar ID único basado en hash del username
        user_id = abs(hash(username)) % 10000  # ID numérico único
        
        return {
            'id': user_id,
            'usuario': username,
            'password_hash': TestSecurityManager.generate_test_password_hash(username),
            'rol': role,
            'estado': 'activo',
            'nombre': f'Test_{username}',
            'apellido': 'MockUser',
            'email': f'{username}@test.local',
            'created_for_testing': True  # Marca claramente que es para tests
        }
    
    @staticmethod
    def get_mock_auth_response(username: str, success: bool = True) -> Dict[str, Any]:
        """
        Genera respuesta de autenticación mock para tests.
        """
        if success:
            return {
                'success': True,
                'user_id': hash(username) % 1000,  # ID determinístico para tests
                'username': username,
                'role': 'ADMIN' if username == 'admin' else 'USER',
                'session_id': f"test_session_{secrets.token_hex(8)}",
                'expires_at': '2025-08-22T10:00:00',
                'test_mode': True
            }
        else:
            return {
                'success': False,
                'error': 'invalid_credentials',
                'attempts_remaining': 2,
                'test_mode': True
            }
    
    @staticmethod
    def get_password_strength_test_cases():
        """
        Casos de prueba para validación de fortaleza de passwords.
        NO incluye passwords reales.
        """
        return {
            'weak_patterns': [
                'short',  # Muy corta
                '12345678',  # Solo números
                'abcdefgh',  # Solo letras
                'password',  # Palabra común
                'qwertyui'   # Secuencia de teclado
            ],
            'strong_patterns': [
                'T3st@2025!',    # Compleja pero claramente de test
                'M0ck#P4ssw0rd', # Mock password con símbolos
                'T3st1ng$2025',  # Testing password con números
                'S3cur3@T3st!'   # Secure test pattern
            ],
            'validation_rules': {
                'min_length': 8,
                'require_uppercase': True,
                'require_lowercase': True,
                'require_numbers': True,
                'require_symbols': True,
                'forbid_common_words': ['password', 'admin', 'test', '123456']
            }
        }
    
    @staticmethod
    def create_secure_test_config() -> Dict[str, Any]:
        """
        Configuración segura para tests.
        """
        return {
            'security': {
                'use_mock_auth': True,
                'bypass_real_validation': True,
                'test_mode_enabled': True,
                'log_auth_attempts': False,  # No loggear en tests
                'session_timeout_seconds': 300,  # 5 min para tests
            },
            'database': {
                'use_mock_database': True,
                'isolate_test_data': True,
                'auto_cleanup': True
            },
            'warnings': [
                'NEVER use real passwords in tests',
                'NEVER commit real user data',
                'ALWAYS use mock data for testing',
                'Tests should be isolated and secure'
            ]
        }


class MockPasswordValidator:
    """Validador de passwords mock para tests."""
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """
        Valida fortaleza de password (versión para tests).
        """
        rules = TestSecurityManager.get_password_strength_test_cases()['validation_rules']
        
        result = {
            'is_valid': True,
            'score': 0,
            'issues': [],
            'suggestions': []
        }
        
        # Longitud mínima
        if len(password) < rules['min_length']:
            result['is_valid'] = False
            result['issues'].append(f'Must be at least {rules["min_length"]} characters')
        else:
            result['score'] += 20
        
        # Mayúsculas
        if rules['require_uppercase'] and not any(c.isupper() for c in password):
            result['is_valid'] = False
            result['issues'].append('Must contain uppercase letters')
        else:
            result['score'] += 20
        
        # Minúsculas  
        if rules['require_lowercase'] and not any(c.islower() for c in password):
            result['is_valid'] = False
            result['issues'].append('Must contain lowercase letters')
        else:
            result['score'] += 20
        
        # Números
        if rules['require_numbers'] and not any(c.isdigit() for c in password):
            result['is_valid'] = False
            result['issues'].append('Must contain numbers')
        else:
            result['score'] += 20
        
        # Símbolos
        if rules['require_symbols'] and not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            result['is_valid'] = False
            result['issues'].append('Must contain special characters')
        else:
            result['score'] += 20
        
        # Palabras comunes
        password_lower = password.lower()
        for forbidden in rules['forbid_common_words']:
            if forbidden in password_lower:
                result['is_valid'] = False
                result['issues'].append(f'Cannot contain common word: {forbidden}')
                result['score'] -= 10
        
        return result


# Constantes seguras para tests
SECURE_TEST_CONSTANTS = {
    'MOCK_USERS': {
        'admin': TestSecurityManager.create_mock_user_data('admin', 'ADMIN'),
        'manager': TestSecurityManager.create_mock_user_data('manager', 'MANAGER'), 
        'user': TestSecurityManager.create_mock_user_data('user', 'USER'),
        'viewer': TestSecurityManager.create_mock_user_data('viewer', 'VIEWER')
    },
    'TEST_DISCLAIMER': [
        '🔒 SECURITY WARNING: This file contains MOCK data for testing only',
        '❌ NEVER use real passwords, usernames, or sensitive data in tests',
        '✅ ALL data here is generated for testing purposes only',
        '🧪 Test data is isolated and should not reflect production systems'
    ]
}

# Validación de importación segura
def validate_secure_test_import():
    """
    Validar que este módulo se use solo en contexto de testing.
    """
    import sys
    
    # Verificar que estamos en contexto de testing
    test_indicators = [
        'pytest' in sys.modules,
        'test' in sys.argv[0].lower(),
        os.environ.get('TESTING', '').lower() == 'true'
    ]
    
    if not any(test_indicators):
        print("⚠️  WARNING: Security helpers loaded outside test context")
        print("This module should only be used during testing")
    
    return True

# Auto-validación al importar
validate_secure_test_import()