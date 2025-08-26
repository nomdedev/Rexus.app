-- Búsqueda de usuarios con filtros dinámicos (SQL Server)
-- Parámetros: @nombre, @usuario, @email, @rol, @estado (opcionales)
-- Retorna: Lista de usuarios filtrada

SELECT 
    id,
    usuario,
    nombre_completo,
    email,
    telefono,
    rol,
    estado,
    fecha_creacion,
    ultimo_acceso
FROM usuarios 
WHERE activo = 1
    AND (@nombre IS NULL OR LOWER(nombre_completo) LIKE LOWER('%' + @nombre + '%'))
    AND (@usuario IS NULL OR LOWER(usuario) LIKE LOWER('%' + @usuario + '%'))
    AND (@email IS NULL OR LOWER(email) LIKE LOWER('%' + @email + '%'))
    AND (@rol IS NULL OR rol = @rol)
    AND (@estado IS NULL OR estado = @estado)
ORDER BY nombre_completo
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