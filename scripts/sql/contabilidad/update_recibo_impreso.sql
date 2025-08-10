-- Marca un recibo como impreso
-- Parámetros: recibo_id
UPDATE recibos
SET impreso = 1, fecha_impresion = GETDATE()
WHERE id = ?