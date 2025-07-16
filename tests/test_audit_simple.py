#!/usr/bin/env python3
"""
Tests simples de audit trail
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.core.audit_trail import AuditTrail


def test_audit_trail():
    """Test básico de audit trail"""
    print("Iniciando tests de audit trail...")
    
    errors = []
    
    try:
        # Test 1: Crear instancia de AuditTrail
        print("Test 1: Creando instancia de AuditTrail...")
        audit_trail = AuditTrail()
        audit_trail.set_current_user(1, "admin")
        print("OK - AuditTrail creado")
        
        # Test 2: Crear tabla de auditoría
        print("Test 2: Creando tabla de auditoría...")
        try:
            audit_trail._create_audit_table_if_not_exists()
            print("OK - Tabla de auditoría creada")
        except Exception as e:
            errors.append(f"Error creando tabla: {e}")
        
        # Test 3: Registrar cambio
        print("Test 3: Registrando cambio...")
        try:
            success = audit_trail.log_change(
                tabla='test_table',
                accion='TEST',
                registro_id=999,
                datos_nuevos={'test': 'data'},
                modulo='test_module',
                detalles='Test de funcionamiento'
            )
            
            if success:
                print("OK - Cambio registrado")
            else:
                errors.append("Error registrando cambio")
        except Exception as e:
            errors.append(f"Error en log_change: {e}")
        
        # Test 4: Consultar logs
        print("Test 4: Consultando logs...")
        try:
            logs = audit_trail.get_audit_log(limit=5)
            if isinstance(logs, list):
                print(f"OK - Logs consultados: {len(logs)} registros")
            else:
                errors.append("Error consultando logs")
        except Exception as e:
            errors.append(f"Error en get_audit_log: {e}")
        
        # Resumen
        print("\n" + "=" * 40)
        print("RESUMEN DE TESTS DE AUDIT TRAIL:")
        print(f"Total de tests: 4")
        print(f"Errores encontrados: {len(errors)}")
        
        if errors:
            print("\nERRORES:")
            for i, error in enumerate(errors, 1):
                print(f"{i}. {error}")
        else:
            print("Todos los tests de audit trail pasaron!")
        
        return len(errors) == 0
        
    except Exception as e:
        print(f"Error fatal durante tests de audit trail: {e}")
        return False


if __name__ == "__main__":
    success = test_audit_trail()
    sys.exit(0 if success else 1)