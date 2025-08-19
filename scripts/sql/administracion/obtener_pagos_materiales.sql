SELECT
    pm.id,
    pm.proveedor_id,
    pm.monto,
    pm.fecha_pago,
    pm.concepto,
    pm.metodo_pago,
    pm.referencia,
    pm.estado,
    p.nombre as proveedor_nombre,
    p.razon_social as proveedor_razon_social
FROM pagos_materiales pm
LEFT JOIN proveedores p ON pm.proveedor_id = p.id
WHERE 1=1