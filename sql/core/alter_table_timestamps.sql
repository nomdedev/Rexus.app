-- Archivo SQL: Agregar columnas de timestamp a tabla
-- Ubicación: sql/core/alter_table_timestamps.sql
-- Propósito: Correción SQL injection en audit_trail.py línea 462

ALTER TABLE {tabla_name}
ADD fecha_creacion DATETIME DEFAULT GETDATE(),
    fecha_actualizacion DATETIME DEFAULT GETDATE();