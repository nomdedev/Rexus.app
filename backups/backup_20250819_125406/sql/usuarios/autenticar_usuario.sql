SELECT
    id,
    usuario,
    password_hash,
    nombre_completo,
    email,
    telefono,
    rol,
    estado,
    intentos_fallidos,
    bloqueado_hasta,
    ultimo_acceso,
    fecha_creacion,
    fecha_modificacion
FROM [usuarios]
WHERE LOWER(usuario) = LOWER(?)
    AND activo = 1
    AND estado IN ('ACTIVO', 'PRIMERA_VEZ');