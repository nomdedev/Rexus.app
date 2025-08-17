SELECT
    ISNULL(SUM(
        ISNULL((SELECT SUM(dc.cantidad * dc.precio_unitario)
                FROM detalle_compras dc
                WHERE dc.compra_id = c.id), 0) - c.descuento + c.impuestos
    ), 0) as total
FROM compras c