-- Verificar si una tabla existe en SQL Server
SELECT * FROM sysobjects WHERE name=? AND xtype='U'