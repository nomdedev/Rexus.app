SELECT 
    om.material_id,
    om.cantidad_asignada,
    om.tipo_material,
    om.fecha_asignacion,
    v.descripcion,
    v.precio
FROM obra_materiales om
LEFT JOIN vidrios v ON om.material_id = v.id AND om.tipo_material = 'vidrio'
WHERE om.obra_id = @obra_id
  AND om.cantidad_asignada > 0
