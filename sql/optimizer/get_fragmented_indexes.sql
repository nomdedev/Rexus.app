-- Obtener índices con alta fragmentación
SELECT 
    OBJECT_SCHEMA_NAME(ips.object_id) as schema_name,
    OBJECT_NAME(ips.object_id) as table_name,
    i.name as index_name,
    ips.avg_fragmentation_in_percent,
    ips.page_count
FROM sys.dm_db_index_physical_stats(DB_ID(), NULL, NULL, NULL, 'LIMITED') ips
INNER JOIN sys.indexes i ON ips.object_id = i.object_id AND ips.index_id = i.index_id
WHERE ips.avg_fragmentation_in_percent > 30
  AND ips.page_count > 1000
  AND i.type > 0
ORDER BY ips.avg_fragmentation_in_percent DESC
