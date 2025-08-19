SELECT
    id, producto, proveedor, cantidad, precio_unitario,
    total, pagado, pendiente, estado, fecha_compra,
    fecha_pago, usuario_creacion
FROM pagos_materiales
WHERE
    (? IS NULL OR ? = 'Todos' OR proveedor = ?)
    AND (? IS NULL OR ? = 'Todos' OR estado = ?)
ORDER BY fecha_compra DESC