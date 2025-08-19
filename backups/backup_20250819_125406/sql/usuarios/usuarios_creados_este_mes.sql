SELECT COUNT(*) FROM usuarios
WHERE activo = 1 AND MONTH(fecha_creacion) = MONTH(GETDATE())
AND YEAR(fecha_creacion) = YEAR(GETDATE())