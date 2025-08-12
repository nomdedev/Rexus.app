-- Consulta segura para obtener estadísticas de vidrios por tipo
-- Reemplaza f-string en obtener_estadisticas()
-- Sin parámetros

SELECT tipo, COUNT(*) as cantidad
FROM [vidrios]
WHERE estado = 'ACTIVO'
GROUP BY tipo
ORDER BY cantidad DESC;