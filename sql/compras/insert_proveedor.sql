INSERT INTO proveedores (
    codigo, nombre, razon_social, ruc, telefono, email, 
    direccion, contacto_principal, calificacion, activo,
    fecha_registro, observaciones, tipo_proveedor,
    condiciones_pago, descuento_comercial
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
