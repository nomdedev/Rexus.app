SELECT rol, COUNT(*)
FROM usuarios
WHERE activo = 1
GROUP BY rol