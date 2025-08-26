-- Obtener lista de tablas de usuario para actualizar estadísticas
SELECT 
    SCHEMA_NAME(schema_id) as schema_name, 
    name as table_name
FROM sys.tables
WHERE type = 'U'
ORDER BY schema_name, name
