-- update_usuario_campo.sql
-- Actualiza el campo usuario de un usuario específico
-- Parámetros: :nuevo_usuario, :user_id

UPDATE usuarios 
SET usuario = :nuevo_usuario 
WHERE id = :user_id