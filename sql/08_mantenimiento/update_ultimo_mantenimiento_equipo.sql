-- Actualiza fecha de último mantenimiento de un equipo
UPDATE equipos 
SET ultimo_mantenimiento = @fecha_ultimo_mantenimiento 
WHERE id = @equipo_id
