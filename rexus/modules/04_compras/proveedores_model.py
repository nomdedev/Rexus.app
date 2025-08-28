"""
Modelo de Proveedores - Compras
Gestión de datos de proveedores para el módulo de compras
"""

from typing import Dict, List, Any, Optional
from decimal import Decimal
from datetime import datetime

# Importar utilidades
try:
    from ...utils.app_logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

# Importar utilidades de seguridad
try:
    from ...utils.security_utils import SecurityUtils
    SECURITY_AVAILABLE = True
except ImportError:
    logger.warning("Security utilities not available in proveedores")
    SECURITY_AVAILABLE = False


class ProveedoresModel:
    """Modelo para gestión de proveedores."""
    
    def __init__(self, db_connection=None):
        """
        Inicializa el modelo de proveedores.
        
        Args:
            db_connection: Conexión a la base de datos
        """
        self.db_connection = db_connection
        
    def crear_proveedor(self, datos_proveedor: Dict[str, Any]) -> Optional[int]:
        """
        Crea un nuevo proveedor.
        
        Args:
            datos_proveedor: Datos del proveedor

        Returns:
            ID del proveedor creado o None si falló
        """
        try:
            if not self.db_connection:
                logger.error("No hay conexión a BD disponible")
                return None

            # Validar datos requeridos
            if not self._validar_datos_proveedor(datos_proveedor):
                return None

            cursor = self.db_connection.cursor()

            # Sanitizar datos de entrada
            datos_sanitizados = self._sanitizar_datos_proveedor(datos_proveedor)
            with open('sql/04_compras/insert_proveedor.sql', 'r', encoding='utf-8') as f:
                insert_query = f.read()
            cursor.execute(insert_query, (
                datos_sanitizados['codigo'],
                datos_sanitizados['nombre'],
                datos_sanitizados['razon_social'],
                datos_sanitizados['ruc'],
                datos_sanitizados.get('telefono', ''),
                datos_sanitizados.get('email', ''),
                datos_sanitizados.get('direccion', ''),
                datos_sanitizados.get('contacto_principal', ''),
                datos_sanitizados.get('calificacion', 5),
                1,  # activo por defecto
                datetime.now(),
                datos_sanitizados.get('observaciones', ''),
                datos_sanitizados.get('tipo_proveedor', 'GENERAL'),
                datos_sanitizados.get('condiciones_pago', '30 días'),
                datos_sanitizados.get('descuento_comercial', 0.0)
            ))
            proveedor_id = cursor.lastrowid
            self.db_connection.commit()
            logger.info(f"Proveedor creado con ID {proveedor_id}")
            return proveedor_id
            
        except Exception as e:
            logger.error(f"Error creando proveedor: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return None

    def obtener_proveedor(self, proveedor_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene los datos de un proveedor específico.

        Args:
            proveedor_id: ID del proveedor

        Returns:
            Diccionario con datos del proveedor o None si no existe
        """
        try:
            if not self.db_connection:
                return None

            cursor = self.db_connection.cursor()
            with open('sql/04_compras/select_proveedor_by_id.sql', 'r', encoding='utf-8') as f:
                select_query = f.read()
            cursor.execute(select_query, (proveedor_id,))
            result = cursor.fetchone()
            if result:
                return {
                    'id': result[0],
                    'codigo': result[1],
                    'nombre': result[2],
                    'razon_social': result[3],
                    'ruc': result[4],
                    'telefono': result[5],
                    'email': result[6],
                    'direccion': result[7],
                    'contacto_principal': result[8],
                    'calificacion': result[9],
                    'activo': result[10],
                    'fecha_registro': result[11],
                    'observaciones': result[12],
                    'tipo_proveedor': result[13],
                    'condiciones_pago': result[14],
                    'descuento_comercial': result[15]
                }
            return None
        except Exception as e:
            logger.error(f"Error obteniendo proveedor {proveedor_id}: {e}")
            return None

    def obtener_proveedores(self, activos_solo: bool = True) -> List[Dict[str, Any]]:
        """
        Obtiene lista de proveedores.
        
        Args:
            activos_solo: Si True, solo retorna proveedores activos
            
        Returns:
            Lista de diccionarios con datos de proveedores
        """
        try:
            if not self.db_connection:
                return []

            cursor = self.db_connection.cursor()
            
            if activos_solo:
                with open('sql/04_compras/select_proveedores_activos.sql', 'r', encoding='utf-8') as f:
                    select_query = f.read()
            else:
                with open('sql/04_compras/select_proveedores_all.sql', 'r', encoding='utf-8') as f:
                    select_query = f.read()
                    
            cursor.execute(select_query)
            
            proveedores = []
            for row in cursor.fetchall():
                proveedor = {
                    'id': row[0],
                    'codigo': row[1],
                    'nombre': row[2],
                    'razon_social': row[3],
                    'ruc': row[4],
                    'telefono': row[5],
                    'email': row[6],
                    'direccion': row[7],
                    'contacto_principal': row[8],
                    'calificacion': row[9],
                    'activo': row[10],
                    'fecha_registro': row[11],
                    'observaciones': row[12],
                    'tipo_proveedor': row[13],
                    'condiciones_pago': row[14],
                    'descuento_comercial': row[15]
                }
                proveedores.append(proveedor)
            
            return proveedores
            
        except Exception as e:
            logger.error(f"Error obteniendo proveedores: {e}")
            return []

    def _validar_datos_proveedor(self, datos: Dict[str, Any]) -> bool:
        """Valida los datos del proveedor antes de crear/actualizar."""
        required_fields = ['codigo', 'nombre', 'razon_social', 'ruc']
        for field in required_fields:
            if not datos.get(field):
                logger.error(f"Campo requerido faltante: {field}")
                return False
        return True
        
    def _sanitizar_datos_proveedor(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitiza los datos del proveedor."""
        if SECURITY_AVAILABLE:
            return SecurityUtils.sanitize_dict(datos)
        return datos
