SELECT id, tabla_afectada, registro_id, accion, datos_anteriores,
datos_nuevos, usuario, fecha_accion, ip_address, observaciones
FROM auditoria_contable
WHERE 1=1
ORDER BY fecha_accion DESC
