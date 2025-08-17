-- Verificar existencia de tabla de vidrios
SELECT name FROM sysobjects WHERE name = ? AND xtype = 'U'