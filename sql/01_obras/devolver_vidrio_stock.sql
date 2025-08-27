UPDATE vidrios
SET stock = stock + @cantidad,
    fecha_modificacion = GETDATE()
WHERE id = @material_id
