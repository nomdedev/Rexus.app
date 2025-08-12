# Cómo Ejecutar Rexus.app

## Punto de Entrada Único

Después de la reorganización profesional del código, **Rexus.app se ejecuta desde un único punto de entrada**:

```bash
python main.py
```

## Estructura Actualizada

```
rexus-app/
├── main.py              # 🚀 PUNTO DE ENTRADA ÚNICO
├── rexus/               # Paquete principal de la aplicación
│   ├── main/
│   │   └── app.py       # Aplicación PyQt6 principal
│   ├── core/            # Núcleo del sistema
│   ├── modules/         # Módulos de negocio
│   └── utils/           # Utilidades compartidas
├── tools/               # Scripts de desarrollo
├── tests/               # Tests organizados
└── docs/                # Documentación
```

## Métodos de Ejecución

### 1. Ejecución Normal (Recomendado)
```bash
# Desde el directorio raíz del proyecto
python main.py
```

### 2. Ejecución con Python 3 Específico
```bash
python3 main.py
```

### 3. Ejecución en Windows
```cmd
# PowerShell o CMD
python main.py

# O con Python específico
py -3 main.py
```

### 4. Ejecución en Linux/macOS
```bash
# Hacer ejecutable (una sola vez)
chmod +x main.py

# Ejecutar directamente
./main.py
```

## Variables de Entorno Requeridas

Antes de ejecutar, configurar en un archivo `.env`:

```env
# Configuración de Base de Datos
DB_SERVER=tu_servidor_sql
DB_USERNAME=tu_usuario
DB_PASSWORD=tu_contraseña
DB_NAME=tu_base_de_datos
DB_USERS=tabla_usuarios

# Configuración Opcional
ENVIRONMENT=development
LOG_LEVEL=INFO
```

## Flujo de Inicio

1. **main.py** → Configuración del entorno
2. **rexus.main.app** → Aplicación PyQt6 principal
3. **Carga de módulos** → Inventario, Obras, Usuarios, etc.
4. **Interface de usuario** → Sidebar y vistas modulares

## Solución de Problemas

### Error: "No module named 'rexus'"
```bash
# Verificar que estás en el directorio correcto
pwd  # Debe mostrar: .../Rexus.app

# Verificar que existe la carpeta rexus/
ls -la rexus/
```

### Error: "Variables de entorno no encontradas"
```bash
# Crear archivo .env en la raíz del proyecto
cp .env.example .env  # Si existe ejemplo
# O crear manualmente con las variables requeridas
```

### Error: "No se puede conectar a la base de datos"
```bash
# Verificar que SQL Server esté ejecutándose
# Verificar credenciales en .env
# Probar conexión manualmente
```

## Scripts de Desarrollo

### Validar Esquema de Base de Datos
```bash
python tools/database/schema-validation/validate_module_schema.py --module=obras
```

### Ejecutar Tests
```bash
# Tests específicos
python -m pytest tests/modules/obras/

# Todos los tests
python -m pytest tests/
```

### Scripts de Mantenimiento
```bash
# Limpiar archivos temporales
python tools/maintenance/cleanup.py

# Analizar estructura de módulos
python tools/maintenance/analyze_modules.py
```

## ⚠️ Archivos Obsoletos

Los siguientes archivos **NO** se usan más después de la reorganización:

- ❌ `run.py` - Reemplazado por `main.py`
- ❌ `run_app.py` - Reemplazado por `main.py`  
- ❌ `inicio_rexus.py` - Reemplazado por `main.py`
- ❌ Scripts sueltos en raíz - Movidos a `tools/`

## ✅ Verificación de Instalación

Para verificar que todo está correctamente configurado:

```bash
# 1. Verificar Python
python --version  # Debe ser 3.8+

# 2. Verificar dependencias
pip install -r requirements.txt

# 3. Verificar estructura
ls -la main.py rexus/

# 4. Ejecutar aplicación
python main.py
```

## Credenciales por Defecto

Una vez que la aplicación inicie:

- **Usuario**: `admin`
- **Contraseña**: `admin`

## Soporte

Si tienes problemas:

1. Verificar que estás en el directorio correcto
2. Verificar variables de entorno
3. Verificar logs en `logs/rexus.log`
4. Revisar documentación en `docs/`

---

**Recordatorio**: Siempre usar `python main.py` como punto de entrada único.