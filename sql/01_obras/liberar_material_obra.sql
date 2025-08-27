UPDATE obra_materiales 
SET cantidad_asignada = 0,
    fecha_modificacion = GETDATE()
WHERE obra_id = @obra_id 
  AND material_id = @material_id
