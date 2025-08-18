-- Actualizar usuario aprobador y fecha de aprobación
UPDATE pedidos
SET usuario_aprobador = ?, fecha_aprobacion = GETDATE()
WHERE id = ?