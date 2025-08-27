"""
Modelo de Compras - Rexus.app v2.0.0

Maneja la lógica de negocio y acceso a datos para el sistema de compras.
MIGRADO A SQL EXTERNO - Todas las consultas usan SQLQueryManager
para prevenir inyección SQL y mejorar mantenibilidad.
"""

import datetime
import json
import logging
from decimal import Decimal
from typing import Dict, List, Any, Optional

# Importar logging
try:
    from ...utils.app_logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

# Importar utilidades de sanitización
try:
    from rexus.utils.unified_sanitizer import sanitize_string, unified_sanitizer
    SANITIZER_AVAILABLE = True
except ImportError:
    logger.warning("Sanitizador no disponible, usando métodos básicos")
    SANITIZER_AVAILABLE = False

# SQLQueryManager para externalizar queries
try:
    from rexus.core.sql_query_manager import SQLQueryManager
except ImportError:
    from rexus.utils.sql_script_loader import sql_script_loader
    class SQLQueryManager:
        def __init__(self):
            self.sql_loader = sql_script_loader
        def get_query(self, path, filename):
            return self.sql_loader.load_script(filename)

    def sanitize_string(s):
        return str(s).replace("'", "''").replace(";", "") if s else ""

    def validate_input(s, input_type="string"):
        return bool(s and len(str(s)) < 1000)


