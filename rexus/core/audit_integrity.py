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
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict, field
from enum import Enum
import base64

try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives.serialization import load_pem_private_key
    from cryptography.hazmat.backends import default_backend
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False

try:
    from rexus.utils.secure_logger import log_security_event
except ImportError:
    def log_security_event(event_type: str, details: dict, severity: str = "INFO"):
        print(f"AUDIT LOG [{severity}] {event_type}: {details}")


class IntegrityStatus(Enum):
    """Estado de integridad de registros de auditoría."""
    VALID = "valid"
    CORRUPTED = "corrupted"
    MISSING = "missing"
    TAMPERED = "tampered"
    SIGNATURE_INVALID = "signature_invalid"
    CHAIN_BROKEN = "chain_broken"


@dataclass
class AuditRecord:
    """Registro de auditoría con metadatos de integridad."""
    id: str
    timestamp: str
    event_type: str
    user_id: Optional[int]
    resource: str
    action: str
    details: Dict[str, Any]
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None

    # Campos de integridad
    content_hash: Optional[str] = None
    previous_hash: Optional[str] = None
    chain_hash: Optional[str] = None
    signature: Optional[str] = None
    integrity_sealed: bool = False
    created_by_system: str = "rexus_audit"


@dataclass
class IntegrityReport:
    """Reporte de verificación de integridad."""
    total_records: int
    valid_records: int
    corrupted_records: int
    missing_records: int
    tampered_records: int
    chain_integrity: bool
    signature_validity: bool
    first_record_timestamp: Optional[str]
    last_record_timestamp: Optional[str]
    verification_timestamp: str
    issues: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class IntegrityChainInfo:
    """Información de cadena de integridad."""
    genesis_hash: str
    last_hash: str
    chain_length: int
    creation_timestamp: str
    last_update_timestamp: str
    key_fingerprint: str


