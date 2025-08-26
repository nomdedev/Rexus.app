-- Contar intentos de login fallidos
SELECT COUNT(*) as total
FROM auditoria_sistema
WHERE event_type = 'AUTH_FAILURE' AND timestamp >= ?;
