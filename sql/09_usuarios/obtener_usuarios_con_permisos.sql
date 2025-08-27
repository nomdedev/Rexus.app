SELECT
    u.id,
    u.usuario as username,
    u.email,
    u.nombre_completo,
    u.rol,
    u.activo,
    u.fecha_creacion,
    u.fecha_modificacion as fecha_actualizacion,
    u.ultimo_acceso,
    u.intentos_fallidos,
    u.bloqueado_hasta as fecha_bloqueo,
    u.configuracion_personal as configuracion,
    u.configuracion_personal as preferencias
FROM usuarios u
WHERE u.activo = 1
ORDER BY u.fecha_creacion DESC