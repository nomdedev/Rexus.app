-- Verificar si un herraje existe por código
-- Parámetros:
--   :codigo (requerido) - Código del herraje
-- Retorna: ID del herraje si existe

SELECT id FROM herrajes WHERE codigo = :codigo;
