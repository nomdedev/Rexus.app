"""
Tests para Sistema de Integridad de Auditoría - Rexus.app

Tests que validan el sistema de integridad de registros de auditoría,
incluyendo hashing, firma digital, cadena de integridad y detección de manipulación.

Author: Rexus Testing Team
Date: 2025-08-11
Version: 1.0.0
"""

import pytest
import json
import hashlib
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Import the modules we're testing
try:
    from rexus.core.audit_integrity import (
        AuditIntegrityManager,
        AuditRecord,
        IntegrityReport,
        IntegrityChainInfo,
        IntegrityStatus,
        init_audit_integrity,
        get_audit_integrity_manager,
        create_secure_audit_record,
        verify_audit_record
    )
    AUDIT_INTEGRITY_AVAILABLE = True
except ImportError:
    AUDIT_INTEGRITY_AVAILABLE = False


@pytest.mark.skipif(not AUDIT_INTEGRITY_AVAILABLE, reason="Audit integrity modules not available")
class TestAuditIntegrityManager:
    """Tests para la clase AuditIntegrityManager."""
    
    def test_initialization_without_keys(self):
        """Test que valida la inicialización sin claves externas."""
        manager = AuditIntegrityManager()
        
        assert manager.secret_key is not None
        assert len(manager.secret_key) > 0
        assert manager.private_key is not None
        assert manager.public_key is not None
        assert manager.signature_enabled
        assert manager.genesis_hash is None
        assert manager.last_record_hash is None
    
    def test_initialization_with_secret_key(self):
        """Test que valida la inicialización con clave secreta."""
        test_secret = "test_secret_key_for_integrity"
        manager = AuditIntegrityManager(secret_key=test_secret)
        
        assert manager.secret_key == test_secret.encode()
        assert manager.signature_enabled
    
    def test_create_audit_record_basic(self):
        """Test que valida la creación básica de registros de auditoría."""
        manager = AuditIntegrityManager()
        
        record = manager.create_audit_record(
            event_type="USER_LOGIN",
            user_id=1,
            resource="authentication",
            action="login",
            details={"success": True, "method": "password"},
            ip_address="192.168.1.100"
        )
        
        assert record.id is not None
        assert record.id.startswith("audit_")
        assert record.event_type == "USER_LOGIN"
        assert record.user_id == 1
        assert record.resource == "authentication"
        assert record.action == "login"
        assert record.details == {"success": True, "method": "password"}
        assert record.ip_address == "192.168.1.100"
        assert record.content_hash is not None
        assert len(record.content_hash) == 64  # SHA256 hex
        assert record.integrity_sealed == True
    
    def test_record_content_hash_consistency(self):
        """Test que valida la consistencia del hash de contenido."""
        manager = AuditIntegrityManager()
        
        # Crear registro
        record = manager.create_audit_record(
            event_type="TEST_EVENT",
            user_id=1,
            resource="test_resource",
            action="test_action",
            details={"key": "value"}
        )
        
        # Calcular hash esperado manualmente
        record_dict = {
            "id": record.id,
            "timestamp": record.timestamp,
            "event_type": "TEST_EVENT",
            "user_id": 1,
            "resource": "test_resource",
            "action": "test_action",
            "details": {"key": "value"},
            "ip_address": None,
            "user_agent": None,
            "session_id": None,
            "created_by_system": "rexus_audit"
        }
        
        expected_hash = hashlib.sha256(
            json.dumps(record_dict, sort_keys=True).encode('utf-8')
        ).hexdigest()
        
        assert record.content_hash == expected_hash
    
    def test_chain_hash_linking(self):
        """Test que valida el enlazamiento de hash de cadena."""
        manager = AuditIntegrityManager()
        
        # Crear primer registro
        record1 = manager.create_audit_record(
            event_type="FIRST_EVENT",
            user_id=1,
            resource="test",
            action="create",
            details={"order": 1}
        )
        
        # Verificar que es el primer registro de la cadena
        assert record1.previous_hash is None
        assert record1.chain_hash is not None
        
        # Crear segundo registro
        record2 = manager.create_audit_record(
            event_type="SECOND_EVENT",
            user_id=1,
            resource="test",
            action="update",
            details={"order": 2}
        )
        
        # Verificar enlazamiento
        assert record2.previous_hash == record1.chain_hash
        assert record2.chain_hash != record1.chain_hash
        
        # Verificar que el gestor mantuvo el estado
        assert manager.genesis_hash == record1.chain_hash
        assert manager.last_record_hash == record2.chain_hash
    
    def test_record_signature(self):
        """Test que valida la firma digital de registros."""
        manager = AuditIntegrityManager()
        
        record = manager.create_audit_record(
            event_type="SIGNED_EVENT",
            user_id=1,
            resource="sensitive",
            action="access",
            details={"classified": True}
        )
        
        # Verificar que se generó firma
        assert record.signature is not None
        assert len(record.signature) > 0
        
        # Verificar que la firma es válida
        assert manager._verify_signature(record)
    
    def test_verify_record_integrity_valid(self):
        """Test que valida verificación de integridad exitosa."""
        manager = AuditIntegrityManager()
        
        record = manager.create_audit_record(
            event_type="VALID_EVENT",
            user_id=1,
            resource="test",
            action="validate",
            details={"test": True}
        )
        
        status, issues = manager.verify_record_integrity(record)
        
        assert status == IntegrityStatus.VALID
        assert len(issues) == 0
    
    def test_verify_record_integrity_tampered(self):
        """Test que valida detección de registros manipulados."""
        manager = AuditIntegrityManager()
        
        record = manager.create_audit_record(
            event_type="ORIGINAL_EVENT",
            user_id=1,
            resource="test",
            action="test",
            details={"original": True}
        )
        
        # Manipular el registro
        record.details = {"tampered": True}
        
        status, issues = manager.verify_record_integrity(record)
        
        assert status == IntegrityStatus.CORRUPTED
        assert len(issues) > 0
        assert any("Hash de contenido inválido" in issue for issue in issues)
    
    def test_verify_record_integrity_signature_invalid(self):
        """Test que valida detección de firma inválida."""
        manager = AuditIntegrityManager()
        
        record = manager.create_audit_record(
            event_type="SIGNED_EVENT",
            user_id=1,
            resource="test",
            action="test",
            details={"signed": True}
        )
        
        # Corromper la firma
        record.signature = "invalid_signature_base64=="
        
        status, issues = manager.verify_record_integrity(record)
        
        assert status == IntegrityStatus.SIGNATURE_INVALID
        assert len(issues) > 0
        assert any("Firma digital inválida" in issue for issue in issues)
    
    def test_verify_chain_integrity_valid(self):
        """Test que valida verificación de integridad de cadena válida."""
        manager = AuditIntegrityManager()
        
        # Crear cadena de registros
        records = []
        for i in range(5):
            record = manager.create_audit_record(
                event_type=f"EVENT_{i}",
                user_id=1,
                resource="chain_test",
                action="sequence",
                details={"sequence": i}
            )
            records.append(record)
        
        # Verificar integridad de la cadena
        report = manager.verify_chain_integrity(records)
        
        assert report.total_records == 5
        assert report.valid_records == 5
        assert report.corrupted_records == 0
        assert report.tampered_records == 0
        assert report.chain_integrity == True
        assert report.signature_validity == True
        assert len(report.issues) == 0
    
    def test_verify_chain_integrity_broken_chain(self):
        """Test que valida detección de cadena rota."""
        manager = AuditIntegrityManager()
        
        # Crear tres registros
        record1 = manager.create_audit_record(
            event_type="EVENT_1", user_id=1, resource="test", action="test", details={}
        )
        record2 = manager.create_audit_record(
            event_type="EVENT_2", user_id=1, resource="test", action="test", details={}
        )
        record3 = manager.create_audit_record(
            event_type="EVENT_3", user_id=1, resource="test", action="test", details={}
        )
        
        # Romper la cadena modificando el hash previo del registro 2
        record2.previous_hash = "fake_hash_that_breaks_chain"
        
        records = [record1, record2, record3]
        report = manager.verify_chain_integrity(records)
        
        assert report.chain_integrity == False
        assert len(report.issues) > 0
        assert any("Hash previo no coincide" in issue["issue"] for issue in report.issues)
    
    def test_verify_chain_integrity_missing_record(self):
        """Test que valida detección de registros faltantes."""
        manager = AuditIntegrityManager()
        
        # Crear tres registros
        record1 = manager.create_audit_record(
            event_type="EVENT_1", user_id=1, resource="test", action="test", details={}
        )
        record2 = manager.create_audit_record(
            event_type="EVENT_2", user_id=1, resource="test", action="test", details={}
        )
        record3 = manager.create_audit_record(
            event_type="EVENT_3", user_id=1, resource="test", action="test", details={}
        )
        
        # Simular registro faltante omitiendo record2
        records = [record1, record3]
        report = manager.verify_chain_integrity(records)
        
        assert report.chain_integrity == False
        assert len(report.issues) > 0
        assert any("Hash previo no coincide" in issue["issue"] for issue in report.issues)
    
    def test_export_chain_proof(self):
        """Test que valida exportación de prueba de cadena."""
        manager = AuditIntegrityManager()
        
        # Crear cadena de registros
        records = []
        for i in range(3):
            record = manager.create_audit_record(
                event_type=f"EXPORT_EVENT_{i}",
                user_id=1,
                resource="export_test",
                action="test",
                details={"index": i}
            )
            records.append(record)
        
        # Exportar prueba
        proof = manager.export_chain_proof(records)
        
        assert "export_timestamp" in proof
        assert proof["total_records"] == 3
        assert "first_record_timestamp" in proof
        assert "last_record_timestamp" in proof
        assert "full_chain_hash" in proof
        assert "integrity_report" in proof
        assert "key_fingerprint" in proof
        assert "records" in proof
        assert "export_signature" in proof
        assert len(proof["records"]) == 3
        
        # Verificar que el reporte de integridad es válido
        integrity_report = proof["integrity_report"]
        assert integrity_report["chain_integrity"] == True
        assert integrity_report["valid_records"] == 3
    
    def test_export_chain_proof_corrupted_chain(self):
        """Test que valida rechazo de exportación de cadena corrupta."""
        manager = AuditIntegrityManager()
        
        # Crear registro y corromperlo
        record = manager.create_audit_record(
            event_type="CORRUPTED_EVENT",
            user_id=1,
            resource="test",
            action="test",
            details={"original": True}
        )
        
        # Corromper el registro
        record.details = {"corrupted": True}
        
        # Intentar exportar debe fallar
        with pytest.raises(ValueError, match="integridad comprometida"):
            manager.export_chain_proof([record])
    
    def test_import_and_verify_chain(self):
        """Test que valida importación y verificación de cadena."""
        manager = AuditIntegrityManager()
        
        # Crear y exportar cadena original
        original_records = []
        for i in range(3):
            record = manager.create_audit_record(
                event_type=f"IMPORT_EVENT_{i}",
                user_id=1,
                resource="import_test",
                action="test",
                details={"index": i}
            )
            original_records.append(record)
        
        export_proof = manager.export_chain_proof(original_records)
        
        # Crear nuevo gestor para simular importación en sistema diferente
        new_manager = AuditIntegrityManager(secret_key="same_secret")
        # Copiar claves para verificación de firma
        new_manager.private_key = manager.private_key
        new_manager.public_key = manager.public_key
        
        # Importar y verificar
        is_valid, report = new_manager.import_and_verify_chain(export_proof)
        
        assert is_valid == True
        assert report.chain_integrity == True
        assert report.total_records == 3
        assert report.valid_records == 3
        assert len(report.issues) == 0
    
    def test_import_and_verify_chain_tampered_export(self):
        """Test que valida detección de exportación manipulada."""
        manager = AuditIntegrityManager()
        
        # Crear y exportar cadena
        record = manager.create_audit_record(
            event_type="EXPORT_EVENT",
            user_id=1,
            resource="test",
            action="test",
            details={}
        )
        
        export_proof = manager.export_chain_proof([record])
        
        # Manipular la exportación
        export_proof["full_chain_hash"] = "tampered_hash"
        
        # Crear nuevo gestor
        new_manager = AuditIntegrityManager()
        new_manager.private_key = manager.private_key
        new_manager.public_key = manager.public_key
        
        # Importar debe detectar manipulación
        is_valid, report = new_manager.import_and_verify_chain(export_proof)
        
        assert is_valid == False
        assert report.chain_integrity == False
        assert len(report.issues) > 0
    
    def test_chain_state_tracking(self):
        """Test que valida seguimiento del estado de la cadena."""
        manager = AuditIntegrityManager()
        
        # Inicialmente no hay cadena
        assert manager.chain_info is None
        
        # Crear primer registro
        record1 = manager.create_audit_record(
            event_type="FIRST",
            user_id=1,
            resource="test",
            action="test",
            details={}
        )
        
        # Verificar estado inicial de cadena
        assert manager.chain_info is not None
        assert manager.chain_info.genesis_hash == record1.chain_hash
        assert manager.chain_info.last_hash == record1.chain_hash
        assert manager.chain_info.chain_length == 1
        
        # Crear segundo registro
        record2 = manager.create_audit_record(
            event_type="SECOND",
            user_id=1,
            resource="test",
            action="test",
            details={}
        )
        
        # Verificar actualización de estado
        assert manager.chain_info.genesis_hash == record1.chain_hash  # No cambia
        assert manager.chain_info.last_hash == record2.chain_hash     # Se actualiza
        assert manager.chain_info.chain_length == 2                  # Se incrementa
    
    def test_key_fingerprint_generation(self):
        """Test que valida generación de huella digital de clave."""
        manager = AuditIntegrityManager()
        
        fingerprint = manager._get_key_fingerprint()
        
        assert fingerprint is not None
        assert len(fingerprint) == 16  # Primeros 16 caracteres de hash
        assert isinstance(fingerprint, str)
    
    def test_concurrent_record_creation(self):
        """Test que valida creación concurrente de registros."""
        import threading
        import time
        
        manager = AuditIntegrityManager()
        records = []
        errors = []
        
        def create_record(index):
            try:
                record = manager.create_audit_record(
                    event_type=f"CONCURRENT_{index}",
                    user_id=index,
                    resource="concurrent_test",
                    action="create",
                    details={"thread": index}
                )
                records.append(record)
            except Exception as e:
                errors.append(str(e))
        
        # Crear múltiples threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_record, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Esperar que terminen
        for thread in threads:
            thread.join()
        
        # Verificar resultados
        assert len(errors) == 0, f"Errors in concurrent creation: {errors}"
        assert len(records) == 5
        
        # Verificar que todos los registros son válidos
        for record in records:
            status, issues = manager.verify_record_integrity(record)
            assert status == IntegrityStatus.VALID, f"Record {record.id} invalid: {issues}"


