
# [LOCK] DB Authorization Check - Verify user permissions before DB operations
# Ensure all database operations are properly authorized
# DB Authorization Check
"""
Modelo de Compras

Maneja la lógica de negocio y acceso a datos para el sistema de compras.
"""

import datetime
import logging
import os
                        return False

        try:
            cursor = self.db_connection.cursor()
            
            # Verificar que existe la compra
            compra = self.obtener_compra_por_id(compra_id)
            if not compra:
                logger.error(f"No se encontró la compra {compra_id}")
                return False

            # Eliminar primero los detalles de la compra (foreign key constraint)
            delete_details_query = self.sql_manager.get_query('compras', 'eliminar_detalles_compra')
            cursor.execute(delete_details_query, (compra_id,))
            
            # Eliminar la compra principal
            delete_query = self.sql_manager.get_query('compras', 'eliminar_compra')
            result = cursor.execute(delete_query, (compra_id,))
            
            # Confirmar transacción
            self.db_connection.commit()
            
            # Verificar que se eliminó
            rows_affected = result.rowcount
            if rows_affected > 0:
                logger.info(f"Compra {compra_id} eliminada exitosamente")
                return True
            else:
                logger.error(f"No se pudo eliminar la compra {compra_id}")
                return False

        except Exception as e:
            try:
                self.db_connection.rollback()
            except:
                pass
            return False

    def _row_to_dict(self, row, description):
        """Convierte una fila de base de datos a diccionario"""
        return {desc[0]: row[i] for i, desc in enumerate(description)}
