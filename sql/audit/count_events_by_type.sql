-- Contar eventos por tipo
SELECT event_type, COUNT(*) as total
FROM auditoria_sistema
WHERE timestamp >= ?
GROUP BY event_type
ORDER BY total DESC;
