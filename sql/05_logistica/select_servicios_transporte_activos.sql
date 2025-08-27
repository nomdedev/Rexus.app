SELECT st.id, st.codigo, st.descripcion, st.tipo_servicio,
       st.origen, st.destino, st.fecha_programada, st.fecha_real,
       st.estado, st.costo_estimado, st.costo_real,
       st.capacidad_peso, st.capacidad_volumen, st.observaciones,
       pt.nombre as proveedor_nombre
FROM servicios_transporte st
LEFT JOIN proveedores_transporte pt ON st.proveedor_transporte_id = pt.id
WHERE st.activo = 1
ORDER BY st.fecha_programada DESC;
