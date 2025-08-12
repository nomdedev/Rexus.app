# Variables de Entorno Requeridas - Rexus.app

## 🔐 **CRÍTICO: CREDENCIALES DE SEGURIDAD ELIMINADAS**

Se han eliminado **todas las credenciales hardcodeadas** del código fuente por razones de seguridad. 
Ahora **DEBE configurar** las siguientes variables de entorno antes de ejecutar la aplicación.

---

## 📋 **Variables Obligatorias**

### **API y Desarrollo**
```bash
# Credenciales API (Desarrollo)
API_ADMIN_PASSWORD=your_secure_admin_password_here
API_USER_PASSWORD=your_secure_api_password_here

# Credenciales de desarrollo
REXUS_DEV_PASSWORD=your_secure_dev_password_here
REXUS_DEV_USER=admin
REXUS_DEV_AUTO_LOGIN=true
```

### **Base de Datos**
```bash
# Configuración de base de datos
DB_PASSWORD=your_database_password_here
DB_SERVER=your_server_name
DB_DATABASE=inventario
DB_USER=sa
```

### **Modo Demo**
```bash
# Credenciales demo para testing
DEMO_ADMIN_PASSWORD=demo_secure_admin_2025
DEMO_SUPERVISOR_PASSWORD=demo_secure_supervisor_2025
DEMO_OPERADOR_PASSWORD=demo_secure_operador_2025
DEMO_CONTADOR_PASSWORD=demo_secure_contador_2025
```

### **Seguridad Adicional**
```bash
# Salt para passwords y tokens seguros
PASSWORD_SALT=your_unique_salt_here_min_32_chars
JWT_SECRET=your_jwt_secret_key_here_min_32_chars

# Configuración de entorno
APP_ENV=development  # o 'production'
```

---

## 📝 **Configuración**

### **1. Archivo .env (Recomendado)**
Crear archivo `.env.development` en la raíz del proyecto:

```bash
# .env.development
API_ADMIN_PASSWORD=Mi_Password_Seguro_Admin_2025!
API_USER_PASSWORD=Mi_Password_Seguro_API_2025!
REXUS_DEV_PASSWORD=Mi_Password_Dev_Seguro_2025!
DB_PASSWORD=Mi_Password_DB_Seguro_2025!
DEMO_ADMIN_PASSWORD=Demo_Admin_Seguro_2025!
# ... etc
```

### **2. Variables del Sistema**
En Windows:
```cmd
set API_ADMIN_PASSWORD=Mi_Password_Seguro_Admin_2025!
set API_USER_PASSWORD=Mi_Password_Seguro_API_2025!
# ... etc
```

En Linux/Mac:
```bash
export API_ADMIN_PASSWORD="Mi_Password_Seguro_Admin_2025!"
export API_USER_PASSWORD="Mi_Password_Seguro_API_2025!"
# ... etc
```

---

## ⚠️ **IMPORTANTE - SEGURIDAD**

### **❌ NO HACER:**
- ✗ Hardcodear contraseñas en el código
- ✗ Usar contraseñas débiles como "123456", "admin", etc.
- ✗ Compartir credenciales en repositorios públicos
- ✗ Usar las mismas credenciales en desarrollo y producción

### **✅ HACER:**
- ✓ Usar contraseñas fuertes (min 12 caracteres, números, símbolos)
- ✓ Diferentes credenciales para cada entorno
- ✓ Rotar contraseñas periódicamente
- ✓ Usar gestores de secretos en producción

---

## 🚨 **Mensajes de Error**

Si no configura las variables, verá estos errores:

```
[SECURITY ERROR] REXUS_DEV_PASSWORD debe definirse en variables de entorno
[SECURITY WARNING] Variables de entorno API_ADMIN_PASSWORD y API_USER_PASSWORD no definidas
[SECURITY WARNING] Credenciales demo para 'admin' no definidas en variables de entorno
```

---

## 🔧 **Verificación Rápida**

Ejecute este comando para verificar las variables:

```bash
python -c "
import os
required = ['API_ADMIN_PASSWORD', 'API_USER_PASSWORD', 'REXUS_DEV_PASSWORD', 'DB_PASSWORD']
missing = [v for v in required if not os.getenv(v)]
print('✅ Todas las variables configuradas' if not missing else f'❌ Faltan: {missing}')
"
```

---

## 📚 **Documentación Adicional**

- [Guía de Seguridad](./security/SECURITY.md)
- [Configuración de Desarrollo](./development/SETUP.md)
- [Configuración de Producción](./deployment/PRODUCTION.md)

---

**Fecha de actualización:** 11 de agosto de 2025  
**Estado:** ✅ Credenciales hardcodeadas eliminadas completamente