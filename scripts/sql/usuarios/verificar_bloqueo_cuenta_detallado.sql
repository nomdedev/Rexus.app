-- Verifica si un usuario está bloqueado con detalles de tiempo
SELECT intentos_fallidos, bloqueado_hasta 
FROM usuarios 
WHERE usuario = ?