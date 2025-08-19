SELECT tipo, COUNT(*) as cantidad
FROM [vidrios]
WHERE estado = 'ACTIVO'
GROUP BY tipo
ORDER BY cantidad DESC;