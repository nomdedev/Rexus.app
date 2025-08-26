-- Obtener eventos de auditoría por tipo de evento
SELECT COUNT(*) as total
FROM auditoria_sistema
WHERE event_type = ?;