@pytest.mark.skipif(not AUDIT_INTEGRITY_AVAILABLE, reason="Audit integrity modules not available")
class TestAuditIntegrityGlobalFunctions:
    """Tests para las funciones globales del sistema de integridad."""
    
    def test_init_and_get_audit_integrity_manager(self):
        """Test que valida inicialización global."""
        manager = init_audit_integrity(secret_key="global_test_key")
        
        assert manager is not None
        assert isinstance(manager, AuditIntegrityManager)
        
        # Obtener instancia global
        global_manager = get_audit_integrity_manager()
        
        assert global_manager is manager
    
    def test_create_secure_audit_record_global(self):
        """Test que valida función global de creación de registro."""
        init_audit_integrity(secret_key="global_test_key")
        
        record = create_secure_audit_record(
            event_type="GLOBAL_EVENT",
            user_id=1,
            resource="global_resource",
            action="global_action",
            details={"global": True}
        )
        
        assert record.event_type == "GLOBAL_EVENT"
        assert record.user_id == 1
        assert record.resource == "global_resource"
        assert record.action == "global_action"
        assert record.details == {"global": True}
        assert record.integrity_sealed == True
    
    def test_verify_audit_record_global(self):
        """Test que valida función global de verificación."""
        init_audit_integrity(secret_key="global_test_key")
        
        # Crear registro usando función global
        record = create_secure_audit_record(
            event_type="VERIFY_EVENT",
            user_id=1,
            resource="verify_test",
            action="verify",
            details={"verify": True}
        )
        
        # Verificar usando función global
        status, issues = verify_audit_record(record)
        
        assert status == IntegrityStatus.VALID
        assert len(issues) == 0