class AuditIntegrityManager:
    """
    Gestor de integridad para registros de auditoría.

    Proporciona funcionalidad completa para:
    - Crear registros con integridad garantizada
    - Verificar integridad individual y de cadena
    - Detectar manipulación o corrupción
    - Generar reportes de integridad
    - Sellar registros criptográficamente
    """

    def __init__(self, private_key_path: Optional[str] = None,
                 secret_key: Optional[str] = None):
        """
        Inicializa el gestor de integridad de auditoría.

        Args:
            private_key_path: Ruta a clave privada para firma digital
            secret_key: Clave secreta para HMAC (se genera una si no se proporciona)
        """
        if not CRYPTOGRAPHY_AVAILABLE:
            raise ImportError("Paquete 'cryptography' es requerido para integridad de auditoría")

        # Inicializar claves criptográficas
        self._init_crypto_keys(private_key_path, secret_key)

        # Estado de la cadena de integridad
        self.chain_info: Optional[IntegrityChainInfo] = None
        self.genesis_hash: Optional[str] = None
        self.last_record_hash: Optional[str] = None

        # Configuración
        self.hash_algorithm = hashlib.sha256
        self.signature_enabled = self.private_key is not None

        log_security_event(
            "AUDIT_INTEGRITY_MANAGER_INITIALIZED",
            {
                "signature_enabled": self.signature_enabled,
                "hash_algorithm": "SHA256"
            },
            "INFO"
        )

    def _init_crypto_keys(self, private_key_path: Optional[str], secret_key: Optional[str]):
        """Inicializa las claves criptográficas."""
        # Clave secreta para HMAC
        if secret_key is None:
            secret_key = secrets.token_urlsafe(32)
        self.secret_key = secret_key.encode() if isinstance(secret_key, str) else secret_key

        # Claves RSA para firma digital
        self.private_key = None
        self.public_key = None

        if private_key_path:
            try:
                with open(private_key_path, 'rb') as key_file:
                    self.private_key = load_pem_private_key(
                        key_file.read(),
                        password=None,
                        backend=default_backend()
                    )
                    self.public_key = self.private_key.public_key()
            except Exception as e:
                log_security_event(
                    "AUDIT_KEY_LOAD_ERROR",
                    {"error": str(e), "key_path": private_key_path},
                    "WARNING"
                )

        # Generar claves si no se proporcionaron
        if self.private_key is None:
            self.private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            self.public_key = self.private_key.public_key()

    def create_audit_record(self,
                          event_type: str,
                          user_id: Optional[int],
                          resource: str,
                          action: str,
                          details: Dict[str, Any],
                          ip_address: Optional[str] = None,
                          user_agent: Optional[str] = None,
                          session_id: Optional[str] = None) -> AuditRecord:
        """
        Crea un registro de auditoría con integridad garantizada.

        Args:
            event_type: Tipo de evento de auditoría
            user_id: ID del usuario (si aplica)
            resource: Recurso afectado
            action: Acción realizada
            details: Detalles adicionales del evento
            ip_address: Dirección IP del cliente
            user_agent: User agent del cliente
            session_id: ID de sesión

        Returns:
            Registro de auditoría con campos de integridad
        """
        try:
            # Crear ID único para el registro
            record_id = self._generate_record_id()
            timestamp = datetime.now().isoformat()

            # Crear registro base
            record = AuditRecord(
                id=record_id,
                timestamp=timestamp,
                event_type=event_type,
                user_id=user_id,
                resource=resource,
                action=action,
                details=details,
                ip_address=ip_address,
                user_agent=user_agent,
                session_id=session_id
            )

            # Calcular hash del contenido
            record.content_hash = self._calculate_content_hash(record)

            # Establecer hash previo y de cadena
            record.previous_hash = self.last_record_hash
            record.chain_hash = self._calculate_chain_hash(record)

            # Firmar registro si está habilitado
            if self.signature_enabled:
                record.signature = self._sign_record(record)

            # Sellar registro
            record.integrity_sealed = True

            # Actualizar estado de cadena
            self._update_chain_state(record)

            log_security_event(
                "AUDIT_RECORD_CREATED",
                {
                    "record_id": record_id,
                    "event_type": event_type,
                    "resource": resource,
                    "action": action,
                    "user_id": user_id,
                    "content_hash": record.content_hash[:16] + "..."
                },
                "DEBUG"
            )

            return record

        except Exception as e:
            log_security_event(
                "AUDIT_RECORD_CREATION_ERROR",
                {
                    "event_type": event_type,
                    "resource": resource,
                    "error": str(e)
                },
                "ERROR"
            )
            raise

    def verify_record_integrity(self, record: AuditRecord) -> Tuple[IntegrityStatus, List[str]]:
        """
        Verifica la integridad de un registro individual.

        Args:
            record: Registro a verificar

        Returns:
            Tupla con estado de integridad y lista de problemas encontrados
        """
        issues = []

        try:
            # Verificar si el registro está sellado
            if not record.integrity_sealed:
                issues.append("Registro no está sellado para integridad")
                return IntegrityStatus.TAMPERED, issues

            # Verificar hash del contenido
            expected_content_hash = self._calculate_content_hash(record, exclude_integrity=True)
            if record.content_hash != expected_content_hash:
                issues.append(f"Hash de contenido inválido: esperado {expected_content_hash[:16]}..., obtenido {record.content_hash[:16] if record.content_hash else 'None'}...")
                return IntegrityStatus.CORRUPTED, issues

            # Verificar firma si está presente
            if record.signature and self.signature_enabled:
                if not self._verify_signature(record):
                    issues.append("Firma digital inválida")
                    return IntegrityStatus.SIGNATURE_INVALID, issues

            # Verificar hash de cadena
            expected_chain_hash = self._calculate_chain_hash(record, exclude_integrity=True)
            if record.chain_hash != expected_chain_hash:
                issues.append(f"Hash de cadena inválido: esperado {expected_chain_hash[:16]}..., obtenido {record.chain_hash[:16] if record.chain_hash else 'None'}...")
                return IntegrityStatus.CHAIN_BROKEN, issues

            return IntegrityStatus.VALID, []

        except Exception as e:
            issues.append(f"Error durante verificación: {str(e)}")
            log_security_event(
                "AUDIT_RECORD_VERIFICATION_ERROR",
                {"record_id": record.id, "error": str(e)},
                "ERROR"
            )
            return IntegrityStatus.CORRUPTED, issues

    def verify_chain_integrity(self, records: List[AuditRecord]) -> IntegrityReport:
        """
        Verifica la integridad de una cadena completa de registros.

        Args:
            records: Lista de registros ordenados cronológicamente

        Returns:
            Reporte completo de integridad de la cadena
        """
        report = IntegrityReport(
            total_records=len(records),
            valid_records=0,
            corrupted_records=0,
            missing_records=0,
            tampered_records=0,
            chain_integrity=True,
            signature_validity=True,
            first_record_timestamp=records[0].timestamp if records else None,
            last_record_timestamp=records[-1].timestamp if records else None,
            verification_timestamp=datetime.now().isoformat()
        )

        if not records:
            return report

        try:
            previous_hash = None

            for i, record in enumerate(records):
                # Verificar integridad individual
                status, issues = self.verify_record_integrity(record)

                if status == IntegrityStatus.VALID:
                    report.valid_records += 1
                elif status == IntegrityStatus.CORRUPTED:
                    report.corrupted_records += 1
                    report.chain_integrity = False
                elif status == IntegrityStatus.TAMPERED:
                    report.tampered_records += 1
                    report.chain_integrity = False
                elif status == IntegrityStatus.SIGNATURE_INVALID:
                    report.signature_validity = False

                if issues:
                    report.issues.extend([
                        {
                            "record_id": record.id,
                            "record_index": i,
                            "timestamp": record.timestamp,
                            "issue": issue
                        } for issue in issues
                    ])

                # Verificar enlace con registro anterior
                if i > 0:  # No el primer registro
                    if record.previous_hash != previous_hash:
                        report.chain_integrity = False
                        report.issues.append({
                            "record_id": record.id,
                            "record_index": i,
                            "timestamp": record.timestamp,
                            "issue": f"Hash previo no coincide: esperado {previous_hash[:16] if previous_hash else 'None'}..., obtenido {record.previous_hash[:16] if record.previous_hash else 'None'}..."
                        })

                # Actualizar hash previo para siguiente iteración
                previous_hash = record.chain_hash

            log_security_event(
                "AUDIT_CHAIN_VERIFICATION_COMPLETED",
                {
                    "total_records": report.total_records,
                    "valid_records": report.valid_records,
                    "chain_integrity": report.chain_integrity,
                    "issues_found": len(report.issues)
                },
                "INFO"
            )

        except Exception as e:
            log_security_event(
                "AUDIT_CHAIN_VERIFICATION_ERROR",
                {"error": str(e)},
                "ERROR"
            )
            report.chain_integrity = False
            report.issues.append({
                "record_id": "N/A",
                "record_index": -1,
                "timestamp": "N/A",
                "issue": f"Error crítico durante verificación: {str(e)}"
            })

        return report

    def export_chain_proof(self, records: List[AuditRecord]) -> Dict[str, Any]:
        """
        Exporta prueba criptográfica de integridad de la cadena.

        Args:
            records: Lista de registros a exportar

        Returns:
            Diccionario con prueba de integridad exportable
        """
        try:
            # Verificar integridad antes de exportar
            report = self.verify_chain_integrity(records)

            if not report.chain_integrity:
                raise ValueError("No se puede exportar cadena con integridad comprometida")

            # Calcular hash de toda la cadena
            chain_content = json.dumps([
                {
                    "id": r.id,
                    "timestamp": r.timestamp,
                    "content_hash": r.content_hash,
                    "chain_hash": r.chain_hash
                }
                for r in records
            ], sort_keys=True)

            full_chain_hash = hashlib.sha256(chain_content.encode()).hexdigest()

            # Crear prueba de exportación
            export_proof = {
                "export_timestamp": datetime.now().isoformat(),
                "total_records": len(records),
                "first_record_timestamp": records[0].timestamp if records else None,
                "last_record_timestamp": records[-1].timestamp if records else None,
                "full_chain_hash": full_chain_hash,
                "integrity_report": asdict(report),
                "key_fingerprint": self._get_key_fingerprint(),
                "records": [asdict(record) for record in records]
            }

            # Firmar la prueba de exportación
            if self.signature_enabled:
                export_content = json.dumps(export_proof, sort_keys=True).encode()
                signature = self._sign_data(export_content)
                export_proof["export_signature"] = signature

            log_security_event(
                "AUDIT_CHAIN_EXPORTED",
                {
                    "record_count": len(records),
                    "chain_hash": full_chain_hash[:16] + "...",
                    "integrity_valid": report.chain_integrity
                },
                "INFO"
            )

            return export_proof

        except Exception as e:
            log_security_event(
                "AUDIT_CHAIN_EXPORT_ERROR",
                {"error": str(e)},
                "ERROR"
            )
            raise

    def import_and_verify_chain(self,
export_data: Dict[str,
        Any]) -> Tuple[bool,
        IntegrityReport]:
        """
        Importa y verifica una cadena de auditoría exportada.

        Args:
            export_data: Datos exportados de cadena de auditoría

        Returns:
            Tupla con resultado de verificación y reporte detallado
        """
        try:
            # Verificar firma de exportación si está presente
            if "export_signature" in export_data and self.signature_enabled:
                export_copy = export_data.copy()
                export_signature = export_copy.pop("export_signature")
                export_content = json.dumps(export_copy, sort_keys=True).encode()

                if not self._verify_data_signature(export_content, export_signature):
                    log_security_event(
                        "AUDIT_IMPORT_SIGNATURE_INVALID",
                        {"export_timestamp": export_data.get("export_timestamp")},
                        "WARNING"
                    )
                    return False, IntegrityReport(
                        total_records=0,
                        valid_records=0,
                        corrupted_records=0,
                        missing_records=0,
                        tampered_records=0,
                        chain_integrity=False,
                        signature_validity=False,
                        first_record_timestamp=None,
                        last_record_timestamp=None,
                        verification_timestamp=datetime.now().isoformat(),
                        issues=[{"record_id": "EXPORT", "record_index": -1, "timestamp": "N/A", "issue": "Firma de exportación inválida"}]
                    )

            # Reconstruir registros
            records = []
            for record_data in export_data.get("records", []):
                record = AuditRecord(**record_data)
                records.append(record)

            # Verificar integridad de la cadena importada
            report = self.verify_chain_integrity(records)

            # Verificar hash de cadena completa
            if "full_chain_hash" in export_data:
                chain_content = json.dumps([
                    {
                        "id": r.id,
                        "timestamp": r.timestamp,
                        "content_hash": r.content_hash,
                        "chain_hash": r.chain_hash
                    }
                    for r in records
                ], sort_keys=True)

                calculated_hash = hashlib.sha256(chain_content.encode()).hexdigest()
                if calculated_hash != export_data["full_chain_hash"]:
                    report.chain_integrity = False
                    report.issues.append({
                        "record_id": "CHAIN",
                        "record_index": -1,
                        "timestamp": "N/A",
                        "issue": "Hash de cadena completa no coincide con exportación"
                    })

            log_security_event(
                "AUDIT_CHAIN_IMPORTED",
                {
                    "record_count": len(records),
                    "integrity_valid": report.chain_integrity,
                    "export_timestamp": export_data.get("export_timestamp")
                },
                "INFO"
            )

            return report.chain_integrity, report

        except Exception as e:
            log_security_event(
                "AUDIT_CHAIN_IMPORT_ERROR",
                {"error": str(e)},
                "ERROR"
            )
            return False, IntegrityReport(
                total_records=0,
                valid_records=0,
                corrupted_records=0,
                missing_records=0,
                tampered_records=0,
                chain_integrity=False,
                signature_validity=False,
                first_record_timestamp=None,
                last_record_timestamp=None,
                verification_timestamp=datetime.now().isoformat(),
                issues=[{"record_id": "IMPORT", "record_index": -1, "timestamp": "N/A", "issue": f"Error durante importación: {str(e)}"}]
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

        except Exception:
            return False

    def _verify_data_signature(self, data: bytes, signature: str) -> bool:
        """Verifica la firma de datos arbitrarios."""
        if not self.public_key:
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

        except Exception:
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
        except Exception:
            return "unknown"


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
    return manager.create_audit_record(event_type,
user_id,
        resource,
        action,
        details,
        **kwargs)


def verify_audit_record(record: AuditRecord) -> Tuple[IntegrityStatus, List[str]]:
    """Función de conveniencia para verificar integridad de registro."""
    manager = get_audit_integrity_manager()
    return manager.verify_record_integrity(record)
