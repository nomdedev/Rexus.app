-- Verificar si existe tabla SQLite en cualquier módulo
-- Este archivo verifica la existencia de tablas en formato SQLite
-- Compatible con SQL Server y SQLite

-- Verificar tabla genérica (parámetro: nombre de tabla)
SELECT 
    CASE 
        WHEN OBJECT_ID('{tabla_nombre}', 'U') IS NOT NULL THEN 1 
        ELSE 0 
    END as table_exists,
    '{tabla_nombre}' as table_name;

-- Si existe, mostrar estructura básica
IF OBJECT_ID('{tabla_nombre}', 'U') IS NOT NULL
BEGIN
    SELECT 
        COLUMN_NAME,
        DATA_TYPE,
        IS_NULLABLE,
        COLUMN_DEFAULT
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_NAME = '{tabla_nombre}'
    ORDER BY ORDINAL_POSITION;
END