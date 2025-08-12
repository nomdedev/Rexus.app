-- Verificar existencia de tabla obras
SELECT * FROM sysobjects WHERE name=? AND xtype='U'
