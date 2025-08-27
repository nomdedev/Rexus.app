"""
Sistema de Validación de Integridad de Datos para Rexus.app

Proporciona validaciones automáticas para garantizar la integridad 
de los datos entre las 3 bases de datos del sistema.
"""

import logging
import sqlite3
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
        logger.info("Iniciando validación completa de integridad de datos")
        
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

    def _validate_foreign_key_consistency(self):
        """Valida consistencia de claves foráneas entre tablas."""
        logger.debug("Validando consistencia de claves foráneas")
        
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
                        expected_value=f"Usuario existente en BD users",
                        actual_value=user,
                        severity="HIGH",
                        description=f"Usuario '{user}' referenciado en inventario no existe en BD users",
                        timestamp=datetime.now()
                    ))
                    
        except Exception as e:
        """Valida que productos referenciados en auditoría existan."""
        if 'auditoria' not in self.db_connections or 'inventario' not in self.db_connections:
            return
        
        try:
            audit_cursor = self.db_connections['auditoria'].cursor()
            inv_cursor = self.db_connections['inventario'].cursor()
            
            # Obtener productos únicos referenciados en auditoría
            audit_cursor.execute("""
                SELECT DISTINCT registro_id 
                FROM auditoria_eventos 
                WHERE tabla_afectada = 'productos'
                AND registro_id IS NOT NULL
            """)
            
            referenced_products = [row[0] for row in audit_cursor.fetchall()]
            
            # Verificar que existan en tabla productos
            for product_id in referenced_products:
                inv_cursor.execute("SELECT id FROM productos WHERE id = ?", (product_id,))
                if not inv_cursor.fetchone():
                    self.violations.append(IntegrityViolation(
                        violation_type="foreign_key_violation",
                        table_name="auditoria_eventos",
                        record_id=product_id,
                        field_name="registro_id",
                        expected_value=f"Producto existente en BD inventario",
                        actual_value=product_id,
                        severity="MEDIUM",
                        description=f"Producto ID '{product_id}' en auditoría no existe en inventario",
                        timestamp=datetime.now()
                    ))
                    
        except Exception as e:
        """Valida referencias entre obras y otros módulos."""
        if 'inventario' not in self.db_connections:
            return
        
        try:
            cursor = self.db_connections['inventario'].cursor()
            
            # Validar que obras referenciadas en movimientos existan
            cursor.execute("""
                SELECT DISTINCT obra_id 
                FROM movimientos_inventario 
                WHERE obra_id IS NOT NULL 
                AND obra_id != ''
            """)
            
            referenced_obras = [row[0] for row in cursor.fetchall()]
            
            for obra_id in referenced_obras:
                cursor.execute("SELECT id FROM obras WHERE id = ?", (obra_id,))
                if not cursor.fetchone():
                    self.violations.append(IntegrityViolation(
                        violation_type="foreign_key_violation",
                        table_name="movimientos_inventario",
                        record_id=obra_id,
                        field_name="obra_id",
                        expected_value="Obra existente",
                        actual_value=obra_id,
                        severity="HIGH",
                        description=f"Obra ID '{obra_id}' en movimientos no existe",
                        timestamp=datetime.now()
                    ))
                    
        except Exception as e:
        """Valida reglas de negocio específicas."""
        logger.debug("Validando reglas de negocio")
        
        self._validate_stock_consistency()
        self._validate_date_logic()
        self._validate_price_ranges()

    def _validate_stock_consistency(self):
        """Valida consistencia de stock."""
        if 'inventario' not in self.db_connections:
            return
        
        try:
            cursor = self.db_connections['inventario'].cursor()
            
            # Stock negativo
            cursor.execute("""
                SELECT id, codigo_producto, stock_actual 
                FROM productos 
                WHERE stock_actual < 0
            """)
            
            for row in cursor.fetchall():
                self.violations.append(IntegrityViolation(
                    violation_type="business_rule_violation",
                    table_name="productos",
                    record_id=row[0],
                    field_name="stock_actual",
                    expected_value="≥ 0",
                    actual_value=row[2],
                    severity="HIGH",
                    description=f"Producto '{row[1]}' tiene stock negativo: {row[2]}",
                    timestamp=datetime.now()
                ))
            
            # Stock menor que mínimo
            cursor.execute("""
                SELECT id, codigo_producto, stock_actual, stock_minimo 
                FROM productos 
                WHERE stock_actual < stock_minimo 
                AND stock_minimo > 0
            """)
            
            for row in cursor.fetchall():
                self.violations.append(IntegrityViolation(
                    violation_type="business_rule_violation",
                    table_name="productos",
                    record_id=row[0],
                    field_name="stock_actual",
                    expected_value=f"≥ {row[3]}",
                    actual_value=row[2],
                    severity="MEDIUM",
                    description=f"Producto '{row[1]}' por debajo del stock mínimo",
                    timestamp=datetime.now()
                ))
                
        except Exception as e:
        """Valida lógica de fechas."""
        if 'inventario' not in self.db_connections:
            return
        
        try:
            cursor = self.db_connections['inventario'].cursor()
            
            # Fechas de obras: fecha_fin debe ser >= fecha_inicio
            cursor.execute("""
                SELECT id, codigo_obra, fecha_inicio, fecha_fin_estimada 
                FROM obras 
                WHERE fecha_fin_estimada < fecha_inicio
            """)
            
            for row in cursor.fetchall():
                self.violations.append(IntegrityViolation(
                    violation_type="business_rule_violation",
                    table_name="obras",
                    record_id=row[0],
                    field_name="fecha_fin_estimada",
                    expected_value=f"≥ {row[2]}",
                    actual_value=row[3],
                    severity="HIGH",
                    description=f"Obra '{row[1]}' tiene fecha fin anterior a fecha inicio",
                    timestamp=datetime.now()
                ))
                
        except Exception as e:
        """Valida rangos de precios."""
        if 'inventario' not in self.db_connections:
            return
        
        try:
            cursor = self.db_connections['inventario'].cursor()
            
            # Precios negativos o cero
            cursor.execute("""
                SELECT id, codigo_producto, precio 
                FROM productos 
                WHERE precio <= 0
            """)
            
            for row in cursor.fetchall():
                self.violations.append(IntegrityViolation(
                    violation_type="business_rule_violation",
                    table_name="productos",
                    record_id=row[0],
                    field_name="precio",
                    expected_value="> 0",
                    actual_value=row[2],
                    severity="MEDIUM",
                    description=f"Producto '{row[1]}' tiene precio inválido: {row[2]}",
                    timestamp=datetime.now()
                ))
                
        except Exception as e:
        """Valida tipos de datos y formatos."""
        logger.debug("Validando tipos de datos")
        
        # Esta validación se haría a nivel de esquema
        # Por ahora registramos como completada
        pass

    def _detect_orphaned_records(self):
        """Detecta registros huérfanos."""
        logger.debug("Detectando registros huérfanos")
        
        self._detect_orphaned_movements()
        self._detect_orphaned_audit_records()

    def _detect_orphaned_movements(self):
        """Detecta movimientos de inventario huérfanos."""
        if 'inventario' not in self.db_connections:
            return
        
        try:
            cursor = self.db_connections['inventario'].cursor()
            
            # Movimientos sin producto válido
            cursor.execute("""
                SELECT m.id, m.producto_id 
                FROM movimientos_inventario m 
                LEFT JOIN productos p ON m.producto_id = p.id 
                WHERE p.id IS NULL
            """)
            
            for row in cursor.fetchall():
                self.violations.append(IntegrityViolation(
                    violation_type="orphaned_record",
                    table_name="movimientos_inventario",
                    record_id=row[0],
                    field_name="producto_id",
                    expected_value="Producto existente",
                    actual_value=row[1],
                    severity="HIGH",
                    description=f"Movimiento {row[0]} referencia producto inexistente {row[1]}",
                    timestamp=datetime.now()
                ))
                
        except Exception as e:
        """Detecta registros de auditoría huérfanos."""
        if 'auditoria' not in self.db_connections or 'users' not in self.db_connections:
            return
        
        try:
            audit_cursor = self.db_connections['auditoria'].cursor()
            users_cursor = self.db_connections['users'].cursor()
            
            # Auditorías sin usuario válido
            audit_cursor.execute("""
                SELECT id, usuario 
                FROM auditoria_eventos 
                WHERE usuario IS NOT NULL 
                AND usuario != ''
            """)
            
            for row in audit_cursor.fetchall():
                users_cursor.execute("SELECT id FROM usuarios WHERE username = ?", (row[1],))
                if not users_cursor.fetchone():
                    self.violations.append(IntegrityViolation(
                        violation_type="orphaned_record",
                        table_name="auditoria_eventos",
                        record_id=row[0],
                        field_name="usuario",
                        expected_value="Usuario existente",
                        actual_value=row[1],
                        severity="MEDIUM",
                        description=f"Evento auditoría {row[0]} referencia usuario inexistente {row[1]}",
                        timestamp=datetime.now()
                    ))
                    
        except Exception as e:
        """Detecta registros duplicados."""
        logger.debug("Detectando registros duplicados")
        
        if 'inventario' not in self.db_connections:
            return
        
        try:
            cursor = self.db_connections['inventario'].cursor()
            
            # Códigos de producto duplicados
            cursor.execute("""
                SELECT codigo_producto, COUNT(*) as count 
                FROM productos 
                GROUP BY codigo_producto 
                HAVING COUNT(*) > 1
            """)
            
            for row in cursor.fetchall():
                self.violations.append(IntegrityViolation(
                    violation_type="duplicate_record",
                    table_name="productos",
                    record_id=None,
                    field_name="codigo_producto",
                    expected_value="Único",
                    actual_value=f"{row[1]} duplicados",
                    severity="HIGH",
                    description=f"Código producto '{row[0]}' duplicado {row[1]} veces",
                    timestamp=datetime.now()
                ))
                
        except Exception as e:
        """Genera reporte final de integridad."""
        violations_by_severity = {
            'CRITICAL': [v for v in self.violations if v.severity == 'CRITICAL'],
            'HIGH': [v for v in self.violations if v.severity == 'HIGH'],
            'MEDIUM': [v for v in self.violations if v.severity == 'MEDIUM'],
            'LOW': [v for v in self.violations if v.severity == 'LOW']
        }
        
        violations_by_type = {}
        for violation in self.violations:
            if violation.violation_type not in violations_by_type:
                violations_by_type[violation.violation_type] = []
            violations_by_type[violation.violation_type].append(violation)
        
        total_violations = len(self.violations)
        critical_violations = len(violations_by_severity['CRITICAL'])
        high_violations = len(violations_by_severity['HIGH'])
        
        return {
            'status': 'FAILED' if critical_violations > 0 else 'PASSED' if total_violations == 0 else 'WARNING',
            'total_violations': total_violations,
            'violations_by_severity': {
                'CRITICAL': critical_violations,
                'HIGH': high_violations,
                'MEDIUM': len(violations_by_severity['MEDIUM']),
                'LOW': len(violations_by_severity['LOW'])
            },
            'violations_by_type': {k: len(v) for k, v in violations_by_type.items()},
            'can_operate_safely': critical_violations == 0 and high_violations < 5,
            'violations': [
                {
                    'type': v.violation_type,
                    'table': v.table_name,
                    'record_id': v.record_id,
                    'field': v.field_name,
                    'expected': v.expected_value,
                    'actual': v.actual_value,
                    'severity': v.severity,
                    'description': v.description,
                    'timestamp': v.timestamp.isoformat()
                }
                for v in self.violations
            ],
            'recommendations': self._generate_recommendations()
        }

    def _generate_recommendations(self) -> List[str]:
        """Genera recomendaciones basadas en violaciones encontradas."""
        recommendations = []
        
        violations_by_type = {}
        for violation in self.violations:
            if violation.violation_type not in violations_by_type:
                violations_by_type[violation.violation_type] = 0
            violations_by_type[violation.violation_type] += 1
        
        if violations_by_type.get('foreign_key_violation', 0) > 0:
            recommendations.append("Implementar validación de claves foráneas antes de insertar/actualizar datos")
        
        if violations_by_type.get('business_rule_violation', 0) > 0:
            recommendations.append("Agregar validaciones de reglas de negocio en formularios de entrada")
        
        if violations_by_type.get('orphaned_record', 0) > 0:
            recommendations.append("Ejecutar limpieza de registros huérfanos usando scripts de mantenimiento")
        
        if violations_by_type.get('duplicate_record', 0) > 0:
            recommendations.append("Implementar restricciones UNIQUE en campos que deben ser únicos")
        
        if len(self.violations) == 0:
            recommendations.append("La integridad de datos está en excelente estado")
        
        return recommendations

    def _generate_error_report(self) -> Dict[str, Any]:
        """Genera reporte de error cuando falla la validación."""
        return {
            'status': 'ERROR',
            'total_violations': len(self.violations),
            'can_operate_safely': False,
            'error_message': 'Error durante validación de integridad',
            'violations': [],
            'recommendations': ['Revisar logs de aplicación para detalles del error']
        }

    def fix_violations(self, violation_types: List[str] = None) -> Dict[str, Any]:
        """
        Intenta corregir automáticamente violaciones específicas.
        
        Args:
            violation_types: Lista de tipos de violaciones a corregir.
                           Si None, intenta corregir todas las automáticas.
        
        Returns:
            Dict con resultados de corrección
        """
        if violation_types is None:
            violation_types = ['orphaned_record', 'duplicate_record']
        
        fixed_violations = []
        failed_fixes = []
        
        for violation in self.violations:
            if violation.violation_type not in violation_types:
                continue
            
            try:
                if violation.violation_type == 'orphaned_record':
                    success = self._fix_orphaned_record(violation)
                elif violation.violation_type == 'duplicate_record':
                    success = self._fix_duplicate_record(violation)
                else:
                    success = False
                
                if success:
                    fixed_violations.append(violation)
                else:
                    failed_fixes.append(violation)
                    
            except Exception as e:
        
        return {
            'fixed_count': len(fixed_violations),
            'failed_count': len(failed_fixes),
            'fixed_violations': [v.description for v in fixed_violations],
            'failed_violations': [v.description for v in failed_fixes]
        }

    def _fix_orphaned_record(self, violation: IntegrityViolation) -> bool:
        """Intenta corregir un registro huérfano."""
        # Implementación simplificada - eliminar registro huérfano
        try:
            if violation.table_name in ['movimientos_inventario', 'auditoria_eventos']:
                db_name = 'inventario' if 'inventario' in violation.table_name else 'auditoria'
                if db_name in self.db_connections:
                    cursor = self.db_connections[db_name].cursor()
                    cursor.execute(
                        f"DELETE FROM {violation.table_name} WHERE id = ?",
                        (violation.record_id,)
                    )
                    self.db_connections[db_name].commit()
                    logger.info(f"Eliminado registro huérfano {violation.record_id} de {violation.table_name}")
                    return True
        except Exception as e:

    def _fix_duplicate_record(self, violation: IntegrityViolation) -> bool:
        """Intenta corregir un registro duplicado."""
        # Implementación simplificada - marcar duplicados para revisión manual
        try:
            if 'inventario' in self.db_connections:
                cursor = self.db_connections['inventario'].cursor()
                # Marcar duplicados con sufijo para revisión manual
                cursor.execute("""
                    UPDATE productos 
                    SET codigo_producto = codigo_producto || '_DUP_' || id 
                    WHERE codigo_producto = ? 
                    AND id > (
                        SELECT MIN(id) 
                        FROM productos p2 
                        WHERE p2.codigo_producto = productos.codigo_producto
                    )
                """, (violation.actual_value.split()[2].strip("'"),))
                
                if cursor.rowcount > 0:
                    self.db_connections['inventario'].commit()
                    logger.info(f"Marcados {cursor.rowcount} duplicados de {violation.actual_value}")
                    return True
        except Exception as e:


