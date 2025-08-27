-- Cuenta nuevos usuarios en los últimos 30 días
SELECT COUNT(*) FROM usuarios
WHERE created_at > DATEADD(DAY, -30, GETDATE())
