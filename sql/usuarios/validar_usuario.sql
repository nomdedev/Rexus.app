-- Consulta para validar credenciales de usuario
-- Parámetros: :usuario, :password
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
WHERE u.usuario = :usuario 
  AND u.password_hash = HASHBYTES('SHA2_256', :password + u.salt)
  AND u.activo = 1
  AND u.estado = 'Activo';