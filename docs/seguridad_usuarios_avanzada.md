# Funcionalidades Avanzadas de Seguridad de Usuarios - Rexus.app v2.0.0

## 📋 Resumen Ejecutivo

Se han implementado funcionalidades de seguridad avanzadas para el módulo de usuarios de Rexus.app, incluyendo limitación de intentos de login, bloqueo temporal de cuentas, validación de contraseñas robustas y Two-Factor Authentication (2FA).

## 🔐 Funcionalidades Implementadas

### 1. Limitación de Intentos de Login

#### Características:
- **Máximo de intentos**: 3 intentos fallidos antes del bloqueo
- **Duración del bloqueo**: 15 minutos (900 segundos)
- **Reset automático**: Los intentos se resetean después del tiempo de bloqueo
- **Logging**: Registro de todos los intentos fallidos con timestamp

#### Métodos implementados:
```python
def registrar_intento_login(self, username: str, exitoso: bool = False) -> None
def verificar_cuenta_bloqueada(self, username: str) -> bool
def reset_intentos_login(self, username: str) -> bool
```

#### Columnas de base de datos agregadas:
```sql
ALTER TABLE usuarios ADD intentos_fallidos INT DEFAULT 0;
ALTER TABLE usuarios ADD ultimo_intento_fallido DATETIME2;
ALTER TABLE usuarios ADD bloqueado_hasta DATETIME2;
```

### 2. Validación de Contraseñas Robustas

