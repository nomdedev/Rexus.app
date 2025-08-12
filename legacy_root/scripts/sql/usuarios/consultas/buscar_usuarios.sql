-- Buscar usuarios con filtros
SELECT 
    id,
    username,
    email,
    nombre_completo,
    rol,
    activo,
    ultimo_acceso,
    fecha_registro
FROM usuarios 
WHERE 1=1
    AND (%(filtro_nombre)s = '' OR username LIKE CONCAT('%%', %(filtro_nombre)s, '%%'))
    AND (%(filtro_email)s = '' OR email LIKE CONCAT('%%', %(filtro_email)s, '%%'))
    AND (%(filtro_rol)s = '' OR rol = %(filtro_rol)s)
    AND (%(activo)s = -1 OR activo = %(activo)s)
ORDER BY fecha_registro DESC;
