UPDATE pedidos
SET subtotal = ?,
    descuento = ?,
    impuestos = ?,
    total = ?
WHERE id = ?;