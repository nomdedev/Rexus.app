# 🚀 Desarrollo con Hot-Reload - Rexus.app

## ⚡ Configuración Rápida

### 1. Configuración inicial
```bash
# Windows
setup-dev.bat

# Linux/Mac
chmod +x setup-dev.sh
./setup-dev.sh
```

### 2. Iniciar servidor de desarrollo
```bash
python dev-server-new.py
```

## 🎯 Características

✅ **Auto-login**: Sin más contraseñas durante desarrollo  
✅ **Hot-reload**: La app se reinicia automáticamente al cambiar código  
✅ **Rápido**: Reinicio en < 2 segundos  
✅ **Sin Docker**: Evita problemas de permisos y complejidad  

## 🔐 Credenciales de Desarrollo

Por defecto se usan estas credenciales automáticamente:
- **Usuario**: `admin`
- **Contraseña**: `admin`

### Cambiar credenciales
Edita el archivo `.env.development`:
```env
REXUS_DEV_USER=tu_usuario
REXUS_DEV_PASSWORD=tu_password
REXUS_DEV_AUTO_LOGIN=true
```

## 🛠️ Uso

1. **Inicia el servidor**: `python dev-server-new.py`
2. **Edita código**: Cualquier archivo `.py` en `rexus/`, `scripts/`, `resources/`
3. **Auto-reload**: La aplicación se reinicia automáticamente
4. **Sin contraseñas**: Se logea automáticamente con las credenciales configuradas

## 🔄 Comandos

```bash
# Iniciar desarrollo
python dev-server-new.py

# Parar servidor
Ctrl+C

# Ver archivos monitoreados
# Se muestran al iniciar el servidor
```

## 📂 Archivos de Configuración

- **`.env.development`**: Credenciales y configuración
- **`dev-server-new.py`**: Servidor de hot-reload
- **`rexus/core/dev_auth_manager.py`**: Gestor de auto-login

## 🚫 Producción

⚠️ **Importante**: Este sistema es **SOLO para desarrollo**

- No usar credenciales por defecto en producción
- El archivo `.env.development` no debe subirse a Git
- Para producción, usar el sistema de autenticación normal

## 📋 Troubleshooting

### Error: "watchdog not found"
```bash
pip install watchdog python-dotenv
```

### Error: "main.py not found"
Ejecutar desde el directorio raíz de Rexus.app

### La app no se logea automáticamente
Verificar que `.env.development` tenga:
```env
REXUS_DEV_AUTO_LOGIN=true
```

### Hot-reload muy lento
Ajustar en `.env.development`:
```env
HOTRELOAD_DELAY=0.5  # Reducir delay
```