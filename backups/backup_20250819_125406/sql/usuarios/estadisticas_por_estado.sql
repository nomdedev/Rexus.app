SELECT estado, COUNT(*)
FROM usuarios
WHERE activo = 1
GROUP BY estado