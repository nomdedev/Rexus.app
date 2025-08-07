UPDATE obras
SET nombre = ?, descripcion = ?, cliente = ?, direccion = ?,
    telefono_contacto = ?, email_contacto = ?, fecha_fin_estimada = ?,
    presupuesto_total = ?, estado = ?, tipo_obra = ?, prioridad = ?,
    responsable = ?, observaciones = ?, fecha_modificacion = GETDATE(),
    usuario_modificacion = ?
WHERE id = ?