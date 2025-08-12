-- Verifica si existe la tabla de auditoría en el sistema
SELECT * FROM sysobjects WHERE name=? AND xtype='U'