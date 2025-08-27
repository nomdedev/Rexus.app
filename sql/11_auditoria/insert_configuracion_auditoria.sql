-- Insertar configuración por defecto de auditoría
-- Parámetros: :modulo, :tabla, :auditoria_activa, :auditoria_inserts, :auditoria_updates, :auditoria_deletes, :retencion_dias, :nivel_detalle
-- Retorna: ID del registro insertado

INSERT OR IGNORE INTO auditoria_configuracion 
(modulo, tabla, auditoria_activa, auditoria_inserts, 
 auditoria_updates, auditoria_deletes, retencion_dias, nivel_detalle) 
VALUES (:modulo, :tabla, :auditoria_activa, :auditoria_inserts, 
        :auditoria_updates, :auditoria_deletes, :retencion_dias, :nivel_detalle);