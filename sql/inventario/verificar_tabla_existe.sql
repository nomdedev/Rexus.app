-- Verificar si existe una tabla específica en inventario
-- Compatible con SQL Server
-- Parámetro: ? (nombre de la tabla a verificar)

SELECT 
    TABLE_NAME 
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_TYPE = 'BASE TABLE' 
    AND TABLE_NAME = ?;
