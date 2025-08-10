-- Obtener usuarios con paginación
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
WHERE activo = 1
ORDER BY fecha_registro DESC
LIMIT %(limit)s OFFSET %(offset)s;
