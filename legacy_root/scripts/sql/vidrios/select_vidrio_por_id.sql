-- Consulta segura para obtener vidrio por ID
-- Reemplaza f-string en obtener_vidrio_por_id()
-- Parámetros: vidrio_id (int)

SELECT
    id, codigo, descripcion, tipo, espesor, proveedor,
    precio_m2, color, tratamiento, dimensiones_disponibles,
    estado, observaciones, fecha_actualizacion
FROM [vidrios]
WHERE id = ?;