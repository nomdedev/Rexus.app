-- Eliminar un herraje por código
-- Parámetros:
--   :codigo (requerido) - Código del herraje a eliminar
-- Retorna: Filas eliminadas

DELETE FROM herrajes WHERE codigo = :codigo;
