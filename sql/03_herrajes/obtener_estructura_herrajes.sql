-- Obtener estructura de la tabla herrajes
-- Parámetros: Ninguno
-- Retorna: Lista de columnas con sus tipos de datos

SELECT COLUMN_NAME, DATA_TYPE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'herrajes'
ORDER BY ORDINAL_POSITION;
