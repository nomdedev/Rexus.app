-- Consulta segura para obtener todas las obras
-- Utiliza la tabla 'obras' con la estructura real de la base de datos
-- Los parámetros se deben pasar desde el código usando prepared statements

SELECT 
    id, codigo, nombre, descripcion, cliente,
    fecha_inicio, fecha_fin_estimada, fecha_fin_real,
    etapa_actual, estado, progreso,
    presupuesto_total, costo_actual, margen_estimado,
    ubicacion, responsable, observaciones,
    activo, created_at, updated_at
FROM obras 
WHERE activo = 1
    -- Filtros opcionales a agregar con parámetros seguros:
    -- AND estado = ?
    -- AND etapa_actual = ?
    -- AND cliente = ?
    -- AND responsable = ?
ORDER BY fecha_inicio DESC;