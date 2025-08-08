-- Consulta de conteo para paginación de usuarios
-- Archivo: get_count_query_usuarios.sql

SELECT COUNT(*) FROM usuarios WHERE activo = 1;
