"""
Modelo de Herrajes - Rexus.app v2.0.0

Maneja la lógica de negocio y acceso a datos para herrajes.
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

# SQLQueryManager unificado
try:
    from rexus.core.sql_query_manager import SQLQueryManager
except ImportError:
    from rexus.utils.sql_script_loader import sql_script_loader
    
    class SQLQueryManager:
        def __init__(self):
            self.sql_loader = sql_script_loader

        def get_query(self, path, filename):
            script_name = filename
            return self.sql_loader.load_script(script_name)

class HerrajesModel:
    """Modelo para el módulo de herrajes."""

    def __init__(self, db_connection=None):
        """Inicializa el modelo de herrajes."""
        self.db_connection = db_connection
        self.sql_manager = SQLQueryManager()
        self.sql_path = 'herrajes'
        self.logger = logger

    def obtener_herraje_por_codigo(self, codigo: str) -> Optional[Dict[str, Any]]:
        """Obtiene un herraje por su código."""
        try:
            if not self.db_connection:
                return None

            cursor = self.db_connection.cursor()
            query = self.sql_manager.get_query(self.sql_path, 'select_herraje_by_codigo')
            cursor.execute(query, {'codigo': codigo})

            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'codigo': row[1],
                    'nombre': row[2],
                    'tipo': row[3],
                    'descripcion': row[4],
                    'precio_unitario': row[5],
                    'stock_actual': row[6],
                    'stock_minimo': row[7]
                }
            return None

        except Exception as e:
            self.logger.error(f"Error obteniendo herraje por código: {e}")
            return None

    def eliminar_herraje(self, codigo: str) -> bool:
        """Elimina un herraje por su código."""
        try:
            if not self.db_connection:
                return False

            cursor = self.db_connection.cursor()

            # Verificar si el herraje existe
            query_check = self.sql_manager.get_query(self.sql_path, 'select_herraje_id_by_codigo')
            cursor.execute(query_check, {'codigo': codigo})
            if not cursor.fetchone():
                self.logger.warning(f"Herraje con código {codigo} no encontrado")
                return False

            # Eliminar relaciones primero
            query_delete_rel = self.sql_manager.get_query(self.sql_path, 'delete_herrajes_obra_by_codigo')
            cursor.execute(query_delete_rel, {'codigo': codigo})

            # Eliminar el herraje
            query_delete = self.sql_manager.get_query(self.sql_path, 'delete_herraje_by_codigo')
            cursor.execute(query_delete, {'codigo': codigo})
            rows_affected = cursor.rowcount

            if rows_affected > 0:
                self.db_connection.commit()
                self.logger.info(f"Herraje {codigo} eliminado exitosamente")
                return True
            else:
                self.logger.warning(f"No se pudo eliminar el herraje {codigo}")
                return False

        except Exception as e:
            self.logger.error(f"Error eliminando herraje: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False

    def obtener_todos_herrajes(self) -> List[Dict[str, Any]]:
        """Obtiene todos los herrajes."""
        try:
            if not self.db_connection:
                return []

            cursor = self.db_connection.cursor()
            query = self.sql_manager.get_query(self.sql_path, 'select_all_herrajes')
            cursor.execute(query)

            herrajes = []
            for row in cursor.fetchall():
                herrajes.append({
                    'id': row[0],
                    'codigo': row[1],
                    'nombre': row[2],
                    'tipo': row[3],
                    'descripcion': row[4],
                    'precio_unitario': row[5],
                    'stock_actual': row[6],
                    'stock_minimo': row[7]
                })

            return herrajes

        except Exception as e:
            self.logger.error(f"Error obteniendo herrajes: {e}")
            return []

    def crear_herraje(self, datos: Dict[str, Any]) -> Optional[int]:
        """Crea un nuevo herraje."""
        try:
            if not self.db_connection:
                return None

            cursor = self.db_connection.cursor()
            query = self.sql_manager.get_query(self.sql_path, 'insert_herraje_simple')
            cursor.execute(query, {
                'codigo': datos.get('codigo'),
                'nombre': datos.get('nombre'),
                'tipo': datos.get('tipo'),
                'descripcion': datos.get('descripcion', ''),
                'precio_unitario': datos.get('precio_unitario', 0.0),
                'stock_actual': datos.get('stock_actual', 0),
                'stock_minimo': datos.get('stock_minimo', 0)
            })

            herraje_id = cursor.lastrowid
            self.db_connection.commit()
            self.logger.info(f"Herraje creado exitosamente: {herraje_id}")
            return herraje_id

        except Exception as e:
            self.logger.error(f"Error creando herraje: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return None

    def actualizar_stock(self, codigo: str, nuevo_stock: int) -> bool:
        """Actualiza el stock de un herraje."""
        try:
            if not self.db_connection:
                return False

            cursor = self.db_connection.cursor()
            query = self.sql_manager.get_query(self.sql_path, 'update_stock_herraje')
            cursor.execute(query, {
                'nuevo_stock': nuevo_stock,
                'codigo': codigo
            })

            if cursor.rowcount > 0:
                self.db_connection.commit()
                self.logger.info(f"Stock actualizado para herraje {codigo}: {nuevo_stock}")
                return True
            else:
                self.logger.warning(f"No se encontró herraje con código {codigo}")
                return False

        except Exception as e:
            self.logger.error(f"Error actualizando stock: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False