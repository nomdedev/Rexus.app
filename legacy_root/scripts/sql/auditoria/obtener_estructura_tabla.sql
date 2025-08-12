-- Obtiene la estructura de columnas de la tabla de auditoría
SELECT COLUMN_NAME, DATA_TYPE 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = ?