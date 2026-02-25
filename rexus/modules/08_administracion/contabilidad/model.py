"""
Modelo de Contabilidad - Rexus.app v2.0.0

Maneja la lógica de negocio y acceso a datos para contabilidad.
Gestiona asientos contables, recibos y pagos.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, date

# Configuración de logging
logger = logging.getLogger(__name__)

class ContabilidadModel:
    """Modelo principal para gestión de contabilidad"""
    
    def __init__(self, db_connection=None):
        """
        Inicializa el modelo de contabilidad.
        
        Args:
            db_connection: Conexión a la base de datos
        """
        self.db_connection = db_connection
        self.tabla_libro_contable = self._validate_table_name("libro_contable")
        self.tabla_recibos = self._validate_table_name("recibos")
        self.tabla_pagos_obra = self._validate_table_name("pagos_obra")
        self.tabla_pagos_materiales = self._validate_table_name("pagos_materiales")
        
        if self.db_connection:
            self._verificar_tablas()
    
    def _verificar_tablas(self):
        """Verifica que las tablas necesarias existan"""
        try:
            cursor = self.db_connection.cursor()
            
            # Verificar tabla principal
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_name = ?
                """,
                (self.tabla_libro_contable,),
            )
            
            if cursor.fetchone()[0] > 0:
                logger.info(f"OK [CONTABILIDAD] Tabla '{self.tabla_libro_contable}' verificada correctamente.")
            else:
                logger.warning(f"ADVERTENCIA: La tabla '{self.tabla_libro_contable}' no existe en la base de datos.")
                
        except Exception as e:
            logger.error(f"ERROR [CONTABILIDAD] Verificando tablas: {e}")
    
    def _validate_table_name(self, table_name: str) -> str:
        """
        Valida y sanitiza un nombre de tabla.
        
        Args:
            table_name: Nombre de la tabla a validar
            
        Returns:
            Nombre de tabla validado
        """
        if not table_name:
            raise ValueError("El nombre de la tabla no puede estar vacío")
        
        # Solo permitir caracteres alfanuméricos y guiones bajos
        import re
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table_name):
            raise ValueError(f"Nombre de tabla inválido: {table_name}")
        
        return table_name
    
    def crear_asiento_contable(self, datos_asiento: Dict[str, Any]) -> Tuple[bool, str, Optional[int]]:
        """
        Crea un nuevo asiento contable.
        
        Args:
            datos_asiento: Diccionario con datos del asiento
            
        Returns:
            Tuple con (éxito, mensaje, id_asiento)
        """
        if not self.db_connection:
            return False, "No hay conexión a la base de datos", None
        
        try:
            # Validar datos requeridos
            if not datos_asiento.get("fecha_asiento"):
                return False, "La fecha del asiento es requerida", None
            
            if not datos_asiento.get("tipo_asiento"):
                return False, "El tipo de asiento es requerido", None
            
            # Insertar asiento
            cursor = self.db_connection.cursor()
            
            query = f"""
                INSERT INTO {self.tabla_libro_contable} 
                (fecha_asiento, tipo_asiento, concepto, referencia, debe, haber, saldo, estado, fecha_creacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
            """
            
            valores = (
                datos_asiento.get("fecha_asiento"),
                datos_asiento.get("tipo_asiento"),
                datos_asiento.get("concepto", ""),
                datos_asiento.get("referencia", ""),
                datos_asiento.get("debe", 0),
                datos_asiento.get("haber", 0),
                datos_asiento.get("saldo", 0),
                datos_asiento.get("estado", "ACTIVO")
            )
            
            cursor.execute(query, valores)
            self.db_connection.commit()
            
            # Obtener ID del asiento insertado
            cursor.execute("SELECT @@IDENTITY")
            asiento_id = cursor.fetchone()[0]
            
            logger.info(f"OK [CONTABILIDAD] Asiento contable creado (ID: {asiento_id})")
            
            return True, f"Asiento contable creado correctamente", asiento_id
            
        except Exception as e:
            logger.error(f"ERROR [CONTABILIDAD] Creando asiento contable: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False, f"Error en la base de datos: {str(e)}", None
    
    def obtener_asientos_por_fecha(self, fecha_desde: date = None, fecha_hasta: date = None) -> List[Dict[str, Any]]:
        """
        Obtiene asientos contables por rango de fechas.
        
        Args:
            fecha_desde: Fecha desde
            fecha_hasta: Fecha hasta
            
        Returns:
            Lista de diccionarios con datos de asientos
        """
        if not self.db_connection:
            return []
        
        try:
            cursor = self.db_connection.cursor()
            
            query = f"SELECT * FROM {self.tabla_libro_contable} WHERE 1=1"
            params = []
            
            if fecha_desde:
                query += " AND fecha_asiento >= ?"
                params.append(fecha_desde)
            
            if fecha_hasta:
                query += " AND fecha_asiento <= ?"
                params.append(fecha_hasta)
            
            query += " ORDER BY fecha_asiento DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            if rows:
                columnas = [desc[0] for desc in cursor.description]
                return [dict(zip(columnas, row)) for row in rows]
            
            return []
            
        except Exception as e:
            logger.error(f"ERROR [CONTABILIDAD] Obteniendo asientos por fecha: {e}")
            return []
    
    def obtener_recibos(self, fecha_desde: date = None, fecha_hasta: date = None) -> List[Dict[str, Any]]:
        """
        Obtiene recibos con filtros opcionales.
        
        Args:
            fecha_desde: Fecha desde
            fecha_hasta: Fecha hasta
            
        Returns:
            Lista de diccionarios con datos de recibos
        """
        if not self.db_connection:
            return []
        
        try:
            cursor = self.db_connection.cursor()
            
            query = f"SELECT * FROM {self.tabla_recibos} WHERE 1=1"
            params = []
            
            if fecha_desde:
                query += " AND fecha_emision >= ?"
                params.append(fecha_desde)
            
            if fecha_hasta:
                query += " AND fecha_emision <= ?"
                params.append(fecha_hasta)
            
            query += " ORDER BY fecha_emision DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            if rows:
                columnas = [desc[0] for desc in cursor.description]
                return [dict(zip(columnas, row)) for row in rows]
            
            return []
            
        except Exception as e:
            logger.error(f"ERROR [CONTABILIDAD] Error obteniendo recibos: {e}")
            return []
    
    def crear_recibo(self, datos_recibo: Dict[str, Any]) -> Tuple[bool, str, Optional[int]]:
        """
        Crea un nuevo recibo.
        
        Args:
            datos_recibo: Diccionario con datos del recibo
            
        Returns:
            Tuple con (éxito, mensaje, id_recibo)
        """
        if not self.db_connection:
            return False, "No hay conexión a la base de datos", None
        
        try:
            cursor = self.db_connection.cursor()
            
            query = f"""
                INSERT INTO {self.tabla_recibos}
                (numero_recibo, fecha_emision, monto, concepto, id_obra, estado, fecha_creacion)
                VALUES (?, ?, ?, ?, ?, ?, GETDATE())
            """
            
            valores = (
                datos_recibo.get("numero_recibo"),
                datos_recibo.get("fecha_emision"),
                datos_recibo.get("monto"),
                datos_recibo.get("concepto", ""),
                datos_recibo.get("id_obra"),
                datos_recibo.get("estado", "PENDIENTE")
            )
            
            cursor.execute(query, valores)
            self.db_connection.commit()
            
            # Obtener ID del recibo insertado
            cursor.execute("SELECT @@IDENTITY")
            recibo_id = cursor.fetchone()[0]
            
            logger.info(f"OK [CONTABILIDAD] Recibo creado con ID: {recibo_id}")
            
            return True, f"Recibo creado correctamente", recibo_id
            
        except Exception as e:
            logger.error(f"ERROR [CONTABILIDAD] Creando recibo: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False, f"Error en la base de datos: {str(e)}", None
    
    def obtener_estadisticas_contables(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas generales de contabilidad.
        
        Returns:
            Diccionario con estadísticas
        """
        if not self.db_connection:
            return {}
        
        try:
            cursor = self.db_connection.cursor()
            
            stats = {}
            
            # Total de asientos
            cursor.execute(f"SELECT COUNT(*) FROM {self.tabla_libro_contable}")
            stats["total_asientos"] = cursor.fetchone()[0]
            
            # Total de recibos
            cursor.execute(f"SELECT COUNT(*) FROM {self.tabla_recibos}")
            stats["total_recibos"] = cursor.fetchone()[0]
            
            # Balance general
            cursor.execute(f"""
                SELECT 
                    SUM(CASE WHEN debe > 0 THEN debe ELSE 0 END) as total_debe,
                    SUM(CASE WHEN haber > 0 THEN haber ELSE 0 END) as total_haber
                FROM {self.tabla_libro_contable}
                WHERE estado = 'ACTIVO'
            """)
            
            balance = cursor.fetchone()
            if balance:
                stats["total_debe"] = balance[0] or 0
                stats["total_haber"] = balance[1] or 0
                stats["balance_neto"] = stats["total_debe"] - stats["total_haber"]
            
            return stats
            
        except Exception as e:
            logger.error(f"ERROR [CONTABILIDAD] Error obteniendo estadísticas: {e}")
            return {}


# Clase de compatibilidad para mantener la interfaz anterior
class ModeloContabilidad(ContabilidadModel):
    """Clase de compatibilidad para el modelo de contabilidad"""
    pass
