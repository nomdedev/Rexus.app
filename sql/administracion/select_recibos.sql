-- Obtener recibos con filtros
SELECT 
    r.numero_recibo,
    r.fecha_emision,
    r.empleado_emisor,
    r.descripcion,
    r.monto,
    r.destinatario,
    r.concepto,
    r.impreso,
    r.archivo_pdf
FROM [{tabla_recibos}] r
WHERE 1=1
