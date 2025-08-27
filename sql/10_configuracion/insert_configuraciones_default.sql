-- Inserta configuraciones por defecto (SQL Server)
MERGE configuraciones AS target
USING (VALUES 
    ('empresa_nombre', 'Rexus.app', 'string', 'empresa', 'Nombre de la empresa'),
    ('empresa_direccion', '', 'string', 'empresa', 'Dirección de la empresa'),
    ('empresa_telefono', '', 'string', 'empresa', 'Teléfono de la empresa'),
    ('empresa_email', '', 'string', 'empresa', 'Email de la empresa'),
    ('sistema_tema', 'light', 'string', 'sistema', 'Tema del sistema'),
    ('sistema_idioma', 'es', 'string', 'sistema', 'Idioma del sistema'),
    ('bd_backup_auto', 'true', 'boolean', 'database', 'Backup automático'),
    ('bd_backup_frecuencia', '24', 'number', 'database', 'Frecuencia backup (horas)'),
    ('usuario_sesion_timeout', '480', 'number', 'usuario', 'Timeout de sesión (minutos)'),
    ('sistema_logs_nivel', 'INFO', 'string', 'sistema', 'Nivel de logs')
) AS source (clave, valor, tipo, categoria, descripcion)
ON target.clave = source.clave
WHEN NOT MATCHED THEN
    INSERT (clave, valor, tipo, categoria, descripcion)
    VALUES (source.clave, source.valor, source.tipo, source.categoria, source.descripcion);
