-- Obtener usuarios con permisos optimizado (JOIN para eliminar N+1)
SELECT u.id, u.usuario, u.nombre_completo, u.email, u.telefono, u.rol, u.estado,
       u.fecha_creacion, u.ultimo_acceso, u.intentos_fallidos,
       p.modulo as permiso
FROM usuarios u
LEFT JOIN permisos_usuario p ON u.id = p.usuario_id
WHERE u.activo = 1
ORDER BY u.nombre_completo, p.modulo