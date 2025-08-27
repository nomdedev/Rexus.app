-- Cerrar sesiones expiradas automáticamente  
-- Parámetros: :tiempo_limite
-- Retorna: filas afectadas

UPDATE sesiones
SET activa = 0, 
    closed_at = GETDATE()
WHERE activa = 1 AND last_activity < :tiempo_limite;