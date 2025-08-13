-- Actualiza el stock de un producto en inventario_perfiles
UPDATE inventario_perfiles
SET stock_actual = ?, fecha_modificacion = GETDATE(), usuario_modificacion = ?
WHERE id = ?