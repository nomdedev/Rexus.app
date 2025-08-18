SELECT id, usuario, nombre_completo, email, telefono, rol, estado,
       fecha_creacion, fecha_modificacion, ultimo_acceso, intentos_fallidos,
       bloqueado_hasta, avatar, configuracion_personal
FROM usuarios
WHERE id = ? AND activo = 1