-- select_logs_seguridad.sql
-- Obtiene logs de seguridad paginados
-- Parámetros: :limit

SELECT ls.id, u.usuario, ls.accion, ls.modulo, ls.detalles,
       ls.ip_address, ls.fecha
FROM logs_seguridad ls
LEFT JOIN usuarios u ON ls.usuario_id = u.id
ORDER BY ls.fecha DESC
OFFSET 0 ROWS FETCH NEXT :limit ROWS ONLY