-- Limpiar sesiones expiradas (para job de mantenimiento)
UPDATE auth_sessions 
SET status = 'EXPIRED',
    logout_time = CURRENT_TIMESTAMP,
    logout_reason = 'TIMEOUT',
    updated_at = CURRENT_TIMESTAMP
WHERE status = 'ACTIVE' 
  AND DATEDIFF(HOUR, last_activity, CURRENT_TIMESTAMP) > ?
