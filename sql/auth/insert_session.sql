-- Insertar nueva sesión de usuario para auditoría
INSERT INTO auth_sessions 
(session_id, user_id, usuario, ip_address, user_agent, login_time, last_activity, status)
VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'ACTIVE')
