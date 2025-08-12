-- Seleccionar herramientas con filtros
SELECT 
    h.id, h.codigo, h.nombre, h.tipo, h.marca, h.modelo,
    h.numero_serie, h.fecha_adquisicion, h.ubicacion,
    h.estado, h.valor_adquisicion, h.vida_util_anos,
    h.observaciones, h.fecha_creacion
FROM [{tabla_herramientas}] h
WHERE h.activo = 1
    {filtros_adicionales}
ORDER BY h.nombre
