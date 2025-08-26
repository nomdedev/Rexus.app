-- Verificar si columnas de timestamp existen en una tabla
SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = ? AND COLUMN_NAME = 'fecha_creacion';
