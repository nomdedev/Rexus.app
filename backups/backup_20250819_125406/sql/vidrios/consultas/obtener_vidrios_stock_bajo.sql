SELECT
    v.id,
    v.codigo,
    v.tipo,
    v.descripcion,
    v.stock,
    v.stock_minimo,
    v.proveedor,
    v.precio
FROM vidrios v
WHERE v.activo = 1
  AND v.stock < v.stock_minimo
ORDER BY (v.stock_minimo - v.stock) DESC;