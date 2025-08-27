-- select_estado_usuario.sql
-- Obtiene el estado activo y bloqueado de un usuario
-- Parámetros: :user_id

SELECT activo, bloqueado 
FROM usuarios 
WHERE id = :user_id