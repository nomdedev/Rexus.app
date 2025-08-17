-- Actualizar estado de orden de compra
UPDATE compras 
SET estado = ?, 
    fecha_actualizacion = GETDATE() 
WHERE id = ?