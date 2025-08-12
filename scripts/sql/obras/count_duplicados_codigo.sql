-- Consulta para verificar duplicados por código de obra
-- Utiliza la estructura real de la base de datos

SELECT COUNT(*) 
FROM obras 
WHERE codigo = ? 
AND activo = 1;