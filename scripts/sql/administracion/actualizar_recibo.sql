-- Actualizar recibo existente
UPDATE recibos
SET fecha_recibo = ?,
    cliente = ?,
    concepto = ?,
    monto = ?,
    metodo_pago = ?,
    referencia_pago = ?,
    fecha_modificacion = GETDATE()
WHERE id = ?