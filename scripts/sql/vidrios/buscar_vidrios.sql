SELECT
    id, codigo, descripcion, tipo, espesor, proveedor,
    precio_m2, color, tratamiento, estado
FROM [vidrios]
WHERE
    (codigo LIKE ? OR
     descripcion LIKE ? OR
     tipo LIKE ? OR
     proveedor LIKE ?)
    AND estado = 'ACTIVO'
ORDER BY tipo, espesor;