-- Insertar registro en audit_trail
INSERT INTO audit_trail (
    tabla, 
    accion, 
    registro_id, 
    usuario_id, 
    usuario_nombre, 
    datos_anteriores, 
    datos_nuevos, 
    modulo, 
    detalles, 
    ip_address
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
