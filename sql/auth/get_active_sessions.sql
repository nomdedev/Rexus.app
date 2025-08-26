-- Obtener sesiones activas para monitoreo de seguridad
SELECT 
    s.session_id,
    s.usuario,
    s.ip_address,
    s.user_agent,
    s.login_time,
    s.last_activity,
    DATEDIFF(MINUTE, s.last_activity, CURRENT_TIMESTAMP) as inactive_minutes,
    u.rol,
    u.nombre,
    u.apellido
FROM auth_sessions s
INNER JOIN usuarios u ON s.user_id = u.id
WHERE s.status = 'ACTIVE'
ORDER BY s.last_activity DESC
