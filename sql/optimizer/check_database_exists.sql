-- Verificar si existe una base de datos específica
SELECT name 
FROM sys.databases 
WHERE name = ?
