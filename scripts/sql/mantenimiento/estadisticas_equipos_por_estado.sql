SELECT estado, COUNT(*) as cantidad
FROM equipos
WHERE activo = 1
GROUP BY estado
