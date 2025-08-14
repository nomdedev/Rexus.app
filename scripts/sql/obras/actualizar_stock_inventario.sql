-- Actualizar cantidad disponible en inventario después de uso
UPDATE inventario SET cantidad_disponible = cantidad_disponible - ?, fecha_modificacion = GETDATE() WHERE id = ?