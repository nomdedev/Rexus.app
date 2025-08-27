-- Registrar evento de auditoría
-- Parámetros: :usuario, :accion, :modulo, :tabla_afectada, :registro_id, :datos_anteriores, :datos_nuevos, :detalles, :nivel_riesgo, :ip_address, :user_agent, :resultado
-- Retorna: ID del evento registrado

INSERT INTO auditoria_eventos 
(usuario, accion, modulo, tabla_afectada, registro_id, 
 datos_anteriores, datos_nuevos, detalles, nivel_riesgo,
 ip_address, user_agent, resultado)
VALUES (:usuario, :accion, :modulo, :tabla_afectada, :registro_id,
        :datos_anteriores, :datos_nuevos, :detalles, :nivel_riesgo,
        :ip_address, :user_agent, :resultado);