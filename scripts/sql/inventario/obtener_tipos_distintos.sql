-- Obtener tipos distintos de perfiles
SELECT DISTINCT tipo 
FROM inventario_perfiles 
WHERE activo = 1 
ORDER BY tipo