-- verificar_tabla_existe.sql
-- Verifica si una tabla existe en SQL Server
-- Parámetros: ? (tabla_nombre)

SELECT COUNT(*) 
FROM sysobjects 
WHERE name = ? 
  AND xtype = 'U'