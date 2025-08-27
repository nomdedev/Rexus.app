SELECT 
    COALESCE(SUM(om.cantidad_asignada * v.precio), 0) as costo_total
FROM obra_materiales om
LEFT JOIN vidrios v ON om.material_id = v.id AND om.tipo_material = 'vidrio'
WHERE om.obra_id = @obra_id
  AND om.cantidad_asignada > 0
