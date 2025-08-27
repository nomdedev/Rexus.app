SELECT d.id, d.codigo, d.nombre, d.descripcion, d.responsable, d.presupuesto_mensual,
d.estado, d.fecha_creacion, d.usuario_creacion
FROM [departamentos] d
WHERE d.estado = 'ACTIVO'
ORDER BY d.nombre
