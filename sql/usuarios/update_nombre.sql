-- update_nombre.sql
-- Actualiza el nombre de un usuario específico
-- Parámetros: :nuevo_nombre, :user_id

UPDATE usuarios 
SET nombre = :nuevo_nombre 
WHERE id = :user_id