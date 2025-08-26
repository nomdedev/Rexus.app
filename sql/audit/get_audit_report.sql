-- Obtener reporte de auditoría
SELECT TOP (100)
    id, timestamp, event_type, level, usuario_id, usuario_nombre,
    ip_address, user_agent, modulo, accion, detalles, resultado, session_id
FROM auditoria_sistema
WHERE 1=1
ORDER BY timestamp DESC;
