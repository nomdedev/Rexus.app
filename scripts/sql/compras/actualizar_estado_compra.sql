UPDATE compras
SET estado = ?,
    fecha_actualizacion = GETDATE()
WHERE id = ?