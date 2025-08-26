-- Insertar acción de optimización en el log
INSERT INTO optimization_actions 
(action_type, table_name, details, success, execution_time, timestamp)
VALUES (?, ?, ?, ?, ?, ?)
