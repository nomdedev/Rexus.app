-- Archivo SQL: Obtener logs de auditoría con filtros
-- Ubicación: sql/core/select_audit_log_filtered.sql  
-- Propósito: Corrección SQL injection en audit_trail.py get_audit_log()

SELECT TOP {limit} * FROM audit_trail 
WHERE 1=1
{tabla_filter}
{usuario_filter}
{fecha_inicio_filter}
{fecha_fin_filter}
ORDER BY fecha_cambio DESC;