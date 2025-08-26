-- Obtener tamaño y uso de espacio de una base de datos
SELECT 
    SUM(CAST(FILEPROPERTY(name, 'SpaceUsed') AS BIGINT) * 8.0 / 1024) as used_mb,
    SUM(CAST(size AS BIGINT) * 8.0 / 1024) as total_mb
FROM sys.database_files
WHERE type IN (0, 1)
