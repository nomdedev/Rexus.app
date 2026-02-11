-- Eliminar relaciones de herrajes con obras
-- Parámetros:
--   :codigo (requerido) - Código del herraje
-- Retorna: Filas eliminadas

DELETE FROM herrajes_obra
WHERE herraje_id = (SELECT id FROM herrajes WHERE codigo = :codigo);
