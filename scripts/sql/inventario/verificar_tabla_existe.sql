-- Verifica si una tabla existe en la base de datos
SELECT * FROM sysobjects WHERE name=? AND xtype='U'