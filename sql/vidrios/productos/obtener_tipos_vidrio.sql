-- Obtener tipos de vidrio únicos
SELECT DISTINCT tipo 
FROM vidrios 
WHERE activo = 1 
ORDER BY tipo;
