-- Actualizar estado y fecha de modificación
UPDATE pedidos
SET estado = ?, fecha_modificacion = GETDATE()
WHERE id = ?