-- Consulta para obtener usuarios con filtros opcionales
-- Parámetros: :rol, :estado, :activo, :nombre_like
-- Retorna: Lista de usuarios filtrados

SELECT 
    u.id,
    u.usuario,
    u.nombre_completo,
    u.email,
    u.telefono,
    u.rol,
    u.estado,
    u.fecha_creacion,
    u.ultimo_acceso,
    u.intentos_fallidos,
    u.activo,
    CASE 
        WHEN u.activo = 1 AND u.estado = 'Activo' THEN 'Disponible'
        WHEN u.activo = 1 AND u.estado = 'Bloqueado' THEN 'Bloqueado'
        ELSE 'Inactivo'
    END as estado_completo
FROM usuarios u
WHERE u.activo = ISNULL(:activo, 1)
  AND (:rol IS NULL OR u.rol = :rol)
  AND (:estado IS NULL OR u.estado = :estado)
  AND (:nombre_like IS NULL OR u.nombre_completo LIKE '%' + :nombre_like + '%')
ORDER BY u.nombre_completo, u.usuario;