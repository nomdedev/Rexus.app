SELECT id, codigo, nombre, descripcion, responsable, presupuesto_mensual,
estado, fecha_creacion, usuario_creacion
FROM departamentos
WHERE estado = 'ACTIVO'
ORDER BY nombre
