-- Insertar evento en auditoria_sistema
INSERT INTO auditoria_sistema 
(event_type, level, usuario_id, usuario_nombre, ip_address, 
 user_agent, modulo, accion, detalles, resultado, session_id)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
