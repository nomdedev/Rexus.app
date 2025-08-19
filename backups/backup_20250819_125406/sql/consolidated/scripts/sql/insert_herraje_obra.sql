INSERT INTO productos_obra (herraje_id, obra_id, cantidad_requerida, fecha_asignacion, observaciones)
VALUES (@herraje_id, @obra_id, @cantidad_requerida, GETDATE(), @observaciones);