-- Cuenta usuarios con login reciente (últimos 7 días)
SELECT COUNT(*) FROM usuarios
WHERE last_login > DATEADD(DAY, -7, GETDATE())
