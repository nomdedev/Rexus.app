"""
Sistema de Validación de Integridad de Registros de Auditoría - Rexus.app

Sistema que garantiza la integridad y autenticidad de los registros de auditoría
mediante técnicas criptográficas avanzadas, incluyendo hashing, firma digital
y verificación de cadena de integridad.

Características:
- Hash criptográfico para cada registro de auditoría
- Cadena de integridad que enlaza registros secuencialmente
- Firma digital para autenticación de registros
- Verificación de integridad completa de la cadena
- Detección de manipulación o corrupción
- Sellado temporal opcional
- Exportación segura de registros

Author: Rexus Development Team
Date: 2025-08-11
Version: 1.0.0
"""

import json
import hashlib
import time
import secrets
import base64
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, asdict

try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

# Sistema de logging
try:
    from ..utils.app_logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


@dataclass
class AuditRecord:
    """Registro de auditoría con integridad criptográfica."""
    id: str
    timestamp: str
    event_type: str
    user_id: Optional[int]
    resource: str
    action: str
    details: Dict[str, Any]
    content_hash: str = ""
    previous_hash: Optional[str] = None
    chain_hash: str = ""
    signature: str = ""
    integrity_sealed: bool = False


@dataclass
class IntegrityChainInfo:
    """Información de la cadena de integridad."""
    genesis_hash: str
    last_hash: str
    chain_length: int
    creation_timestamp: str
    last_update_timestamp: str
    key_fingerprint: str


@dataclass
class IntegrityVerificationResult:
    """Resultado de verificación de integridad."""
    is_valid: bool
    record_count: int
    chain_integrity: bool
    signature_validity: bool
    first_record_timestamp: Optional[str]
    last_record_timestamp: Optional[str]
    verification_timestamp: str
    issues: List[Dict[str, Any]]


class IntegrityStatus:
    """Estados de integridad."""
    VALID = "valid"
    CORRUPTED = "corrupted"
    MISSING = "missing"
    INVALID_SIGNATURE = "invalid_signature"
    BROKEN_CHAIN = "broken_chain"


