-- Actualiza un asiento contable existente
-- Parámetros: fecha_asiento, tipo_asiento, concepto, referencia, debe, haber, saldo, estado, asiento_id
UPDATE libro_contable
SET fecha_asiento = ?, tipo_asiento = ?, concepto = ?, referencia = ?,
    debe = ?, haber = ?, saldo = ?, estado = ?, fecha_modificacion = GETDATE()
WHERE id = ?