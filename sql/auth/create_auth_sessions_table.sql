-- Crear tabla de sesiones con capacidades de auditoría
CREATE TABLE auth_sessions (
    id INT IDENTITY(1,1) PRIMARY KEY,
    session_id NVARCHAR(128) NOT NULL UNIQUE,
    user_id INT NOT NULL,
    usuario NVARCHAR(50) NOT NULL,
    ip_address NVARCHAR(45),
    user_agent NVARCHAR(500),
    login_time DATETIME2 NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_activity DATETIME2 NOT NULL DEFAULT CURRENT_TIMESTAMP,
    logout_time DATETIME2 NULL,
    status NVARCHAR(20) NOT NULL DEFAULT 'ACTIVE', -- ACTIVE, EXPIRED, TERMINATED, LOCKED
    logout_reason NVARCHAR(50) NULL, -- MANUAL, TIMEOUT, ADMIN_FORCE, SECURITY
    created_at DATETIME2 NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME2 NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Índices para performance en auditoría
    INDEX IX_auth_sessions_user_id (user_id),
    INDEX IX_auth_sessions_session_id (session_id),
    INDEX IX_auth_sessions_login_time (login_time),
    INDEX IX_auth_sessions_status (status),
    INDEX IX_auth_sessions_ip_address (ip_address),
    
    -- Relación con tabla usuarios
    FOREIGN KEY (user_id) REFERENCES usuarios(id)
);
