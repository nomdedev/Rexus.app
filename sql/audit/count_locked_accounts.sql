-- Contar cuentas bloqueadas
SELECT COUNT(*) as total
FROM auditoria_sistema
WHERE event_type = 'ACCOUNT_LOCKED' AND timestamp >= ?;
