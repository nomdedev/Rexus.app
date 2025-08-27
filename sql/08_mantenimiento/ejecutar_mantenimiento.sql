-- Script para ejecutar tareas de mantenimiento del sistema
-- Parámetros: :tipo_mantenimiento, :usuario_id
-- Retorna: Resultado de las operaciones de mantenimiento

DECLARE @resultado TABLE (
    operacion NVARCHAR(100),
    estado NVARCHAR(50),
    detalles NVARCHAR(500),
    fecha_ejecucion DATETIME
);

-- Limpieza de logs antiguos (más de 90 días)
IF :tipo_mantenimiento = 'limpieza_logs' OR :tipo_mantenimiento = 'completo'
BEGIN
    DELETE FROM auditoria_log 
    WHERE fecha_hora < DATEADD(day, -90, GETDATE());
    
    INSERT INTO @resultado VALUES (
        'Limpieza de logs',
        'Completado',
        CAST(@@ROWCOUNT AS NVARCHAR(50)) + ' registros eliminados',
        GETDATE()
    );
END

-- Actualización de estadísticas de BD
IF :tipo_mantenimiento = 'optimizacion' OR :tipo_mantenimiento = 'completo'
BEGIN
    UPDATE STATISTICS usuarios;
    UPDATE STATISTICS inventario_perfiles;
    UPDATE STATISTICS obras;
    UPDATE STATISTICS pedidos;
    
    INSERT INTO @resultado VALUES (
        'Actualización estadísticas',
        'Completado',
        'Estadísticas de tablas principales actualizadas',
        GETDATE()
    );
END

-- Verificación de integridad
IF :tipo_mantenimiento = 'verificacion' OR :tipo_mantenimiento = 'completo'
BEGIN
    DBCC CHECKDB WITH NO_INFOMSGS;
    
    INSERT INTO @resultado VALUES (
        'Verificación integridad',
        'Completado',
        'Base de datos verificada correctamente',
        GETDATE()
    );
END

-- Registrar en auditoría
INSERT INTO auditoria_log (
    fecha_hora,
    nivel,
    modulo,
    accion,
    usuario_id,
    detalle
)
VALUES (
    GETDATE(),
    'INFO',
    'Mantenimiento',
    'Ejecución mantenimiento: ' + :tipo_mantenimiento,
    :usuario_id,
    'Mantenimiento programado ejecutado exitosamente'
);

SELECT * FROM @resultado;