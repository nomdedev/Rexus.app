-- Actualizar última actividad de sesión para auditoría
UPDATE auth_sessions 
SET last_activity = CURRENT_TIMESTAMP,
    updated_at = CURRENT_TIMESTAMP
WHERE session_id = ? AND status = 'ACTIVE'
