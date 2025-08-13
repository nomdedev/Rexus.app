-- Verificar existencia de tabla en SQL Server
-- Parámetro: nombre de tabla
SELECT * FROM sysobjects WHERE name=? AND xtype='U'