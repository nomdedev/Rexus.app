-- update_email.sql
-- Actualiza el email de un usuario específico
-- Parámetros: :nuevo_email, :user_id

UPDATE usuarios 
SET email = :nuevo_email 
WHERE id = :user_id