-- Terminar sesión de usuario para auditoría
UPDATE auth_sessions 
SET status = ?,
    logout_time = CURRENT_TIMESTAMP,
    logout_reason = ?,
    updated_at = CURRENT_TIMESTAMP
WHERE session_id = ?
