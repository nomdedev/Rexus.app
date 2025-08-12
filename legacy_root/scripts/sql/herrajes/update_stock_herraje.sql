UPDATE herrajes SET
    stock_actual = @nuevo_stock,
    fecha_actualizacion = GETDATE()
WHERE id = @herraje_id;

UPDATE herrajes_inventario SET
    stock_actual = @nuevo_stock,
    fecha_ultima_entrada = CASE WHEN @tipo_movimiento IN ('ENTRADA', 'AJUSTE') THEN GETDATE() ELSE fecha_ultima_entrada END,
    fecha_ultima_salida = CASE WHEN @tipo_movimiento = 'SALIDA' THEN GETDATE() ELSE fecha_ultima_salida END
WHERE herraje_id = @herraje_id;
