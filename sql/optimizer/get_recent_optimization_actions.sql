-- Obtener acciones de optimización recientes
SELECT TOP 20 
    action_type, 
    table_name, 
    details, 
    success, 
    execution_time, 
    timestamp
FROM optimization_actions 
ORDER BY timestamp DESC
