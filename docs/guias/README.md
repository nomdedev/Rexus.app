# Guias para Desarrolladores

Esta carpeta contiene guías prácticas y tutoriales para desarrolladores que trabajan en el proyecto Rexus.app.

## Guias Disponibles

### Guias Principales

| Documento | Descripción | Duración de Lectura |
|-----------|-------------|---------------------|
| **[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)** | Guía completa de desarrollo | 20-30 min |
| **[GUIA_N1_QUICKSTART.md](GUIA_N1_QUICKSTART.md)** | Corrección del problema N+1 | 15-20 min |
| **[CACHING_QUICKSTART.md](CACHING_QUICKSTART.md)** | Implementación de caché Redis | 10-15 min |
| **[REPOSITORY_SERVICE_PATTERN.md](REPOSITORY_SERVICE_PATTERN.md)** | Arquitectura Repository + Service | 20-25 min |
| **[MONITOREO_PROMETHEUS_GRAFANA.md](MONITOREO_PROMETHEUS_GRAFANA.md)** | Sistema de monitoreo | 15-20 min |

## Por Dónde Empezar

### Para Nuevos Desarrolladores
1. **Primero:** Lea `DEVELOPER_GUIDE.md` - Configuración del entorno
2. **Después:** Revise `../CLAUDE.md` (raíz) - Reglas críticas de desarrollo
3. **Luego:** Consulte `CROSSREFERENCES.md` para encontrar temas relacionados

### Para Optimizar Performance
1. `GUIA_N1_QUICKSTART.md` - Entender y corregir problemas N+1
2. `CACHING_QUICKSTART.md` - Implementar caché Redis
3. `../progreso/OPTIMIZACION_N1_COMPLETADAS.md` - Ver ejemplos reales

### Para Mejorar Arquitectura
1. `REPOSITORY_SERVICE_PATTERN.md` - Aprender el patrón
2. `../tecnica/ANALISIS_TECNICO_COMPLETO.md` - Entender arquitectura actual
3. `../progreso/PLAN_MEJORA_GOD_OBJECTS.md` - Plan de refactorización

### Para Implementar Monitoreo
1. `MONITOREO_PROMETHEUS_GRAFANA.md` - Configurar Prometheus y Grafana
2. `../auditoria/AUDITORIA_EXPERTA_2025/FASE3_2_AUDITORIA_LOGGING_MONITOREO.md` - Auditoría de monitoreo

## Resumen de Contenido por Guía

### DEVELOPER_GUIDE.md
- Instalación y configuración del entorno
- Testing y cobertura de código
- Calidad de código (linting, formateo)
- CI/CD Pipeline
- Git Workflow
- Troubleshooting común

### GUIA_N1_QUICKSTART.md
- Explicación del problema N+1 con ejemplos visuales
- Cómo identificar N+1 en tu código
- Soluciones con JOIN vs queries en bucle
- Ejemplos reales corregidos del proyecto
- Métricas de mejora (50-100x más rápido)

### CACHING_QUICKSTART.md
- Instalación rápida de Redis (5 minutos)
- Aplicar caching a modelos existentes
- Decoradores vs caching manual
- Invalidación de caché
- Monitoreo de hit rate
- Troubleshooting

### REPOSITORY_SERVICE_PATTERN.md
- Arquitectura de acceso a datos y lógica de negocio
- Componentes: BaseRepository, BaseService
- Guía de migración paso a paso
- Ejemplo completo: ProductoService
- Beneficios y mejores prácticas

### MONITOREO_PROMETHEUS_GRAFANA.md
- Sistema de monitoreo en tiempo real
- Instalación y configuración
- Métricas disponibles (HTTP, BD, caché, errores)
- Alertas configuradas
- Dashboards de Grafana
- Queries útiles de Prometheus

## Snippets Rápidos

### Ejecutar Tests
```bash
# Suite completa
pytest tests/ -v

# Con cobertura
pytest tests/ --cov=rexus --cov-report=html

# Tests específicos
pytest tests/security/ -v
```

### Verificar Código
```bash
# Formatear
black rexus/ tests/

# Linting
flake8 rexus/ tests/

# Type checking
mypy rexus/
```

### Caché Redis
```python
from rexus.utils.cache_manager import cache_result, CacheConfig

@cache_result(tipo_dato='estadisticas', ttl=CacheConfig.TTL_MEDIO)
def obtener_estadisticas(self):
    # Código aquí
    pass
```

### Repository Pattern
```python
from rexus.repositories.base import BaseRepository
from rexus.services.base import BaseService

class MiRepositorio(BaseRepository):
    def __init__(self, db_connection, sql_manager):
        super().__init__(db_connection, sql_manager)

class MiServicio(BaseService):
    def __init__(self, db_connection, sql_manager, cache_manager):
        super().__init__(MiRepositorio(db_connection, sql_manager), cache_manager)
```

## Documentos Relacionados

- **[CROSSREFERENCES.md](../CROSSREFERENCES.md)** - Enlaces cruzados entre temas
- **[README.md](../README.md)** - Documentación principal
- **[CLAUDE.md](../CLAUDE.md)** - Reglas críticas de desarrollo
- **[../auditoria/README.md](../auditoria/README.md)** - Documentación de auditorías

## Próximos Pasos

Después de leer estas guías:
1. Revise la sección de **Progreso** para ver el estado actual
2. Consulte las **Auditorías** para entender áreas de mejora
3. Lea **Técnica** para深入了解 la arquitectura del sistema
