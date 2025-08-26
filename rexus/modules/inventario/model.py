"""
Modelo de Inventario - Rexus.app
Gestión del inventario de productos
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# SQLQueryManager unificado
try:
    from rexus.core.sql_query_manager import SQLQueryManager
except ImportError:
    try:
        from rexus.utils.sql_query_manager import SQLQueryManager
    except ImportError:
        from rexus.utils.sql_script_loader import sql_script_loader
        
        class SQLQueryManager:
            def __init__(self):
                self.sql_loader = sql_script_loader

            def get_query(self, path, filename):
                script_name = filename
                return self.sql_loader.load_script(script_name)

class InventarioModel:
    """Modelo para gestión de inventario."""
    
    def __init__(self, db_connection=None):
        """Inicializa el modelo de inventario."""
        self.db_connection = db_connection
        self.sql_manager = SQLQueryManager()
        self.sql_path = 'inventario'
        
    def obtener_productos(self, filtros: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Obtiene productos con filtros opcionales."""
        try:
            if not self.db_connection:
                logger.warning("No hay conexión a base de datos disponible")
                return self._get_productos_demo()
                
            cursor = self.db_connection.cursor()
            
            # Usar query externa
            query = self.sql_manager.get_query(self.sql_path, 'select_all_productos')
            if not query:
                logger.error("No se pudo cargar query de productos")
                return self._get_productos_demo()
                
            cursor.execute(query)
            
            productos = []
            for row in cursor.fetchall():
                producto = {
                    'id': row[0],
                    'codigo': row[1],
                    'descripcion': row[2],
                    'tipo': row[3],
                    'acabado': row[4],
                    'stock_actual': row[5],
                    'stock_minimo': row[6],
                    'stock_maximo': row[7],
                    'importe': row[8],
                    'ubicacion': row[9],
                    'proveedor': row[10],
                    'unidad': row[11],
                    'fecha_creacion': row[12],
                    'usuario_creacion': row[13],
                    'observaciones': row[14],
                    'estado': row[15] if len(row) > 15 else 'ACTIVO'
                }
                productos.append(producto)
                
            return productos
                
        except Exception as e:
            logger.error(f"Error obteniendo productos: {e}")
            return self._get_productos_demo()
    
    def obtener_producto_por_id(self, producto_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un producto por su ID."""
        try:
            if not self.db_connection:
                return None
                
            cursor = self.db_connection.cursor()
            query = self.sql_manager.get_query(self.sql_path, 'select_by_id')
            
            if not query:
                logger.error("No se pudo cargar query select_by_id")
                return None
                
            cursor.execute(query, {'producto_id': producto_id})
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row[0],
                    'codigo': row[1],
                    'descripcion': row[2],
                    'tipo': row[3],
                    'acabado': row[4],
                    'stock_actual': row[5],
                    'stock_minimo': row[6],
                    'stock_maximo': row[7],
                    'importe': row[8],
                    'ubicacion': row[9],
                    'proveedor': row[10],
                    'unidad': row[11],
                    'fecha_creacion': row[12],
                    'usuario_creacion': row[13],
                    'observaciones': row[14],
                    'estado': row[15] if len(row) > 15 else 'ACTIVO'
                }
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo producto por ID: {e}")
            return None
    
    def crear_producto(self, datos_producto: Dict[str, Any], usuario: str = "SISTEMA") -> bool:
        """Crea un nuevo producto."""
        try:
            if not self.db_connection:
                logger.error("No hay conexión a BD disponible")
                return False
            
            cursor = self.db_connection.cursor()
            query = self.sql_manager.get_query(self.sql_path, 'insert_producto')
            
            if not query:
                logger.error("No se pudo cargar query insert_producto")
                return False
            
            cursor.execute(query, {
                'codigo': datos_producto.get('codigo'),
                'descripcion': datos_producto.get('descripcion'),
                'tipo': datos_producto.get('tipo', ''),
                'acabado': datos_producto.get('acabado', ''),
                'stock_actual': datos_producto.get('stock_actual', 0),
                'stock_minimo': datos_producto.get('stock_minimo', 0),
                'stock_maximo': datos_producto.get('stock_maximo', 1000),
                'importe': datos_producto.get('importe', 0.00),
                'ubicacion': datos_producto.get('ubicacion', ''),
                'proveedor': datos_producto.get('proveedor', ''),
                'unidad': datos_producto.get('unidad', 'Unidad'),
                'usuario_creacion': usuario,
                'observaciones': datos_producto.get('observaciones', '')
            })
            
            self.db_connection.commit()
            logger.info(f"Producto '{datos_producto.get('codigo')}' creado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error creando producto: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False
    
    def actualizar_producto(self, producto_id: int, datos_producto: Dict[str, Any]) -> bool:
        """Actualiza un producto existente."""
        try:
            if not self.db_connection:
                logger.error("No hay conexión a BD disponible")
                return False
            
            cursor = self.db_connection.cursor()
            query = self.sql_manager.get_query(self.sql_path, 'update_producto')
            
            if not query:
                logger.error("No se pudo cargar query update_producto")
                return False
            
            cursor.execute(query, {
                'descripcion': datos_producto.get('descripcion'),
                'tipo': datos_producto.get('tipo', ''),
                'acabado': datos_producto.get('acabado', ''),
                'stock_actual': datos_producto.get('stock_actual', 0),
                'stock_minimo': datos_producto.get('stock_minimo', 0),
                'stock_maximo': datos_producto.get('stock_maximo', 1000),
                'importe': datos_producto.get('importe', 0.00),
                'ubicacion': datos_producto.get('ubicacion', ''),
                'proveedor': datos_producto.get('proveedor', ''),
                'unidad': datos_producto.get('unidad', 'Unidad'),
                'observaciones': datos_producto.get('observaciones', ''),
                'producto_id': producto_id
            })
            
            self.db_connection.commit()
            logger.info(f"Producto ID {producto_id} actualizado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error actualizando producto: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False
        
    def obtener_lotes(self, producto_id: Optional[int] = None, activos_solo: bool = True) -> List[Dict[str, Any]]:
        """Obtiene lotes de inventario."""
        try:
            if not self.db_connection:
                logger.warning("No hay conexión a base de datos disponible")
                return []
                
            cursor = self.db_connection.cursor()
            
            if producto_id:
                # Usar método existente para producto específico
                return self.obtener_lotes_producto(producto_id)
            else:
                # Obtener todos los lotes usando query externa
                query = self.sql_manager.get_query(self.sql_path, 'select_lotes_inventario')
                if not query:
                    logger.error("No se pudo cargar query de lotes")
                    return []
                    
                cursor.execute(query, {'activos_solo': 1 if activos_solo else 0})
                
                # Procesar resultados
                lotes = []
                for row in cursor.fetchall():
                    lote = {
                        'id': row[0],
                        'producto_id': row[1], 
                        'numero_lote': row[2],
                        'cantidad': row[3],
                        'fecha_vencimiento': row[4],
                        'ubicacion': row[5],
                        'estado': row[6],
                        'fecha_ingreso': row[7],
                        'producto_nombre': row[8] if len(row) > 8 else None,
                        'producto_codigo': row[9] if len(row) > 9 else None
                    }
                    lotes.append(lote)
                    
                return lotes
                
        except Exception as e:
            logger.error(f"Error obteniendo lotes: {e}")
            return []
    
    def obtener_lotes_producto(self, producto_id: int) -> List[Dict[str, Any]]:
        """Obtiene lotes de un producto específico."""
        try:
            if not self.db_connection:
                return []
                
            cursor = self.db_connection.cursor()
            query = self.sql_manager.get_query(self.sql_path, 'obtener_lotes')
            
            if not query:
                logger.error("No se pudo cargar query obtener_lotes")
                return []
                
            cursor.execute(query, {'producto_id': producto_id})
            
            lotes = []
            for row in cursor.fetchall():
                lote = {
                    'id': row[0],
                    'producto_id': row[1], 
                    'numero_lote': row[2],
                    'cantidad': row[3],
                    'fecha_vencimiento': row[4],
                    'ubicacion': row[5],
                    'estado': row[6],
                    'fecha_ingreso': row[7]
                }
                lotes.append(lote)
                
            return lotes
            
        except Exception as e:
            logger.error(f"Error obteniendo lotes del producto {producto_id}: {e}")
            return []

    def _get_productos_demo(self):
        """Datos demo para productos cuando no hay conexión"""
        return [
            {
                'id': 1,
                'codigo': 'PROD001',
                'nombre': 'Producto Demo 1',
                'categoria': 'DEMO',
                'cantidad_disponible': 10,
                'precio_unitario': 100.0
            },
            {
                'id': 2,
                'codigo': 'PROD002', 
                'nombre': 'Producto Demo 2',
                'categoria': 'DEMO',
                'cantidad_disponible': 5,
                'precio_unitario': 200.0
            }
        ]
