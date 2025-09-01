-- Consulta para validar credenciales de usuario
-- Parámetros: ?, ?  (usuario, password_hash)
-- Retorna: Información del usuario si es válido

SELECT 
    u.id,
    u.usuario,
    u.nombre_completo,
    u.email,
    u.rol,
    u.estado,
    u.ultimo_acceso,
    u.activo,
    'Login exitoso' as mensaje
FROM usuarios u
WHERE u.usuario = ? 
  AND u.password_hash = ?
  AND u.activo = 1
  AND u.estado = 'Activo';