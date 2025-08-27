UPDATE configuracion
SET valor = ?, fecha_modificacion = GETDATE()
WHERE clave = ?