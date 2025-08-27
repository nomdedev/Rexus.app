-- update_recibo_impreso_con_pdf.sql
-- Actualiza el estado de impresión de un recibo incluyendo archivo PDF
-- Parámetros: ? (archivo_pdf), ? (usuario_actualizacion), ? (recibo_id)

UPDATE recibos
SET impreso = 1, 
    archivo_pdf = ?, 
    fecha_actualizacion = GETDATE(),
    usuario_actualizacion = ?
WHERE id = ?