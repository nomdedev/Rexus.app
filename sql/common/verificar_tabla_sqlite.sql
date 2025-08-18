-- Verificar si existe tabla SQL Server en cualquier módulo
-- Este archivo verifica la existencia de tablas en formato SQL Server
-- Compatible con SQL Server
-- Parámetro: ? (nombre de la tabla)

SELECT 
    TABLE_NAME 
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_TYPE = 'BASE TABLE' 
    AND TABLE_NAME = ?;