SELECT u.id, u.usuario, u.nombre_completo, u.email, u.telefono, u.rol, u.estado,
       u.fecha_creacion, u.ultimo_acceso, u.intentos_fallidos,
       p.modulo as permiso
FROM usuarios u
LEFT JOIN permisos_usuario p ON u.id = p.usuario_id
WHERE u.activo = 1 AND (
    LOWER(u.nombre_completo) LIKE ? OR
    LOWER(u.usuario) LIKE ? OR
    LOWER(u.email) LIKE ?
)
ORDER BY u.nombre_completo, p.modulo