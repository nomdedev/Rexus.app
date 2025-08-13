-- Actualizar asiento contable existente
UPDATE libro_contable
SET fecha_asiento = ?,
    descripcion = ?,
    debe = ?,
    haber = ?,
    cuenta = ?,
    tipo_asiento = ?,
    referencia = ?,
    fecha_modificacion = GETDATE()
WHERE id = ?