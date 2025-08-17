-- Consulta segura para obtener categorías distintas
-- Utiliza la tabla consolidada 'productos'

SELECT DISTINCT categoria 
FROM productos
WHERE categoria IS NOT NULL AND categoria != '' AND activo = 1
ORDER BY categoria;