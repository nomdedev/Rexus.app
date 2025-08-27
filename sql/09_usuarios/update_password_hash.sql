-- update_password_hash.sql
-- Actualiza el hash de contraseña de un usuario específico
-- Parámetros: :password_hash, :user_id

UPDATE usuarios 
SET password_hash = :password_hash 
WHERE id = :user_id