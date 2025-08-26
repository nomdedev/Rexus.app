-- Obtener estadísticas por tipo de vidrio
SELECT tipo, COUNT(*) as cantidad
FROM vidrios
WHERE activo = 1
GROUP BY tipo
ORDER BY cantidad DESC;
