-- Consulta base para paginación de usuarios
-- Archivo: get_base_query_usuarios.sql

SELECT * FROM usuarios WHERE activo = 1 ORDER BY fecha_creacion DESC;
