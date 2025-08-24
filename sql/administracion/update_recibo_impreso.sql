-- Actualizar recibo como impreso
UPDATE [{tabla_recibos}] 
SET impreso = 1, archivo_pdf = ? 
WHERE numero_recibo = ?
