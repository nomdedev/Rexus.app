-- Verificar si existe una tabla específica
-- Compatible con SQL Server y SQLite

-- Parámetro: {tabla_nombre} (nombre de la tabla a verificar)

-- Verificar si la tabla existe
SELECT 
    CASE 
        WHEN OBJECT_ID('{tabla_nombre}', 'U') IS NOT NULL THEN 1 
        ELSE 0 
    END as table_exists,
    '{tabla_nombre}' as table_name,
    CASE 
        WHEN OBJECT_ID('{tabla_nombre}', 'U') IS NOT NULL THEN 'Table found' 
        ELSE 'Table not found' 
    END as status;

-- Si existe, mostrar información de la tabla
IF OBJECT_ID('{tabla_nombre}', 'U') IS NOT NULL
BEGIN
    SELECT 
        COUNT(*) as column_count
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_NAME = '{tabla_nombre}';
    
    -- Mostrar estructura de la tabla
    SELECT 
        COLUMN_NAME,
        DATA_TYPE,
        CHARACTER_MAXIMUM_LENGTH,
        IS_NULLABLE,
        COLUMN_DEFAULT
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_NAME = '{tabla_nombre}'
    ORDER BY ORDINAL_POSITION;
END