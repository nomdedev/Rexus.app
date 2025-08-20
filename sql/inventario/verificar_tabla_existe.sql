-- Verificar si tabla existe en SQLite
SELECT 
    name as TABLE_NAME
FROM sqlite_master 
WHERE type = 'table' 
    AND name = ?;