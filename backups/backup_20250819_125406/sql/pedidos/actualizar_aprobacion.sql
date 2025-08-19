UPDATE pedidos
SET usuario_aprobador = ?, fecha_aprobacion = GETDATE()
WHERE id = ?