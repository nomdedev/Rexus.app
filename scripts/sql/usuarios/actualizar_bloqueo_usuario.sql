UPDATE usuarios
SET intentos_fallidos = ?, bloqueado_hasta = ?
WHERE usuario = ?