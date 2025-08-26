-- Inserta un nuevo equipo (versión simplificada)
INSERT INTO equipos (nombre, tipo, estado, ubicacion, fecha_instalacion)
VALUES (@nombre, @tipo, @estado, @ubicacion, @fecha_instalacion)
