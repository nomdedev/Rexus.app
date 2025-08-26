UPDATE inventario 
SET cantidad_disponible = cantidad_disponible - @cantidad, 
    fecha_modificacion = GETDATE() 
WHERE id = @material_id
