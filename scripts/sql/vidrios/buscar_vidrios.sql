-- Consulta segura para buscar vidrios por término
-- Reemplaza f-string en buscar_vidrios()
-- Parámetros: termino (4 veces para los diferentes campos)

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