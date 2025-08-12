SELECT COUNT(*) 
FROM mantenimientos
WHERE estado = 'PROGRAMADO' AND fecha_programada 
BETWEEN GETDATE() AND DATEADD(day, 30, GETDATE())
