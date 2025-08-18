-- Verificar si existe tabla SQLite en el módulo de obras
-- Este archivo verifica la existencia de tablas en formato SQLite
-- Compatible con SQL Server y SQLite

IF OBJECT_ID('obras', 'U') IS NOT NULL
    SELECT 1 as table_exists, 'obras' as table_name
ELSE
    SELECT 0 as table_exists, 'obras' as table_name;

-- Verificar estructura básica de tabla obras si existe
IF OBJECT_ID('obras', 'U') IS NOT NULL
BEGIN
    SELECT 
        COLUMN_NAME,
        DATA_TYPE,
        IS_NULLABLE,
        COLUMN_DEFAULT
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_NAME = 'obras'
    ORDER BY ORDINAL_POSITION;
END
