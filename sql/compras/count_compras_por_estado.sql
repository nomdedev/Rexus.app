SELECT estado, COUNT(*) as cantidad
FROM compras
GROUP BY estado
ORDER BY cantidad DESC