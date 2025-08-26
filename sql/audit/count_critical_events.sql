-- Contar eventos críticos
SELECT COUNT(*) as total
FROM auditoria_sistema
WHERE level = 'CRITICAL' AND timestamp >= ?;
