SELECT id, codigo, nombre, razon_social, ruc, telefono, email,
direccion, contacto_principal, calificacion, activo,
fecha_registro, observaciones, tipo_proveedor,
condiciones_pago, descuento_comercial
FROM proveedores
WHERE activo = 1
ORDER BY nombre;
