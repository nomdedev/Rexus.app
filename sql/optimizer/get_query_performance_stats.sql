-- Obtener estadísticas detalladas de consultas para monitoreo
SELECT TOP 50
    qs.total_elapsed_time / qs.execution_count as avg_elapsed_time_us,
    qs.execution_count,
    qs.total_logical_reads / qs.execution_count as avg_logical_reads,
    qs.total_physical_reads / qs.execution_count as avg_physical_reads,
    qs.total_worker_time / qs.execution_count as avg_cpu_time_us,
    qs.last_execution_time,
    SUBSTRING(qt.text, (qs.statement_start_offset/2)+1,
        ((CASE qs.statement_end_offset
            WHEN -1 THEN DATALENGTH(qt.text)
            ELSE qs.statement_end_offset
        END - qs.statement_start_offset)/2)+1) as query_text
FROM sys.dm_exec_query_stats qs
CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) qt
WHERE qs.total_elapsed_time / qs.execution_count > ?
ORDER BY avg_elapsed_time_us DESC
