-- update_apellido.sql
-- Actualiza el apellido de un usuario específico
-- Parámetros: :nuevo_apellido, :user_id

UPDATE usuarios 
SET apellido = :nuevo_apellido 
WHERE id = :user_id