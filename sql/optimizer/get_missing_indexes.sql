-- Obtener sugerencias de índices faltantes con alto impacto
SELECT TOP 10
    OBJECT_SCHEMA_NAME(mid.object_id) as schema_name,
    OBJECT_NAME(mid.object_id) as table_name,
    migs.avg_total_user_cost * (migs.avg_user_impact / 100.0) * (migs.user_seeks + migs.user_scans) as improvement_measure,
    'CREATE INDEX [IX_' + OBJECT_NAME(mid.object_id) + '_missing_' + CAST(mid.index_handle as VARCHAR(10)) + '] ON [' + 
    OBJECT_SCHEMA_NAME(mid.object_id) + '].[' + OBJECT_NAME(mid.object_id) + '] (' + 
    ISNULL(mid.equality_columns,'') + 
    CASE WHEN mid.equality_columns IS NOT NULL AND mid.inequality_columns IS NOT NULL THEN ',' ELSE '' END + 
    ISNULL(mid.inequality_columns, '') + ')' +
    ISNULL(' INCLUDE (' + mid.included_columns + ')', '') as create_statement,
    migs.avg_user_impact,
    ISNULL(mid.equality_columns,'') + ISNULL(mid.inequality_columns, '') as key_columns,
    ISNULL(mid.included_columns, '') as include_columns
FROM sys.dm_db_missing_index_groups mig
INNER JOIN sys.dm_db_missing_index_group_stats migs ON migs.group_handle = mig.index_group_handle
INNER JOIN sys.dm_db_missing_index_details mid ON mig.index_handle = mid.index_handle
WHERE migs.avg_user_impact > 20
ORDER BY improvement_measure DESC
