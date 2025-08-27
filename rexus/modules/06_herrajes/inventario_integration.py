"""
MIT License

Copyright (c) 2025 Rexus.app

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Integración Herrajes-Inventario - Rexus.app
==========================================

Proporciona servicios de integración entre el módulo de herrajes y el sistema
principal de inventario, permitiendo sincronización de stock, transferencias
y movimientos unificados.
"""

import logging
from rexus.utils.sql_query_manager import SQLQueryManager
def corregir_discrepancias(self) -> Tuple[bool, str, int]:
    """
    Corrige discrepancias de stock entre herrajes y su inventario.

    Returns:
    Tuple[bool, str, int]: (éxito, mensaje, correcciones realizadas)
    """
    # Inicializar sql_manager si no existe
    if not hasattr(self, 'sql_manager'):
        self.sql_manager = SQLQueryManager()
        
    if not self.db_connection:
        return False, "Sin conexión a la base de datos", 0

    try:
        pass  # TODO: Implementar lógica
    except Exception as e:
        logger.error(f"Error: {e}")
    cursor = self.db_connection.cursor()
    correcciones = 0

    # Obtener discrepancias
    cursor.execute("""
    SELECT h.id, h.codigo, h.stock_actual, hi.stock_actual
    FROM herrajes h
    LEFT JOIN herrajes_inventario hi ON h.id = hi.herraje_id
    WHERE h.estado = 'ACTIVO'
    AND (h.stock_actual != ISNULL(hi.stock_actual, 0))
    """)

    discrepancias = cursor.fetchall()

    for herraje_id, codigo, stock_herrajes, stock_inventario in discrepancias:
    # Usar stock_herrajes como fuente de verdad
    if stock_inventario is None:
    # Crear entrada en herrajes_inventario usando archivo SQL externo
    params = {'herraje_id': herraje_id, 'stock_actual': stock_herrajes}
    cursor.execute(
        self.sql_manager.get_query('sql/06_herrajes', 'insert_herraje_inventario.sql'),
        params
    )
    else:
    # Actualizar stock en herrajes_inventario usando archivo SQL externo
    params = {'stock_actual': stock_herrajes, 'herraje_id': herraje_id}
    cursor.execute(
        self.sql_manager.get_query('sql/06_herrajes', 'update_stock_inventario.sql'),
        params
    )

    # Registrar corrección usando archivo SQL externo
    params = {
        'registro_id': herraje_id,
        'observaciones': f"Corrección automática de stock: {stock_inventario} -> {stock_herrajes}"
    }
    cursor.execute(
        self.sql_manager.get_query('sql/06_herrajes', 'insert_historial_correccion.sql'),
        params
    )

    correcciones += 1

    self.db_connection.commit()
    return True, f"Se corrigieron {correcciones} discrepancias de stock", correcciones

    except Exception as e:
    logger.error(f"Error sincronizando stock: {e}")
    return False, f"Error: {str(e)}", 0
