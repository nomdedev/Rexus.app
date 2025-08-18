-- Contar usuarios activos en el último mes
SELECT COUNT(*) FROM usuarios
WHERE activo = 1 AND ultimo_acceso >= DATEADD(MONTH, -1, GETDATE())