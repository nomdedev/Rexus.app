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

        except (json.JSONEncodeError, ValueError, TypeError, AttributeError) as e:
            
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
