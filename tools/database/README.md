# Database Management Tools

Esta carpeta contiene herramientas profesionales para gestión de base de datos en Rexus.app.

## Estructura

```
tools/database/
├── schema-validation/          # Scripts para validar esquemas de BD
├── column-generation/          # Scripts para generar columnas faltantes  
├── migration-scripts/          # Scripts de migración de datos
├── temp-fixes/                # Fixes temporales (eliminar después de usar)
└── README.md                  # Esta documentación
```

## Principios de Seguridad

### ✅ Buenas Prácticas
- **Scripts temporales**: Solo en `temp-fixes/`, eliminar después de usar
- **Queries parametrizadas**: Siempre usar placeholders para evitar SQL injection
- **Backup automático**: Scripts de migración crean respaldo antes de ejecutar
- **Logging detallado**: Registrar todas las operaciones realizadas
- **Validación previa**: Verificar estado antes de aplicar cambios

### ❌ Evitar
- Scripts sueltos en el directorio raíz
- Queries concatenadas con strings
- Modificaciones directas sin backup
- Scripts sin documentación
- Hardcodear credenciales

## Uso de Scripts

### 1. Scripts de Validación de Esquema
```bash
python tools/database/schema-validation/validate_module_schema.py --module=obras
```

### 2. Scripts de Generación de Columnas
```bash
python tools/database/column-generation/add_missing_columns.py --module=inventario
```

### 3. Scripts de Migración
```bash
python tools/database/migration-scripts/migrate_v1_to_v2.py --backup=true
```

### 4. Fixes Temporales
```bash
python tools/database/temp-fixes/fix_obras_columns_20250129.py
# ⚠️ ELIMINAR DESPUÉS DE USAR
```

## Estándares de Código

### Estructura de Script
```python
#!/usr/bin/env python3
"""
Nombre descriptivo del script.

Propósito: [Descripción clara del objetivo]
Uso: python script.py [argumentos]
Autor: [Nombre]
Fecha: [YYYY-MM-DD]
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Any

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/{Path(__file__).stem}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Función principal."""
    logger.info("Iniciando script...")
    # Implementación
    logger.info("Script completado.")

if __name__ == "__main__":
    main()
```

### Plantilla para Fixes Temporales
```python
"""
SCRIPT TEMPORAL - ELIMINAR DESPUÉS DE USAR

Fix: [Descripción del problema]
Fecha límite: [YYYY-MM-DD]
Responsable: [Nombre]
"""

def apply_fix():
    # Crear backup
    backup_result = create_backup()
    if not backup_result:
        logger.error("No se pudo crear backup. Abortando.")
        return False
    
    # Aplicar fix
    # [Código del fix]
    
    # Validar resultado
    if validate_fix():
        logger.info("Fix aplicado exitosamente")
        return True
    else:
        logger.error("Fix falló validación. Restaurando backup.")
        restore_backup()
        return False
```

## Conexión Segura a BD

```python
import pyodbc
from typing import Optional

class SecureDatabaseConnection:
    def __init__(self):
        self.connection = None
        
    def connect(self) -> bool:
        try:
            # Usar variables de entorno, nunca hardcodear
            server = os.getenv('DB_SERVER')
            username = os.getenv('DB_USERNAME') 
            password = os.getenv('DB_PASSWORD')
            database = os.getenv('DB_NAME')
            
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                f"UID={username};"
                f"PWD={password};"
                f"TrustServerCertificate=yes;"
            )
            
            self.connection = pyodbc.connect(conn_str)
            return True
            
        except Exception as e:
            logger.error(f"Error conectando a BD: {e}")
            return False
    
    def execute_safe_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Ejecuta query de forma segura con parámetros."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            
            if query.strip().upper().startswith('SELECT'):
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
            else:
                self.connection.commit()
                return [{"affected_rows": cursor.rowcount}]
                
        except Exception as e:
            logger.error(f"Error ejecutando query: {e}")
            self.connection.rollback()
            raise
```

## Checklist Pre-Ejecución

Antes de ejecutar cualquier script:

- [ ] Script está en la carpeta correcta
- [ ] Backup de datos críticos realizado
- [ ] Variables de entorno configuradas
- [ ] Conexión a BD de prueba verificada
- [ ] Logging configurado correctamente
- [ ] Script probado en entorno de desarrollo
- [ ] Documentación del script completa

## Checklist Post-Ejecución

Después de ejecutar scripts temporales:

- [ ] Validar que el fix funcionó correctamente
- [ ] Documentar cambios realizados
- [ ] Mover script a `temp-fixes/used/` con fecha
- [ ] Actualizar logs de cambios
- [ ] Notificar al equipo si es necesario