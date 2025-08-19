SELECT
    t.id,
    t.codigo,
    t.tipo,
    t.proveedor,
    t.capacidad_kg,
    t.capacidad_m3,
    t.costo_km,
    t.disponible,
    t.observaciones,
    t.fecha_creacion,
    t.fecha_modificacion
FROM [transportes] t
WHERE t.activo = 1