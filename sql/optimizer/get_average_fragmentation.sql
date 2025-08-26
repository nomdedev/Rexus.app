-- Obtener fragmentación promedio de índices
SELECT AVG(avg_fragmentation_in_percent)
FROM sys.dm_db_index_physical_stats(DB_ID(), NULL, NULL, NULL, 'LIMITED')
WHERE index_level = 0 
  AND page_count > 1000
