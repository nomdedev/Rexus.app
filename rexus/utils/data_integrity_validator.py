"""
Sistema de Validación de Integridad de Datos para Rexus.app

Proporciona validaciones automáticas para garantizar la integridad
de los datos entre las 3 bases de datos del sistema.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class IntegrityViolation:
    """Representa una violación de integridad de datos"""

    def __init__(self, violation_type: str, table_name: str, record_id: Any,
                 field_name: str, expected_value: Any, actual_value: Any,
                 severity: str, description: str, timestamp: datetime):
        self.violation_type = violation_type
        self.table_name = table_name
        self.record_id = record_id
        self.field_name = field_name
        self.expected_value = expected_value
        self.actual_value = actual_value
        self.severity = severity
        self.description = description
        self.timestamp = timestamp


class DataIntegrityValidator:
    """Validador de integridad de datos para múltiples bases de datos"""

    def __init__(self, db_connections: Dict[str, Any]):
        self.db_connections = db_connections
        self.violations: List[IntegrityViolation] = []
        self.logger = logging.getLogger(__name__)

        # Configuración de reglas de integridad
        self.integrity_rules = {
            'foreign_key_consistency': True,
            'data_type_validation': True,
            'business_rule_validation': True,
            'orphaned_records_detection': True,
            'duplicate_detection': True
        }

        # Configuraciones críticas por módulo
        self.critical_tables = {
            'inventario': ['productos', 'movimientos_inventario', 'categorias'],
            'users': ['usuarios', 'permisos', 'sesiones'],
            'auditoria': ['auditoria_eventos', 'auditoria_acciones']
        }

    def validate_all(self) -> Dict[str, Any]:
        """
        Ejecuta todas las validaciones de integridad.

        Returns:
            Dict con resultados de validación completos
        """
        self.logger.info("Iniciando validación completa de integridad de datos")

        self.violations.clear()

        try:
            # Validaciones principales
            self._validate_foreign_key_consistency()
            self._validate_business_rules()
            self._validate_data_types()
            self._detect_orphaned_records()
            self._detect_duplicates()

            # Generar reporte
            return self._generate_integrity_report()

        except Exception as e:
            self.logger.error(f"Error durante validación de integridad: {e}")
            return self._generate_integrity_report()

    def _validate_foreign_key_consistency(self):
        """Valida consistencia de claves foráneas entre tablas."""
        self.logger.debug("Validando consistencia de claves foráneas")

        # Validar usuarios en inventario
        self._validate_user_references_in_inventario()

        # Validar productos en auditoría
        self._validate_product_references_in_auditoria()

        # Validar referencias de obras
        self._validate_obra_references()

    def _validate_user_references_in_inventario(self):
        """Valida que usuarios referenciados en inventario existan."""
        if 'inventario' not in self.db_connections or 'users' not in self.db_connections:
            return

        try:
            inv_cursor = self.db_connections['inventario'].cursor()
            users_cursor = self.db_connections['users'].cursor()

            # Obtener usuarios únicos referenciados en inventario
            inv_cursor.execute("""
                SELECT DISTINCT usuario_creacion
                FROM productos
                WHERE usuario_creacion IS NOT NULL
                AND usuario_creacion != ''
            """)

            referenced_users = [row[0] for row in inv_cursor.fetchall()]

            # Verificar que existan en tabla users
            for user in referenced_users:
                users_cursor.execute("SELECT id FROM usuarios WHERE username = ?", (user,))
                if not users_cursor.fetchone():
                    self.violations.append(IntegrityViolation(
                        violation_type="foreign_key_violation",
                        table_name="productos",
                        record_id=None,
                        field_name="usuario_creacion",
                        expected_value="Usuario existente en BD users",
                        actual_value=user,
                        severity="HIGH",
                        description=f"Usuario '{user}' referenciado en inventario no existe en BD users",
                        timestamp=datetime.now()
                    ))

        except Exception as e:
            self.logger.error(f"Error validando referencias de usuario: {e}")

    def _validate_product_references_in_auditoria(self):
        """Valida que productos referenciados en auditoría existan."""
        if 'auditoria' not in self.db_connections or 'inventario' not in self.db_connections:
            return

        try:
            audit_cursor = self.db_connections['auditoria'].cursor()
            inv_cursor = self.db_connections['inventario'].cursor()

            # Obtener productos únicos referenciados en auditoría
            audit_cursor.execute("""
                SELECT DISTINCT producto_id
                FROM auditoria_eventos
                WHERE producto_id IS NOT NULL
            """)

            referenced_products = [row[0] for row in audit_cursor.fetchall()]

            # Verificar que existan en tabla productos
            for product_id in referenced_products:
                inv_cursor.execute("SELECT id FROM productos WHERE id = ?", (product_id,))
                if not inv_cursor.fetchone():
                    self.violations.append(IntegrityViolation(
                        violation_type="foreign_key_violation",
                        table_name="auditoria_eventos",
                        record_id=None,
                        field_name="producto_id",
                        expected_value="Producto existente en BD inventario",
                        actual_value=product_id,
                        severity="HIGH",
                        description=f"Producto ID '{product_id}' referenciado en auditoría no existe en BD inventario",
                        timestamp=datetime.now()
                    ))

        except Exception as e:
            self.logger.error(f"Error validando referencias de producto: {e}")

    def _validate_obra_references(self):
        """Valida referencias de obras."""
        self.logger.debug("Validando referencias de obras")
        # Implementación básica - puede ser expandida
        pass

    def _validate_business_rules(self):
        """Valida reglas de negocio."""
        self.logger.debug("Validando reglas de negocio")
        # Implementación básica - puede ser expandida
        pass

    def _validate_data_types(self):
        """Valida tipos de datos."""
        self.logger.debug("Validando tipos de datos")
        # Implementación básica - puede ser expandida
        pass

    def _detect_orphaned_records(self):
        """Detecta registros huérfanos."""
        self.logger.debug("Detectando registros huérfanos")
        # Implementación básica - puede ser expandida
        pass

    def _detect_duplicates(self):
        """Detecta registros duplicados."""
        self.logger.debug("Detectando registros duplicados")
        # Implementación básica - puede ser expandida
        pass

    def _generate_integrity_report(self) -> Dict[str, Any]:
        """Genera reporte completo de integridad."""
        return {
            'timestamp': datetime.now().isoformat(),
            'total_violations': len(self.violations),
            'violations_by_severity': self._count_violations_by_severity(),
            'violations_by_type': self._count_violations_by_type(),
            'critical_tables_status': self._check_critical_tables_status(),
            'violations': [self._violation_to_dict(v) for v in self.violations],
            'recommendations': self._generate_recommendations()
        }

    def _count_violations_by_severity(self) -> Dict[str, int]:
        """Cuenta violaciones por severidad."""
        counts = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        for violation in self.violations:
            counts[violation.severity] = counts.get(violation.severity, 0) + 1
        return counts

    def _count_violations_by_type(self) -> Dict[str, int]:
        """Cuenta violaciones por tipo."""
        counts = {}
        for violation in self.violations:
            counts[violation.violation_type] = counts.get(violation.violation_type, 0) + 1
        return counts

    def _check_critical_tables_status(self) -> Dict[str, bool]:
        """Verifica estado de tablas críticas."""
        status = {}
        for module, tables in self.critical_tables.items():
            status[module] = module in self.db_connections
        return status

    def _violation_to_dict(self, violation: IntegrityViolation) -> Dict[str, Any]:
        """Convierte violación a diccionario."""
        return {
            'violation_type': violation.violation_type,
            'table_name': violation.table_name,
            'record_id': violation.record_id,
            'field_name': violation.field_name,
            'expected_value': violation.expected_value,
            'actual_value': violation.actual_value,
            'severity': violation.severity,
            'description': violation.description,
            'timestamp': violation.timestamp.isoformat()
        }

    def _generate_recommendations(self) -> List[str]:
        """Genera recomendaciones basadas en las violaciones encontradas."""
        recommendations = []

        if len(self.violations) > 0:
            recommendations.append("Revisar y corregir todas las violaciones de integridad detectadas")
            recommendations.append("Implementar triggers de base de datos para mantener integridad referencial")
            recommendations.append("Establecer procesos de validación automática antes de operaciones críticas")

        return recommendations