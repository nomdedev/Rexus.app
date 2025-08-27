SELECT
    id, codigo, descripcion, tipo, espesor, proveedor,
    precio_m2, color, tratamiento, dimensiones_disponibles,
    estado, observaciones, fecha_actualizacion
FROM [vidrios]
WHERE 1=1
ORDER BY tipo, espesor;