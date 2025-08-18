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
    AND (? = '' OR username LIKE '%' + ? + '%')
    AND (? = '' OR email LIKE '%' + ? + '%')
    AND (? = '' OR rol = ?)
    AND (? = -1 OR activo = ?)
ORDER BY fecha_registro DESC;
