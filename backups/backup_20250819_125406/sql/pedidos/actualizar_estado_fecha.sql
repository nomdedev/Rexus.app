UPDATE pedidos
SET estado = ?, fecha_modificacion = GETDATE()
WHERE id = ?