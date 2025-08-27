-- update_rol.sql
-- Actualiza el rol de un usuario específico
-- Parámetros: :nuevo_rol, :user_id

UPDATE usuarios 
SET rol = :nuevo_rol 
WHERE id = :user_id