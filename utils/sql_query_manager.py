"""
SQL Query Manager - Sistema centralizado de consultas SQL

Proporciona un sistema seguro y centralizado para gestionar consultas SQL
evitando inyección SQL y mejorando la mantenibilidad.
"""

import os
import json
import logging
from typing import Dict, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class SQLQueryManager:
    """Gestor centralizado de consultas SQL para prevenir inyección SQL."""
    
    def __init__(self):
        """Inicializa el gestor con configuración por defecto."""
        self.queries_cache = {}
        self.base_path = Path(__file__).parent.parent / "sql"
        
    def get_query(self, module: str, query_name: str) -> Optional[str]:
        """
        Obtiene una consulta SQL específica.
        
        Args:
            module: Nombre del módulo (ej: 'pedidos', 'inventario')
            query_name: Nombre de la consulta específica
            
        Returns:
            La consulta SQL o None si no se encuentra
        """
        cache_key = f"{module}.{query_name}"
        
        # Intentar desde cache
        if cache_key in self.queries_cache:
            return self.queries_cache[cache_key]
            
        # Intentar cargar desde archivo
        query = self._load_query_from_file(module, query_name)
        if query:
            self.queries_cache[cache_key] = query
            return query
            
        # Fallback a consultas básicas
        return self._get_fallback_query(module, query_name)
    
    def _load_query_from_file(self, module: str, query_name: str) -> Optional[str]:
        """Carga una consulta desde archivo JSON."""
        try:
            query_file = self.base_path / f"{module}.json"
            if not query_file.exists():
                return None
                
            with open(query_file, 'r', encoding='utf-8') as f:
                queries = json.load(f)
                return queries.get(query_name)
                
        except Exception as e:
            logger.warning(f"Error cargando consulta {module}.{query_name}: {e}")
            return None
    
    def _get_fallback_query(self, module: str, query_name: str) -> Optional[str]:
        """Proporciona consultas básicas como fallback."""
        fallback_queries = {
            'pedidos': {
                'obtener_pedidos_base': """
                    SELECT id, numero_pedido, fecha_pedido, cliente_id, estado, 
                           total, observaciones, fecha_creacion
                    FROM pedidos 
                    WHERE activo = 1
                    ORDER BY fecha_creacion DESC
                """,
                'insertar_pedido_principal': """
                    INSERT INTO pedidos (numero_pedido, fecha_pedido, cliente_id, 
                                        estado, total, observaciones, fecha_creacion, usuario_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                'actualizar_totales_pedido': """
                    UPDATE pedidos 
                    SET total = ?, subtotal = ?, impuestos = ?
                    WHERE id = ?
                """,
                'insertar_detalle_pedido': """
                    INSERT INTO detalle_pedidos (pedido_id, producto_id, cantidad, 
                                               precio_unitario, subtotal)
                    VALUES (?, ?, ?, ?, ?)
                """,
                'validar_pedido_duplicado_creacion': """
                    SELECT COUNT(*) as count 
                    FROM pedidos 
                    WHERE numero_pedido = ? AND activo = 1
                """,
                'validar_pedido_duplicado_edicion': """
                    SELECT COUNT(*) as count 
                    FROM pedidos 
                    WHERE numero_pedido = ? AND id != ? AND activo = 1
                """,
                'get_base_query_pedidos': """
                    SELECT p.*, c.nombre as cliente_nombre
                    FROM pedidos p
                    LEFT JOIN clientes c ON p.cliente_id = c.id
                    WHERE p.activo = 1
                """,
                'get_count_query_pedidos': """
                    SELECT COUNT(*) as total
                    FROM pedidos p
                    WHERE p.activo = 1
                """
            },
            'inventario': {
                'obtener_productos_base': """
                    SELECT id, codigo, nombre, descripcion, precio, stock, categoria_id
                    FROM productos 
                    WHERE activo = 1
                    ORDER BY nombre
                """,
                'actualizar_stock': """
                    UPDATE productos 
                    SET stock = stock + ?
                    WHERE id = ?
                """,
                'insertar_producto': """
                    INSERT INTO productos (codigo, nombre, descripcion, precio, stock, categoria_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                """
            },
            'compras': {
                'obtener_compras_base': """
                    SELECT id, numero_compra, fecha_compra, proveedor_id, estado, total
                    FROM compras 
                    WHERE activo = 1
                    ORDER BY fecha_compra DESC
                """,
                'insertar_compra': """
                    INSERT INTO compras (numero_compra, fecha_compra, proveedor_id, estado, total)
                    VALUES (?, ?, ?, ?, ?)
                """
            }
        }
        
        module_queries = fallback_queries.get(module, {})
        return module_queries.get(query_name)
    
    def execute_query(self, connection, query: str, params: tuple = None):
        """
        Ejecuta una consulta de manera segura.
        
        Args:
            connection: Conexión a la base de datos
            query: Consulta SQL a ejecutar
            params: Parámetros para la consulta
            
        Returns:
            Resultado de la consulta
        """
        try:
            if params:
                return connection.execute(query, params)
            else:
                return connection.execute(query)
        except Exception as e:
            logger.error(f"Error ejecutando consulta: {e}")
            raise
    
    def add_query(self, module: str, query_name: str, query: str):
        """Añade una consulta al cache."""
        cache_key = f"{module}.{query_name}"
        self.queries_cache[cache_key] = query
        logger.info(f"Consulta añadida: {cache_key}")


# Instancia global
sql_query_manager = SQLQueryManager()