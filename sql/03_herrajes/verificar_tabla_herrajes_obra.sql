-- Verificar si la tabla herrajes_obra existe
-- Parámetros: Ninguno
-- Retorna: COUNT(*) de tablas encontradas

SELECT COUNT(*)
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_NAME = 'herrajes_obra';
