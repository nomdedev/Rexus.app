SELECT rol, COUNT(*) as cantidad
FROM usuarios
WHERE activo = 1
GROUP BY rol
