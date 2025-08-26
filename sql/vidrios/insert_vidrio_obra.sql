INSERT INTO vidrios_por_obra
(vidrio_id, obra_id, metros_cuadrados_requeridos, medidas_especificas, fecha_asignacion, observaciones)
VALUES (@vidrio_id, @obra_id, @metros_cuadrados, @medidas_especificas, GETDATE(), @observaciones)
