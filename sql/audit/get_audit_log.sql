-- Obtener registros de audit_trail con filtros dinámicos
SELECT * FROM audit_trail 
WHERE 1=1
  AND (@tabla IS NULL OR tabla = @tabla)
  AND (@usuario_id IS NULL OR usuario_id = @usuario_id) 
  AND (@fecha_inicio IS NULL OR fecha_cambio >= @fecha_inicio)
  AND (@fecha_fin IS NULL OR fecha_cambio <= @fecha_fin)
ORDER BY fecha_cambio DESC;
