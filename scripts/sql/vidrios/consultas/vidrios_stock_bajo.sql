SELECT COUNT(*) as stock_bajo
FROM vidrios v
WHERE v.activo = 1
  AND v.stock < v.stock_minimo;