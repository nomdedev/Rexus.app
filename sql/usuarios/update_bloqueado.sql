-- update_bloqueado.sql
-- Actualiza el estado bloqueado de un usuario específico
-- Parámetros: :bloqueado, :user_id

UPDATE usuarios 
SET bloqueado = :bloqueado 
WHERE id = :user_id