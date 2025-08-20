-- Búsqueda de usuarios con filtros dinámicos (SQLite)
-- Parámetros: :busqueda, :rol, :estado (opcionales)
-- Retorna: Lista de usuarios filtrada

SELECT 
    u.id, 
    u.username, 
    u.email, 
    u.nombre_completo, 
    u.departamento,
    u.cargo, 
    u.telefono, 
    u.activo, 
    u.fecha_creacion, 
    u.ultimo_acceso,
    COALESCE(ur.role_name, 'Sin Rol') as rol, 
    u.estado
FROM usuarios u
LEFT JOIN user_roles ur ON u.id = ur.user_id
WHERE 1=1
    AND (:busqueda IS NULL OR 
         u.username LIKE '%' || :busqueda || '%' OR 
         u.email LIKE '%' || :busqueda || '%' OR 
         u.nombre_completo LIKE '%' || :busqueda || '%' OR 
         u.departamento LIKE '%' || :busqueda || '%' OR 
         u.cargo LIKE '%' || :busqueda || '%')
    AND (:rol IS NULL OR :rol = 'Todos' OR ur.role_name = :rol)
    AND (:estado IS NULL OR :estado = 'Todos' OR 
         ((:estado = 'Activo' AND u.activo = 1) OR 
          (:estado = 'Inactivo' AND u.activo = 0) OR
          (:estado IN ('Suspendido', 'Bloqueado') AND u.estado = :estado)))
ORDER BY u.fecha_creacion DESC;