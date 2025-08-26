-- Contar número de índices activos
SELECT COUNT(*) 
FROM sys.indexes 
WHERE type > 0
