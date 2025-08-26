-- Obtener historial de sesiones de un usuario para auditoría
SELECT 
    session_id,
    usuario,
    ip_address,
    user_agent,
    login_time,
    logout_time,
    DATEDIFF(MINUTE, login_time, COALESCE(logout_time, last_activity)) as duration_minutes,
    status,
    logout_reason
FROM auth_sessions 
WHERE user_id = ?
ORDER BY login_time DESC
