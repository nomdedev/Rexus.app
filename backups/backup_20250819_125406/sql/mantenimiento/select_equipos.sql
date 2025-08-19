SELECT
    e.id, e.codigo, e.nombre, e.tipo, e.modelo, e.marca,
    e.numero_serie, e.fecha_adquisicion, e.fecha_instalacion,
    e.ubicacion, e.estado, e.valor_adquisicion, e.vida_util_anos,
    e.ultima_revision, e.proxima_revision, e.observaciones,
    e.fecha_creacion, e.fecha_modificacion
FROM [{tabla_equipos}] e
WHERE e.activo = 1
    {filtros_adicionales}
ORDER BY e.nombre