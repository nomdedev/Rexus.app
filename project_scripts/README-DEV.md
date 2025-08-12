# 🚀 Guía de Desarrollo con Hot-Reload

## Opciones de Desarrollo

### 1. Desarrollo Local (Recomendado)
```bash
# Opción 1: Con Makefile
make dev

# Opción 2: Scripts directos
./start-dev.sh    # Linux/Mac
start-dev.bat     # Windows

# Opción 3: Python directo
python dev-server.py
```

### 2. Desarrollo con Docker
```bash
# Con Makefile
make dev-docker

# O directamente
docker-compose up --build
```

## Instalación de Dependencias

### Para desarrollo local:
```bash
make install
# O manualmente:
pip install -r requirements.txt
pip install watchdog python-dotenv folium PyQt6-WebEngine
```

## Características del Hot-Reload

### ✅ Lo que se reinicia automáticamente:
- Cambios en archivos `.py`
- Lógica de negocio
- UI/Widgets
- Configuración

### ⚠️ Lo que requiere reinicio manual:
- Cambios en `requirements.txt`
- Variables de entorno
- Configuración de base de datos

## Acceso a la Aplicación

### Desarrollo Local:
- La app se ejecuta directamente en tu sistema
- Hot-reload en tiempo real

### Desarrollo Docker:
- App disponible via VNC: `http://localhost:6080`
- Usuario VNC: `developer` (sin contraseña)
- Resolución: 1920x1080

## Comandos Útiles

```bash
# Ver logs de desarrollo
make dev          # Incluye logs del hot-reload

# Reconstruir containers
make build

# Limpiar todo
make clean

# Ver ayuda
make help
```

## Estructura de Archivos de Desarrollo

```
📁 Desarrollo Hot-Reload
├── 🐳 Dockerfile          # Container de desarrollo
├── 🐳 docker-compose.yml  # Orquestación completa
├── 🔥 dev-server.py       # Servidor de hot-reload
├── 🛠️ Makefile           # Comandos rápidos
├── 🐧 start-dev.sh       # Script Linux/Mac
├── 🪟 start-dev.bat      # Script Windows
└── ⚙️ .env.docker        # Variables de entorno
```

## Solución de Problemas

### Error de permisos en Linux:
```bash
chmod +x start-dev.sh
```

### Puerto ocupado:
- Cambiar puerto en `docker-compose.yml` (línea 8)
- O detener otros servicios: `make clean`

### Dependencias faltantes:
```bash
make install  # Instala todo lo necesario
```

## Tips de Productividad

1. **Guarda y ve cambios inmediatos** - El hot-reload detecta cambios al guardar
2. **Usa el desarrollo local** - Es más rápido que Docker
3. **Docker para testing final** - Simula entorno de producción
4. **Logs en tiempo real** - Ve errores inmediatamente

¡Listo para desarrollo ultra-rápido! 🚀
