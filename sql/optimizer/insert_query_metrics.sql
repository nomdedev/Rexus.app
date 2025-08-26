-- Insertar métricas de rendimiento de consulta
INSERT INTO query_metrics 
(query_hash, query_text, execution_time, rows_affected, 
 cpu_time, logical_reads, physical_reads, database_name, timestamp)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
