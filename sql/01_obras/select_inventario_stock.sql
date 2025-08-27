SELECT cantidad_disponible 
FROM inventario 
WHERE id = @material_id 
  AND activo = 1
