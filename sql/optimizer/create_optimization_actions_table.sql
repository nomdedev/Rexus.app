-- Crear tabla de acciones de optimización si no existe
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'optimization_actions')
BEGIN
    CREATE TABLE optimization_actions (
        id INT IDENTITY(1,1) PRIMARY KEY,
        action_type NVARCHAR(50),
        table_name NVARCHAR(128),
        details NVARCHAR(MAX),
        success BIT,
        execution_time FLOAT,
        timestamp DATETIME2 DEFAULT GETDATE(),
        INDEX IX_optimization_actions_timestamp (timestamp)
    )
END
