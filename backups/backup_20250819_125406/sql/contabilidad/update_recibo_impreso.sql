UPDATE recibos
SET impreso = 1, fecha_impresion = GETDATE()
WHERE id = ?