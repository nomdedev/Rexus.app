-- Verificar si usuario está bloqueado
SELECT bloqueado_hasta FROM usuarios 
WHERE usuario = ? AND bloqueado_hasta > CURRENT_TIMESTAMP