@pytest.mark.skipif(not AUDIT_INTEGRITY_AVAILABLE, reason="Audit integrity modules not available")
class TestAuditIntegrityIntegration:
    """Tests de integración para el sistema de integridad."""
    
    def test_full_audit_lifecycle(self):
        """Test que valida ciclo completo de auditoría."""
        manager = AuditIntegrityManager()
        
        # 1. Crear múltiples eventos de auditoría
        events = [
            ("USER_LOGIN", 1, "auth", "login", {"success": True}),
            ("RESOURCE_ACCESS", 1, "documents", "read", {"document_id": 123}),
            ("DATA_MODIFICATION", 1, "documents", "update", {"document_id": 123, "changes": ["title"]}),
            ("PERMISSION_CHANGE", 2, "users", "grant", {"target_user": 1, "permission": "admin"}),
            ("USER_LOGOUT", 1, "auth", "logout", {"session_duration": 1800})
        ]
        
        records = []
        for event_type, user_id, resource, action, details in events:
            record = manager.create_audit_record(
                event_type=event_type,
                user_id=user_id,
                resource=resource,
                action=action,
                details=details,
                ip_address="192.168.1.100"
            )
            records.append(record)
        
        # 2. Verificar integridad individual
        for record in records:
            status, issues = manager.verify_record_integrity(record)
            assert status == IntegrityStatus.VALID, f"Record {record.id} failed: {issues}"
        
        # 3. Verificar integridad de cadena
        chain_report = manager.verify_chain_integrity(records)
        assert chain_report.chain_integrity == True
        assert chain_report.total_records == 5
        assert chain_report.valid_records == 5
        
        # 4. Exportar cadena
        export_proof = manager.export_chain_proof(records)
        assert export_proof["total_records"] == 5
        
        # 5. Importar en nuevo sistema
        new_manager = AuditIntegrityManager()
        new_manager.private_key = manager.private_key
        new_manager.public_key = manager.public_key
        
        is_valid, import_report = new_manager.import_and_verify_chain(export_proof)
        assert is_valid == True
        assert import_report.chain_integrity == True
    
    def test_forensic_analysis_scenario(self):
        """Test que simula análisis forense de registros."""
        manager = AuditIntegrityManager()
        
        # Crear registros que simulan actividad sospechosa
        suspicious_events = [
            ("USER_LOGIN", 1, "auth", "login", {"success": True, "method": "password"}),
            ("PRIVILEGE_ESCALATION", 1, "system", "escalate", {"from": "user", "to": "admin"}),
            ("SENSITIVE_ACCESS", 1, "secrets", "read", {"resource": "api_keys"}),
            ("DATA_EXFILTRATION", 1, "data", "export", {"records": 10000, "format": "csv"}),
            ("LOG_TAMPERING", 1, "audit", "delete", {"target": "security_logs"})
        ]
        
        records = []
        for event_type, user_id, resource, action, details in suspicious_events:
            record = manager.create_audit_record(
                event_type=event_type,
                user_id=user_id,
                resource=resource,
                action=action,
                details=details,
                ip_address="10.0.0.100",
                user_agent="SuspiciousBot/1.0"
            )
            records.append(record)
        
        # Simular intento de manipulación del registro de tampering
        tampered_record = records[-1]  # LOG_TAMPERING
        original_details = tampered_record.details.copy()
        
        # Un atacante intenta modificar los detalles
        tampered_record.details = {"target": "unimportant_logs"}  # Cambiar objetivo
        
        # Análisis forense debe detectar la manipulación
        tampered_status, tampered_issues = manager.verify_record_integrity(tampered_record)
        assert tampered_status == IntegrityStatus.CORRUPTED
        assert len(tampered_issues) > 0
        
        # Restaurar registro original para verificar cadena completa
        tampered_record.details = original_details
        
        # La cadena debe ser válida cuando no hay manipulación
        chain_report = manager.verify_chain_integrity(records)
        assert chain_report.chain_integrity == True
        
        # Generar reporte forense
        forensic_export = manager.export_chain_proof(records)
        assert forensic_export["total_records"] == 5
        assert "export_signature" in forensic_export
    
    @patch('rexus.core.audit_integrity.log_security_event')
    def test_security_logging_integration(self, mock_log):
        """Test que valida integración con logging de seguridad."""
        manager = AuditIntegrityManager()
        
        # Crear registro de auditoría
        record = manager.create_audit_record(
            event_type="SECURITY_TEST",
            user_id=1,
            resource="test",
            action="test",
            details={"security_test": True}
        )
        
        # Verificar que se generaron eventos de logging
        mock_log.assert_called()
        
        # Verificar tipos de eventos logueados
        call_args_list = mock_log.call_args_list
        event_types = [call[0][0] for call in call_args_list]
        
        assert "AUDIT_INTEGRITY_MANAGER_INITIALIZED" in event_types
        assert "AUDIT_RECORD_CREATED" in event_types
    
    def test_performance_with_large_chain(self):
        """Test que valida rendimiento con cadena grande."""
        import time
        
        manager = AuditIntegrityManager()
        
        # Crear cadena de 100 registros
        records = []
        start_time = time.time()
        
        for i in range(100):
            record = manager.create_audit_record(
                event_type=f"PERFORMANCE_EVENT_{i}",
                user_id=i % 5 + 1,  # Rotación entre 5 usuarios
                resource="performance_test",
                action="test",
                details={"index": i, "data": f"test_data_{i}"}
            )
            records.append(record)
        
        creation_time = time.time() - start_time
        
        # Verificar que la creación fue razonablemente rápida (< 10 segundos)
        assert creation_time < 10.0, f"Creation took too long: {creation_time}s"
        
        # Verificar integridad de cadena completa
        start_time = time.time()
        chain_report = manager.verify_chain_integrity(records)
        verification_time = time.time() - start_time
        
        assert chain_report.chain_integrity == True
        assert chain_report.total_records == 100
        assert chain_report.valid_records == 100
        
        # Verificación debe ser rápida (< 5 segundos)
        assert verification_time < 5.0, f"Verification took too long: {verification_time}s"


