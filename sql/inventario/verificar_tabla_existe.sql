-- Verificar si existe una tabla específica en inventario
-- Compatible con SQL Server

-- Parámetro: @tabla_nombre (nombre de la tabla a verificar)
-- Por defecto verifica la tabla 'inventario'

DECLARE @tabla_nombre NVARCHAR(128) = 'inventario';

-- Verificar si la tabla existe
IF OBJECT_ID(@tabla_nombre, 'U') IS NOT NULL
BEGIN
    SELECT 
        1 as table_exists,
        @tabla_nombre as table_name,
        'Table found' as status,
        COUNT(*) as column_count
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_NAME = @tabla_nombre;
    
    -- Mostrar estructura de la tabla
    SELECT 
        COLUMN_NAME,
        DATA_TYPE,
        CHARACTER_MAXIMUM_LENGTH,
        IS_NULLABLE,
        COLUMN_DEFAULT
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_NAME = @tabla_nombre
    ORDER BY ORDINAL_POSITION;
END
ELSE
BEGIN
    SELECT 
        0 as table_exists,
        @tabla_nombre as table_name,
        'Table not found' as status,
        0 as column_count;
END
