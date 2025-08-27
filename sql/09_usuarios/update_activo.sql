-- update_activo.sql
-- Actualiza el estado activo de un usuario específico
-- Parámetros: :activo, :user_id

UPDATE usuarios 
SET activo = :activo 
WHERE id = :user_id