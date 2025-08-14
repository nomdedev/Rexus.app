-- Actualizar stock de vidrio después de uso
UPDATE vidrios SET stock = stock - ?, fecha_modificacion = GETDATE() WHERE id = ?