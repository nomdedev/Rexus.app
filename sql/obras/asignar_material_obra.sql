INSERT INTO obra_materiales (
    obra_id, 
    material_id, 
    cantidad_asignada, 
    tipo_material, 
    fecha_asignacion
) VALUES (
    @obra_id, 
    @material_id, 
    @cantidad, 
    @tipo_material, 
    GETDATE()
)
