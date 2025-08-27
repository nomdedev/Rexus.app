INSERT INTO servicios_transporte (
    codigo, descripcion, tipo_servicio, proveedor_transporte_id,
    origen, destino, fecha_programada, fecha_real,
    estado, costo_estimado, costo_real, observaciones,
    capacidad_peso, capacidad_volumen, activo, fecha_creacion
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
