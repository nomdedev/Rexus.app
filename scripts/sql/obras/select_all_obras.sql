-- Consulta segura para obtener todas las obras
-- Utiliza la tabla 'obras'
-- Los parámetros se deben pasar desde el código usando prepared statements

SELECT 
    id, codigo_obra, nombre, descripcion, cliente_id,
    fecha_inicio, fecha_fin_estimada, fecha_fin_real,
    etapa_actual, estado, porcentaje_completado,
    presupuesto_inicial, costo_actual, margen_estimado,
    ubicacion, responsable_obra, observaciones,
    activo, fecha_creacion, fecha_actualizacion
FROM obras 
WHERE activo = 1
    -- Filtros opcionales a agregar con parámetros seguros:
    -- AND estado = ?
    -- AND etapa_actual = ?
    -- AND cliente_id = ?
    -- AND responsable_obra = ?
ORDER BY fecha_inicio DESC;