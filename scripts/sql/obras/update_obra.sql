-- Script para actualizar datos de una obra existente
-- Utiliza parámetros para evitar SQL injection

UPDATE obras
SET nombre = ?, descripcion = ?, cliente = ?, direccion = ?,
    telefono_contacto = ?, email_contacto = ?, fecha_inicio = ?, fecha_fin_estimada = ?,
    presupuesto_total = ?, estado = ?, tipo_obra = ?, prioridad = ?,
    responsable = ?, observaciones = ?, updated_at = GETDATE(),
    usuario_modificacion = ?
WHERE id = ? AND activo = 1