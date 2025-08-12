SELECT estado, COUNT(*) as cantidad
FROM obras
GROUP BY estado
ORDER BY cantidad DESC