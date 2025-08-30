# Configuración Segura de Rexus.app

## Variables de Entorno Requeridas

Para una configuración segura, configure las siguientes variables de entorno:

### Base de Datos
```bash
export REXUS_DB_SERVER="tu_servidor_db"
export REXUS_DB_PORT="1433"
export REXUS_DB_NAME="rexus_db"
export REXUS_DB_USER="tu_usuario_db"
export REXUS_DB_PASSWORD="tu_password_seguro"
```

### Email (para notificaciones)
```bash
export REXUS_EMAIL_SMTP_SERVER="smtp.gmail.com"
export REXUS_EMAIL_SMTP_PORT="587"
export REXUS_EMAIL_USER="tu_email@gmail.com"
export REXUS_EMAIL_PASSWORD="tu_password_app"
export REXUS_EMAIL_SSL="true"
```

### Sistema
```bash
export REXUS_DEBUG="false"
export REXUS_LOG_LEVEL="INFO"
```

## Configuración del Archivo

1. Copie `config/rexus_config.example.json` a `config/rexus_config.json`
2. Configure los valores básicos (no confidenciales) en el archivo JSON
3. Las credenciales sensibles deben configurarse únicamente via variables de entorno

## Archivo .env (Opcional)

Para desarrollo local, puede crear un archivo `.env`:

```bash
cp .env.example .env
# Edite .env con sus valores reales
```

**⚠️ IMPORTANTE:** Nunca commitee el archivo `.env` al repositorio. Asegúrese de que esté en `.gitignore`.

## Verificación

Ejecute el script de configuración para verificar:

```bash
python -c "from rexus.utils.secure_config import get_config; c = get_config(); print('✅ Configuración OK' if not c.validate_required(['database.server', 'database.user', 'database.password']) else '❌ Configuración incompleta')"
```

## Seguridad

- ✅ Credenciales en variables de entorno (nunca en código)
- ✅ Archivo de configuración separado de credenciales
- ✅ Validación de configuración requerida
- ✅ Logging de configuración cargada (sin mostrar passwords)
- ✅ Soporte para diferentes entornos (desarrollo, producción)
