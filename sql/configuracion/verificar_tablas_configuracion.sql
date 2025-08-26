-- Archivo SQL: Verificar que existan las tablas de configuración
-- Ubicación: sql/configuracion/verificar_tablas_configuracion.sql
-- Propósito: Verificar estructura de BD existente (NO crear tablas)

SELECT COUNT(*) as tabla_count
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_NAME = 'configuracion_sistema' 
  AND TABLE_SCHEMA = 'dbo';