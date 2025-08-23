            logger.info(f"[PEDIDOS] Error eliminando pedido: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False
