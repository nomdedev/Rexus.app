-- Verificar existencia de tabla detalles_obra
SELECT * FROM sysobjects WHERE name=? AND xtype='U'
