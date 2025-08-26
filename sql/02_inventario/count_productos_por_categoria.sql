-- count_productos_por_categoria.sql
-- Cuenta productos por categoría específica
-- Parámetros: :categoria

SELECT COUNT(*) 
FROM inventario 
WHERE categoria = :categoria