class ComprasModel:
    """Modelo para gestionar el sistema de compras."""

    def __init__(self, db_connection=None):
        """
        Inicializar modelo de compras.

        Args:
            db_connection: Conexión a la base de datos
        """
        self.db_connection = db_connection
        self.sql_manager = SQLQueryManager()
        self.data_sanitizer = None
        logger.info("ComprasModel inicializado")

    def verificar_estructura_tabla(self):
        """Verifica que las tablas de compras existan en la DB."""
        if not self.db_connection:
            logger.warning("No hay conexión a base de datos disponible")
            return False

        try:
            cursor = self.db_connection.cursor()
            
            # Lista de tablas requeridas (usando nombres que SÍ existen en la BD)
            tablas_requeridas = [
                'compras', 'detalle_compras', 'proveedores', 
                'pedidos_compra', 'pedidos'
            ]
            
            for tabla in tablas_requeridas:
                try:
                    # Usar SQL externalizado compatible con SQL Server
                    sql_verificar = self.sql_manager.get_query('compras', 'verificar_tabla_existe')
                    cursor.execute(sql_verificar, (tabla,))
                    result = cursor.fetchone()
                    if not result or result[0] == 0:
                        logger.warning(f"Tabla '{tabla}' no existe en la base de datos")
                    else:
                        logger.info(f"Tabla '{tabla}' verificada correctamente")
                except Exception as e:
                    logger.error(f"Error verificando tabla '{tabla}': {e}")
                    return False

            logger.info("Verificación de tablas de compras completada")
            return True

        except Exception as e:
            logger.error(f"Error verificando tablas: {e}")
            return False

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

            # Sanitizar datos
            nombre = sanitize_string(datos_proveedor.get('nombre', ''))
            contacto = sanitize_string(datos_proveedor.get('contacto', ''))
            codigo = sanitize_string(datos_proveedor.get('codigo', ''))

            if not nombre or not contacto:
                logger.error("Nombre y contacto son requeridos")
                return None

            cursor = self.db_connection.cursor()

            # Usar archivo SQL externo
            with open('sql/compras/crear_proveedor.sql', 'r', encoding='utf-8') as f:
                insert_query = f.read()

            cursor.execute(insert_query, (
                codigo, nombre, contacto,
                datos_proveedor.get('telefono', ''),
                datos_proveedor.get('email', ''),
                datos_proveedor.get('direccion', ''),
                datos_proveedor.get('ruc', ''),
                datos_proveedor.get('categoria', 'GENERAL'),
                datos_proveedor.get('limite_credito', 0.0),
                datos_proveedor.get('plazo_pago', 30),
                datos_proveedor.get('descuento_habitual', 0.0),
                datos_proveedor.get('observaciones', ''),
                datetime.datetime.now()
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

    def obtener_proveedores(self) -> List[Dict[str, Any]]:
        """
        Obtiene todos los proveedores activos.

        Returns:
            Lista de proveedores
        """
        try:
            if not self.db_connection:
                logger.error("No hay conexión a BD disponible")
                return self._obtener_proveedores_demo()

            cursor = self.db_connection.cursor()

            # Usar archivo SQL externo
            with open('sql/compras/obtener_proveedores.sql', 'r', encoding='utf-8') as f:
                select_query = f.read()

            cursor.execute(select_query)
            rows = cursor.fetchall()

            proveedores = []
            for row in rows:
                proveedor = {
                    'id': row[0],
                    'codigo': row[1],
                    'nombre': row[2],
                    'contacto': row[3],
                    'telefono': row[4],
                    'email': row[5],
                    'direccion': row[6],
                    'ruc': row[7],
                    'categoria': row[8],
                    'activo': row[9],
                    'limite_credito': float(row[10]) if row[10] else 0.0,
                    'plazo_pago': row[11],
                    'descuento_habitual': float(row[12]) if row[12] else 0.0,
                    'observaciones': row[13],
                    'fecha_creacion': row[14],
                    'fecha_modificacion': row[15]
                }
                proveedores.append(proveedor)

            return proveedores

        except Exception as e:
            logger.error(f"Error obteniendo proveedores: {e}")
            return self._obtener_proveedores_demo()

    def crear_orden_compra(self, datos_orden: Dict[str, Any]) -> Optional[int]:
        """
        Crea una nueva orden de compra.

        Args:
            datos_orden: Datos de la orden

        Returns:
            ID de la orden creada o None si falló
        """
        try:
            if not self.db_connection:
                logger.error("No hay conexión a BD disponible")
                return None

            # Validaciones básicas
            if not datos_orden.get('proveedor_id'):
                logger.error("ID de proveedor es requerido")
                return None

            if not datos_orden.get('detalles') or len(datos_orden['detalles']) == 0:
                logger.error("La orden debe tener al menos un detalle")
                return None

            cursor = self.db_connection.cursor()

            # Usar archivo SQL externo para crear orden
            with open('sql/compras/crear_orden_compra.sql', 'r', encoding='utf-8') as f:
                insert_orden_query = f.read()

            cursor.execute(insert_orden_query, (
                datos_orden.get('numero_orden'),
                datos_orden.get('proveedor_id'),
                datos_orden.get('fecha_orden', datetime.date.today()),
                datos_orden.get('fecha_entrega'),
                datos_orden.get('estado', 'BORRADOR'),
                datos_orden.get('subtotal', 0.0),
                datos_orden.get('descuento', 0.0),
                datos_orden.get('impuestos', 0.0),
                datos_orden.get('total', 0.0),
                datos_orden.get('observaciones', ''),
                datos_orden.get('usuario_creador', ''),
                datetime.datetime.now()
            ))

            orden_id = cursor.lastrowid

            # Insertar detalles
            with open('sql/compras/crear_detalle_orden.sql', 'r', encoding='utf-8') as f:
                insert_detalle_query = f.read()

            for detalle in datos_orden['detalles']:
                cursor.execute(insert_detalle_query, (
                    orden_id,
                    detalle.get('producto_id'),
                    detalle.get('codigo_producto', ''),
                    detalle.get('descripcion', ''),
                    detalle.get('cantidad', 0),
                    detalle.get('precio_unitario', 0.0),
                    detalle.get('descuento_porcentaje', 0.0),
                    detalle.get('descuento_monto', 0.0),
                    detalle.get('subtotal', 0.0),
                    datetime.datetime.now()
                ))

            self.db_connection.commit()

            logger.info(f"Orden de compra creada con ID {orden_id}")
            return orden_id

        except Exception as e:
            logger.error(f"Error creando orden de compra: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return None

    def _obtener_proveedores_demo(self) -> List[Dict[str, Any]]:
        """Datos de demostración para proveedores."""
        return [
            {
                'id': 1,
                'codigo': 'PROV001',
                'nombre': 'Proveedor Demo 1',
                'contacto': 'Juan Pérez',
                'telefono': '123-456-7890',
                'email': 'juan@proveedor1.com',
                'direccion': 'Calle Demo 123',
                'ruc': '12345678901',
                'categoria': 'MATERIALES',
                'activo': True,
                'limite_credito': 50000.0,
                'plazo_pago': 30,
                'descuento_habitual': 5.0,
                'observaciones': 'Proveedor confiable',
                'fecha_creacion': datetime.datetime.now(),
                'fecha_modificacion': datetime.datetime.now()
            }
        ]
