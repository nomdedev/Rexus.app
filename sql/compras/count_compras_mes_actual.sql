SELECT COUNT(*) FROM compras
WHERE MONTH(fecha_creacion) = MONTH(GETDATE())
AND YEAR(fecha_creacion) = YEAR(GETDATE())