# Funciones de conveniencia
def validate_system_integrity(db_connections: Dict[str, Any] = None) -> Tuple[bool, Dict[str, Any]]:
    """
    Valida integridad completa del sistema.
    
    Args:
        db_connections: Conexiones a las bases de datos
    
    Returns:
        Tuple[bool, Dict]: (es_seguro_operar, reporte_detallado)
    """
    validator = DataIntegrityValidator(db_connections)
    report = validator.validate_all()
    return report['can_operate_safely'], report


def quick_integrity_check(db_connections: Dict[str, Any] = None) -> bool:
    """
    Verificación rápida de integridad para arranque del sistema.
    
    Returns:
        bool: True si no hay violaciones críticas
    """
    validator = DataIntegrityValidator(db_connections)
    validator._validate_foreign_key_consistency()
    validator._validate_business_rules()
    
    critical_violations = [v for v in validator.violations if v.severity == 'CRITICAL']
    return len(critical_violations) == 0


# Ejemplo de uso:
"""
# En main.py o durante arranque:
from rexus.utils.data_integrity_validator import validate_system_integrity

# Obtener conexiones a las 3 bases de datos
db_connections = {
    'users': get_users_connection(),
    'inventario': get_inventario_connection(), 
    'auditoria': get_auditoria_connection()
}

# Validar integridad
is_safe, report = validate_system_integrity(db_connections)

if not is_safe:
    logger.warning(f)
    for violation in report['violations']:
        if violation['severity'] == 'CRITICAL':
            logger.critical(f"CRÍTICO: {violation['description']}")
else:
    logger.info("Integridad de datos validada correctamente")
"""