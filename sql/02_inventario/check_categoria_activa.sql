-- check_categoria_activa.sql
-- Verifica si existe una categoría activa en tabla categorías  
-- Parámetros: :nombre_categoria

SELECT COUNT(*) 
FROM categorias 
WHERE nombre = :nombre_categoria AND activa = 1