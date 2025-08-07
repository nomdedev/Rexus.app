-- Consulta segura para obtener vidrios con filtros
-- Reemplaza f-string en obtener_todos_vidrios()
-- Todos los parámetros se deben pasar usando prepared statements

SELECT
    id, codigo, descripcion, tipo, espesor, proveedor,
    precio_m2, color, tratamiento, dimensiones_disponibles,
    estado, observaciones, fecha_actualizacion
FROM [vidrios]
WHERE 1=1
-- Filtros dinámicos se agregan desde el código:
-- AND proveedor LIKE ? (when filtros.get("proveedor"))
-- AND tipo LIKE ? (when filtros.get("tipo"))  
-- AND espesor = ? (when filtros.get("espesor"))
ORDER BY tipo, espesor;