SELECT COUNT(*) 
FROM mantenimientos
WHERE estado = 'PROGRAMADO' AND fecha_programada < GETDATE()