# Fixtures para tests de integridad de auditoría
@pytest.fixture
def audit_integrity_manager():
    """Fixture que proporciona instancia de gestor de integridad."""
    return AuditIntegrityManager(secret_key="test_fixture_secret")


@pytest.fixture
def sample_audit_records(audit_integrity_manager):
    """Fixture con registros de auditoría de muestra."""
    events_data = [
        ("USER_LOGIN", 1, "auth", "login", {"method": "password"}),
        ("RESOURCE_ACCESS", 1, "files", "read", {"file": "document.pdf"}),
        ("USER_LOGOUT", 1, "auth", "logout", {"duration": 300})
    ]
    
    records = []
    for event_type, user_id, resource, action, details in events_data:
        record = audit_integrity_manager.create_audit_record(
            event_type=event_type,
            user_id=user_id,
            resource=resource,
            action=action,
            details=details
        )
        records.append(record)
    
    return records


@pytest.fixture
def audit_test_data():
    """Fixture con datos de prueba para tests de auditoría."""
    return {
        'events': [
            {
                'event_type': 'USER_REGISTRATION',
                'user_id': None,
                'resource': 'users',
                'action': 'create',
                'details': {'username': 'newuser', 'email': 'new@example.com'}
            },
            {
                'event_type': 'PASSWORD_CHANGE',
                'user_id': 1,
                'resource': 'authentication',
                'action': 'update',
                'details': {'password_strength': 'strong'}
            },
            {
                'event_type': 'ADMIN_ACCESS',
                'user_id': 2,
                'resource': 'admin_panel',
                'action': 'access',
                'details': {'elevated': True, 'reason': 'maintenance'}
            }
        ],
        'forensic_scenarios': [
            {
                'name': 'data_breach',
                'events': [
                    ('UNAUTHORIZED_LOGIN', 999, 'auth', 'login', {'suspicious': True}),
                    ('DATA_ACCESS', 999, 'database', 'read', {'tables': ['users', 'payments']}),
                    ('DATA_EXPORT', 999, 'database', 'export', {'records': 50000})
                ]
            }
        ]
    }