#### Reglas de complejidad:
- **Longitud mínima**: 8 caracteres
- **Mayúsculas**: Al menos una letra mayúscula
- **Minúsculas**: Al menos una letra minúscula
- **Dígitos**: Al menos un número
- **Caracteres especiales**: Al menos uno (!@#$%^&*()_+-=[]{}|;:,.<>?)

#### Método implementado:
```python
def validar_fortaleza_password(self, password: str) -> Dict[str, Any]
```

#### Respuesta del método:
```python
{
    'valida': bool,           # True si cumple todos los requisitos
    'errores': List[str],     # Lista de errores específicos
    'puntuacion': int         # Puntuación de fortaleza (0-7)
}
```

### 3. Autenticación Segura Mejorada

#### Función principal:
```python
def autenticar_usuario_seguro(self, username: str, password: str) -> Dict[str, Any]
```

#### Proceso de autenticación:
1. **Verificación de bloqueo**: Comprueba si la cuenta está bloqueada
2. **Validación de usuario**: Verifica que el usuario exista y esté activo
3. **Verificación de contraseña**: Valida con múltiples algoritmos de hash
4. **Registro de intentos**: Actualiza contadores de seguridad
5. **Preparación de sesión**: Prepara datos seguros para la sesión

#### Respuesta del método:
```python
{
    'success': bool,                    # True si autenticación exitosa
    'user_data': dict | None,          # Datos del usuario (sin password_hash)
    'message': str,                    # Mensaje descriptivo
    'blocked_until': datetime | None,   # Tiempo de bloqueo si aplica
    'attempts_remaining': int          # Intentos restantes antes del bloqueo
}
```

### 4. Two-Factor Authentication (2FA)

#### Características:
- **Protocolo**: TOTP (Time-based One-Time Password) RFC 6238
- **Algoritmo**: HMAC-SHA1
- **Código**: 6 dígitos
- **Período**: 30 segundos
- **Ventana de tolerancia**: ±30 segundos

#### Métodos principales:
```python
def habilitar_2fa_usuario(self, usuarios_model, username: str) -> Dict[str, Any]
def verificar_setup_2fa(self, usuarios_model, username: str, codigo_verificacion: str) -> bool
def validar_2fa_login(self, usuarios_model, username: str, codigo_2fa: str) -> bool
def deshabilitar_2fa(self, usuarios_model, username: str) -> bool
```

#### Proceso de configuración:
1. **Generación de clave secreta**: Base32 de 160 bits
2. **Código QR**: Para configurar apps móviles
3. **Verificación inicial**: Validación del primer código
4. **Habilitación permanente**: Activación después de verificación exitosa

## 🛠️ Configuración y Uso

### Configuración de Base de Datos

1. **Ejecutar migración**:
```bash
sqlcmd -S servidor -d rexus_db -i scripts/database/add_security_columns.sql
```

2. **Verificar columnas agregadas**:
```sql
SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'usuarios';
```

### Uso en la Aplicación

#### Autenticación básica:
```python
usuarios_model = UsuariosModel(db_connection)
resultado = usuarios_model.autenticar_usuario_seguro("admin", "password123")

if resultado['success']:
    user_data = resultado['user_data']
    print(f"Login exitoso: {user_data['nombre_completo']}")
else:
    print(f"Error: {resultado['message']}")
    print(f"Intentos restantes: {resultado['attempts_remaining']}")
```

#### Configuración de 2FA:
```python
from utils.two_factor_auth import two_factor_auth, agregar_metodo_configuracion_personal

# Agregar método de configuración al modelo
agregar_metodo_configuracion_personal(usuarios_model)

# Habilitar 2FA
resultado = two_factor_auth.habilitar_2fa_usuario(usuarios_model, "admin")
if resultado['success']:
    qr_code_base64 = resultado['qr_code']
    secret_key = resultado['secret_key']
    # Mostrar QR al usuario para configurar app móvil
```

#### Validación con 2FA:
```python
# Después de autenticación básica exitosa
if two_factor_auth.validar_2fa_login(usuarios_model, username, codigo_2fa):
    print("Autenticación 2FA exitosa")
else:
    print("Código 2FA inválido")
```

## 📊 Métricas de Seguridad

### Configuración actual:
- **MAX_LOGIN_ATTEMPTS**: 3 intentos
- **LOCKOUT_DURATION**: 900 segundos (15 minutos)
- **MIN_PASSWORD_LENGTH**: 8 caracteres
- **2FA_PERIOD**: 30 segundos
- **2FA_WINDOW**: ±1 período (tolerancia de 30 segundos)

### Indicadores de seguridad:
- ✅ Prevención de ataques de fuerza bruta
- ✅ Protección contra enumeración de usuarios
- ✅ Validación de contraseñas robustas
- ✅ Autenticación de dos factores opcional
- ✅ Registro de actividad de seguridad
- ✅ Recuperación automática de bloqueos

## 🧪 Testing

### Tests de limitación de intentos:
```python
def test_limitacion_intentos():
    # Simular 3 intentos fallidos
    for i in range(3):
        resultado = usuarios_model.autenticar_usuario_seguro("user", "wrong_password")
        assert not resultado['success']
    
    # Verificar bloqueo
    assert usuarios_model.verificar_cuenta_bloqueada("user")
```

### Tests de validación de contraseñas:
```python
def test_validacion_password():
    resultado = usuarios_model.validar_fortaleza_password("Password123!")
    assert resultado['valida'] == True
    assert resultado['puntuacion'] >= 5
```

### Tests de 2FA:
```python
def test_2fa_completo():
    # Habilitar 2FA
    resultado = two_factor_auth.habilitar_2fa_usuario(usuarios_model, "testuser")
    assert resultado['success']
    
    secret_key = resultado['secret_key']
    
    # Generar código válido
    codigo = two_factor_auth.generar_codigo_totp(secret_key)
    
    # Verificar setup
    assert two_factor_auth.verificar_setup_2fa(usuarios_model, "testuser", codigo)
    
    # Validar login con 2FA
    nuevo_codigo = two_factor_auth.generar_codigo_totp(secret_key)
    assert two_factor_auth.validar_2fa_login(usuarios_model, "testuser", nuevo_codigo)
```

## 🔒 Consideraciones de Seguridad

### Fortalezas implementadas:
1. **Prevención de ataques de fuerza bruta**: Bloqueo temporal después de intentos fallidos
2. **Validación de contraseñas**: Reglas de complejidad configurables
3. **2FA opcional**: Capa adicional de seguridad
4. **Logging de seguridad**: Registro de todos los intentos de autenticación
5. **Recuperación automática**: Desbloqueo automático después del período configurado

### Recomendaciones adicionales:
1. **Monitoreo**: Implementar alertas para múltiples intentos fallidos
2. **Análisis de logs**: Revisar patrones de intentos fallidos regularmente
3. **Backup de claves 2FA**: Implementar códigos de respaldo para 2FA
4. **Educación de usuarios**: Capacitar sobre seguridad de contraseñas
5. **Auditorías regulares**: Revisar configuraciones de seguridad periódicamente

## 📝 Próximos Pasos

### Mejoras futuras sugeridas:
1. **Códigos de respaldo 2FA**: Para recuperación sin dispositivo móvil
2. **Notificaciones de seguridad**: Emails para intentos fallidos
3. **Políticas de contraseñas**: Expiración y historial
4. **Sesiones múltiples**: Control de sesiones concurrentes
5. **Geolocalización**: Detectar accesos desde ubicaciones inusuales

---

**Documento generado**: 5 de Agosto de 2025  
**Versión**: 2.0.0  
**Estado**: ✅ Completado  
**Autor**: GitHub Copilot
