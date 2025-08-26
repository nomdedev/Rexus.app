-- Verificar si existe la tabla de pedidos de compra en SQL Server
SELECT COUNT(*) 
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'dbo' 
  AND TABLE_NAME = ?
  AND TABLE_TYPE = 'BASE TABLE'
