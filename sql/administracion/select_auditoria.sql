-- Obtener auditoría con filtros
SELECT 
    a.id,
    a.fecha_accion,
    a.tabla,
    a.registro_id,
    a.accion,
    a.usuario,
    a.descripcion,
    a.datos_anteriores,
    a.datos_nuevos
FROM [{tabla_auditoria}] a
WHERE 1=1
