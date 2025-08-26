-- Eliminar registros de auditoría antiguos
DELETE FROM audit_trail
WHERE fecha_cambio < DATEADD(day, -?, GETDATE());
