-- Crear tabla de métricas de consultas si no existe
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'query_metrics')
BEGIN
    CREATE TABLE query_metrics (
        id INT IDENTITY(1,1) PRIMARY KEY,
        query_hash NVARCHAR(64),
        query_text NVARCHAR(MAX),
        execution_time FLOAT,
        rows_affected INT,
        cpu_time FLOAT,
        logical_reads INT,
        physical_reads INT,
        database_name NVARCHAR(128),
        timestamp DATETIME2 DEFAULT GETDATE(),
        INDEX IX_query_metrics_timestamp (timestamp),
        INDEX IX_query_metrics_execution_time (execution_time)
    )
END
