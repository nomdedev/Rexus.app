-- scripts/sql/logistica/verificar_tabla_existe.sql
-- Verifica si una tabla específica existe en la base de datos
SELECT * FROM sysobjects WHERE name=? AND xtype='U'