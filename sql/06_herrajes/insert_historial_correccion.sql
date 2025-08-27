-- Registrar corrección en historial de auditoría
-- Parámetros: :registro_id, :observaciones
-- Retorna: ID del historial insertado

INSERT INTO historial (tabla, operacion, registro_id, usuario, fecha, observaciones)
VALUES ('herrajes_inventario', 'CORRECCION', :registro_id, USER_NAME(), GETDATE(), :observaciones);