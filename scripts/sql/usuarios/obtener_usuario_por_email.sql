-- Obtiene un usuario por su email
SELECT id, usuario, password_hash, nombre_completo, email, telefono, rol, estado,
       fecha_creacion, fecha_modificacion, ultimo_acceso, intentos_fallidos, bloqueado_hasta, avatar, configuracion_personal, activo
FROM usuarios WHERE email = ?