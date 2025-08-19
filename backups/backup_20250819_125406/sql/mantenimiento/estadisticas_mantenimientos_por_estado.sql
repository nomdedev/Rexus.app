SELECT estado, COUNT(*) as cantidad
FROM mantenimientos
GROUP BY estado
