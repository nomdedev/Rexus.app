SELECT
    v.id, v.codigo, v.descripcion, v.tipo, v.espesor, v.proveedor,
    v.precio_m2, vo.metros_cuadrados_requeridos, vo.metros_cuadrados_pedidos,
    vo.medidas_especificas, vo.fecha_asignacion, vo.observaciones as obs_obra
FROM [vidrios] v
INNER JOIN [vidrios_obra] vo ON v.id = vo.vidrio_id
WHERE vo.obra_id = ?
ORDER BY v.tipo, v.espesor;