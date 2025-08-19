UPDATE productos SET
    stock_actual = ?,
    stock_disponible = stock_actual - stock_reservado,
    fecha_actualizacion = GETDATE()
WHERE id = ? AND activo = 1;