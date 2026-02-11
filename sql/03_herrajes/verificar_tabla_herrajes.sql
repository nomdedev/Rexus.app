-- Verificar si la tabla herrajes existe
-- Parámetros: Ninguno
-- Retorna: COUNT(*) de tablas encontradas

SELECT COUNT(*)
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_NAME = 'herrajes';
