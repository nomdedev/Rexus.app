-- Script para crear una nueva obra
-- Parámetros: :nombre, :descripcion, :estado, :fecha_inicio, :fecha_fin, :direccion
-- Retorna: ID de la obra creada

INSERT INTO obras (
    nombre,
    descripcion,
    estado,
    fecha_inicio,
    fecha_fin,
    direccion,
    activo,
    fecha_creacion
)
VALUES (
    :nombre,
    :descripcion,
    ISNULL(:estado, 'Planificación'),
    :fecha_inicio,
    :fecha_fin,
    :direccion,
    1,
    GETDATE()
);

SELECT SCOPE_IDENTITY() as nueva_obra_id;