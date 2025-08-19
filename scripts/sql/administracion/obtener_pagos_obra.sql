SELECT
    po.id,
    po.obra_id,
    po.monto,
    po.fecha_pago,
    po.concepto,
    po.metodo_pago,
    po.referencia,
    po.estado,
    o.nombre as obra_nombre,
    o.codigo as obra_codigo
FROM pagos_obra po
LEFT JOIN obras o ON po.obra_id = o.id
WHERE 1=1