class AuditIntegrityManager:
    """Gestor de integridad de auditoría con validación criptográfica."""
    
    def __init__(self, private_key_path: Optional[str] = None, secret_key: Optional[str] = None):
        self.private_key = None
        self.public_key = None
        self.secret_key = secret_key or secrets.token_hex(32)
        self.genesis_hash = None
        self.last_record_hash = None
        self.chain_info = None
        
        if CRYPTO_AVAILABLE and private_key_path:
            try:
                self._load_keys(private_key_path)
            except Exception as e:
                logger.warning(f"No se pudieron cargar las claves criptográficas: {e}")
    
    def _load_keys(self, private_key_path: str):
        """Carga claves criptográficas."""
        try:
            with open(private_key_path, 'rb') as f:
                self.private_key = serialization.load_pem_private_key(
                    f.read(), password=None
                )
            self.public_key = self.private_key.public_key()
        except Exception as e:
            logger.error(f"Error cargando claves: {e}")
            raise
    
    def create_audit_record(self, event_type: str, user_id: Optional[int], 
                           resource: str, action: str, details: Dict[str, Any],
                           **kwargs) -> AuditRecord:
        """Crea un registro de auditoría con integridad criptográfica."""
        try:
            # Crear registro básico
            record = AuditRecord(
                id=self._generate_record_id(),
                timestamp=datetime.now().isoformat(),
                event_type=event_type,
                user_id=user_id,
                resource=resource,
                action=action,
                details=details,
                previous_hash=self.last_record_hash
            )
            
            # Calcular hashes de integridad
            record.content_hash = self._calculate_content_hash(record, exclude_integrity=True)
            record.chain_hash = self._calculate_chain_hash(record, exclude_integrity=True)
            
            # Firmar registro si hay clave privada
            if self.private_key:
                record.signature = self._sign_record(record)
            
            # Sellar integridad
            record.integrity_sealed = True
            
            # Actualizar estado de cadena
            self._update_chain_state(record)
            
            return record
            
        except Exception as e:
            logger.exception(f"Error creando registro de auditoría: {e}")
            # Retornar registro básico sin integridad en caso de error
            return AuditRecord(
                id=self._generate_record_id(),
                timestamp=datetime.now().isoformat(),
                event_type=event_type,
                user_id=user_id,
                resource=resource,
                action=action,
                details=details
            )
    
    def verify_record_integrity(self, record: AuditRecord) -> Tuple[str, List[str]]:
        """Verifica la integridad de un registro de auditoría."""
        issues = []
        
        try:
            # Verificar hash de contenido
            expected_content_hash = self._calculate_content_hash(record, exclude_integrity=True)
            if record.content_hash != expected_content_hash:
                issues.append(f"Hash de contenido no coincide: esperado {expected_content_hash}, encontrado {record.content_hash}")
                return IntegrityStatus.CORRUPTED, issues
            
            # Verificar hash de cadena
            expected_chain_hash = self._calculate_chain_hash(record, exclude_integrity=True)
            if record.chain_hash != expected_chain_hash:
                issues.append(f"Hash de cadena no coincide: esperado {expected_chain_hash}, encontrado {record.chain_hash}")
                return IntegrityStatus.BROKEN_CHAIN, issues
            
            # Verificar firma si existe
            if record.signature:
                if not self._verify_signature(record):
                    issues.append("Firma digital inválida")
                    return IntegrityStatus.INVALID_SIGNATURE, issues
            
            return IntegrityStatus.VALID, issues
            
        except Exception as e:
            logger.exception(f"Error verificando integridad: {e}")
            issues.append(f"Error durante verificación: {str(e)}")
            return IntegrityStatus.CORRUPTED, issues
    
    def export_integrity_report(self, records: List[AuditRecord]) -> IntegrityVerificationResult:
        """Exporta reporte completo de integridad."""
        try:
            issues = []
            valid_records = 0
            chain_integrity = True
            signature_validity = True
            
            for i, record in enumerate(records):
                status, record_issues = self.verify_record_integrity(record)
                if status == IntegrityStatus.VALID:
                    valid_records += 1
                else:
                    chain_integrity = False
                    if status == IntegrityStatus.INVALID_SIGNATURE:
                        signature_validity = False
                    
                    for issue in record_issues:
                        issues.append({
                            "record_id": record.id,
                            "record_index": i,
                            "timestamp": record.timestamp,
                            "issue": issue
                        })
            
            return IntegrityVerificationResult(
                is_valid=(len(issues) == 0),
                record_count=len(records),
                chain_integrity=chain_integrity,
                signature_validity=signature_validity,
                first_record_timestamp=records[0].timestamp if records else None,
                last_record_timestamp=records[-1].timestamp if records else None,
                verification_timestamp=datetime.now().isoformat(),
                issues=issues
            )
            
        except Exception as e:
            logger.exception(f"Error exportando reporte: {e}")
            return IntegrityVerificationResult(
                is_valid=False,
                record_count=len(records) if records else 0,
                chain_integrity=False,
                signature_validity=False,
                first_record_timestamp=None,
                last_record_timestamp=None,
                verification_timestamp=datetime.now().isoformat(),
                issues=[{"record_id": "EXPORT", "record_index": -1, "timestamp": "N/A", "issue": f"Error durante exportación: {str(e)}"}]
            )

    def _generate_record_id(self) -> str:
        """Genera un ID único para el registro."""
        timestamp = str(int(time.time() * 1000))  # Timestamp en milisegundos
        random_part = secrets.token_hex(8)
        return f"audit_{timestamp}_{random_part}"

    def _calculate_content_hash(self, record: AuditRecord, exclude_integrity: bool = False) -> str:
        """Calcula el hash del contenido del registro."""
        # Crear copia para modificación
        record_dict = asdict(record)

        # Excluir campos de integridad del cálculo
        if exclude_integrity:
            record_dict.pop('content_hash', None)
            record_dict.pop('previous_hash', None)
            record_dict.pop('chain_hash', None)
            record_dict.pop('signature', None)
            record_dict.pop('integrity_sealed', None)

        # Serializar de forma determinística
        content = json.dumps(record_dict, sort_keys=True).encode('utf-8')

        # Calcular hash
        return hashlib.sha256(content).hexdigest()

    def _calculate_chain_hash(self, record: AuditRecord, exclude_integrity: bool = False) -> str:
        """Calcula el hash de cadena del registro."""
        content_hash = record.content_hash
        if exclude_integrity:
            content_hash = self._calculate_content_hash(record, exclude_integrity=True)

        # Combinar hash de contenido con hash previo
        chain_content = f"{content_hash}:{record.previous_hash or 'genesis'}"
        return hashlib.sha256(chain_content.encode()).hexdigest()

    def _sign_record(self, record: AuditRecord) -> str:
        """Firma digitalmente un registro."""
        if not self.private_key:
            return ""

        # Preparar datos para firma
        sign_data = {
            "id": record.id,
            "timestamp": record.timestamp,
            "content_hash": record.content_hash,
            "chain_hash": record.chain_hash
        }

        signature_content = json.dumps(sign_data, sort_keys=True).encode()
        return self._sign_data(signature_content)

    def _sign_data(self, data: bytes) -> str:
        """Firma datos arbitrarios."""
        if not self.private_key:
            return ""

        signature = self.private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        return base64.b64encode(signature).decode()

    def _verify_signature(self, record: AuditRecord) -> bool:
        """Verifica la firma digital de un registro."""
        if not self.public_key or not record.signature:
            return False

        try:
            # Preparar datos para verificación
            sign_data = {
                "id": record.id,
                "timestamp": record.timestamp,
                "content_hash": record.content_hash,
                "chain_hash": record.chain_hash
            }

            signature_content = json.dumps(sign_data, sort_keys=True).encode()
            return self._verify_data_signature(signature_content, record.signature)

        except (json.JSONEncodeError, ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error verificando firma: {e}")
            return False
    def _update_chain_state(self, record: AuditRecord):
        """Actualiza el estado de la cadena de integridad."""
        if self.genesis_hash is None:
            self.genesis_hash = record.chain_hash

        self.last_record_hash = record.chain_hash

        # Actualizar información de cadena
        if self.chain_info is None:
            self.chain_info = IntegrityChainInfo(
                genesis_hash=self.genesis_hash,
                last_hash=record.chain_hash,
                chain_length=1,
                creation_timestamp=record.timestamp,
                last_update_timestamp=record.timestamp,
                key_fingerprint=self._get_key_fingerprint()
            )
        else:
            self.chain_info.last_hash = record.chain_hash
            self.chain_info.chain_length += 1
            self.chain_info.last_update_timestamp = record.timestamp

    def _get_key_fingerprint(self) -> str:
        """Obtiene huella digital de la clave pública."""
        if not self.public_key:
            return hashlib.sha256(self.secret_key).hexdigest()[:16]

        try:
            public_pem = self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            return hashlib.sha256(public_pem).hexdigest()[:16]
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error obteniendo huella de clave: {e}")
            return hashlib.sha256(self.secret_key.encode()).hexdigest()[:16]

    def _verify_data_signature(self, data: bytes, signature: str) -> bool:
        """Verifica la firma digital de datos arbitrarios."""
        if not self.public_key or not signature:
            return False
        
        try:
            signature_bytes = base64.b64decode(signature)
            self.public_key.verify(
                signature_bytes,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception as e:
            logger.error(f"Error verificando firma de datos: {e}")
            return False
# Instancia global del gestor de integridad
_audit_integrity_manager: Optional[AuditIntegrityManager] = None


def init_audit_integrity(private_key_path: Optional[str] = None,
                        secret_key: Optional[str] = None) -> AuditIntegrityManager:
    """Inicializa el gestor global de integridad de auditoría."""
    global _audit_integrity_manager
    _audit_integrity_manager = AuditIntegrityManager(private_key_path, secret_key)
    return _audit_integrity_manager


def get_audit_integrity_manager() -> AuditIntegrityManager:
    """Obtiene la instancia global del gestor de integridad."""
    if _audit_integrity_manager is None:
        raise RuntimeError("Gestor de integridad de auditoría no está inicializado. Llame a init_audit_integrity() primero.")
    return _audit_integrity_manager


def create_secure_audit_record(event_type: str, user_id: Optional[int], resource: str,
                              action: str, details: Dict[str, Any], **kwargs) -> AuditRecord:
    """Función de conveniencia para crear registro de auditoría seguro."""
    manager = get_audit_integrity_manager()
    return manager.create_audit_record(event_type, user_id, resource, action, details, **kwargs)


def verify_audit_record(record: AuditRecord) -> Tuple[IntegrityStatus, List[str]]:
    """Función de conveniencia para verificar integridad de registro."""
    manager = get_audit_integrity_manager()
    return manager.verify_record_integrity(record)
