-- check_codigo_existe.sql
-- Verifica si un código de producto ya existe
-- Parámetros: ? (codigo_producto)

SELECT COUNT(*) 
FROM productos 
WHERE codigo = ?