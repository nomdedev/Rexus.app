-- Verificar si existe una tabla específica usando sys.tables (SQL Server moderno)
SELECT COUNT(*) 
FROM sys.tables 
WHERE name = ?
