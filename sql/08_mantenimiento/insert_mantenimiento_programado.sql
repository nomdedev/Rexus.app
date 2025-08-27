-- Programa un nuevo mantenimiento
INSERT INTO mantenimientos_programados (equipo_id, fecha_programada, tipo, observaciones, estado)
VALUES (@equipo_id, @fecha_programada, @tipo, @observaciones, 'programado')
