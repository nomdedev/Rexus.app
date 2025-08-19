INSERT INTO equipos (
    codigo, nombre, tipo, modelo, marca, numero_serie,
    fecha_adquisicion, fecha_instalacion, ubicacion, estado,
    valor_adquisicion, vida_util_anos, observaciones,
    fecha_creacion, fecha_modificacion, activo
) VALUES (
    ?, ?, ?, ?, ?, ?,
    ?, ?, ?, ?,
    ?, ?, ?,
    GETDATE(), GETDATE(), 1
);