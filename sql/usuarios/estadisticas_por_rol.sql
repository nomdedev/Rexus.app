-- Contar usuarios agrupados por rol
SELECT rol, COUNT(*)
FROM usuarios
WHERE activo = 1
GROUP BY rol