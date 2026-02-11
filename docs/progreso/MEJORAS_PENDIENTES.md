# Mejoras Pendientes - Rexus.app

**Fecha de actualizacion:** 2025-02-10
**Version:** 2.0.0
**Estado:** Planificacion de mejoras identificadas

---

## Resumen Ejecutivo

Este documento consolida todas las mejoras identificadas en el proyecto, priorizadas por impacto y esfuerzo. Las mejoras se derivan de auditorias de codigo, analisis de arquitectura y mejores practicas enterprise.

---

## 1. Refactorizacion de God Objects - ALTA PRIORIDAD

### Estado Actual

| Modelo | Lineas | Estado | Submodulos |
|--------|--------|--------|------------|
| **InventarioModel** | 3,149 | ⚠️ God Object | ✅ Ya dividido en managers |
| **UsuariosModel** | 1,790 | ⚠️ God Object | ⚠️ Parcialmente dividido |
| **ObrasModel** | 801 | ✅ Aceptable | ⚠️ Puede mejorar |

### InventarioModel - Ya Mejorado ✅

El modelo de inventario ya tiene una arquitectura de submodulos implementada:

```
rexus/modules/02_inventario/
├── model.py (orquestador con proxies)
└── submodules/
    ├── base_utilities.py
    ├── productos_manager.py
    ├── movimientos_manager.py
    ├── reservas_manager.py
    ├── reportes_manager.py
    ├── categorias_manager.py
    └── consultas_manager.py
```

**Proximos Pasos para Inventario:**
1. **Eliminar codigo fallback** una vez validada la migracion
2. **Mover logica de negocio** desde `model.py` a los managers
3. **Optimizar queries** en cada manager especializado

---

### Plan para UsuariosModel (1,790 lineas)

#### Estructura Propuesta

```
rexus/modules/11_usuarios/
├── model.py (orquestador)
└── submodules/
    ├── auth_manager.py (ya existe - actualizar)
    ├── users_manager.py (gestion de usuarios)
    ├── permissions_manager.py (permisos y roles)
    ├── sessions_manager.py (sesiones y tokens)
    └── profiles_manager.py (perfiles de usuario)
```

#### Responsabilidades por Modulo

**auth_manager.py**
- Login y logout
- Verificacion de contraseñas
- Rate limiting de intentos fallidos
- Bloqueo de cuentas

**users_manager.py**
- CRUD de usuarios
- Gestion de estados (activo/inactivo)
- Validaciones de datos de usuario

**permissions_manager.py**
- Definicion de roles y permisos
- Asignacion de permisos a usuarios
- Verificacion de acceso

**sessions_manager.py**
- Gestion de sesiones activas
- Tokens de recuperacion
- Historial de logins

**profiles_manager.py**
- Informacion personal del usuario
- Preferencias de configuracion
- Avatar y metadata

---

### Plan para ObrasModel (801 lineas)

#### Estructura Propuesta

```
rexus/modules/01_obras/
├── model.py (orquestador)
├── produccion/
│   ├── estados_manager.py
│   ├── tareas_manager.py
│   └── cronograma_manager.py
└── presupuestos/
    ├── costos_manager.py
    ├── materiales_manager.py
    └── valuation_manager.py
```

#### Responsabilidades por Modulo

**estados_manager.py**
- Gestion de estados de obra
- Transiciones de estado
- Historial de cambios

**tareas_manager.py**
- Tareas de la obra
- Asignacion de personal
- Seguimiento de progreso

**cronograma_manager.py**
- Fechas de inicio y fin
- Hitos del proyecto
- Alertas de plazos

**costos_manager.py**
- Presupuesto inicial
- Costos adicionales
- Variaciones de presupuesto

**materiales_manager.py**
- Materiales por obra
- Reservas de inventario
- Consumo real vs estimado

**valuation_manager.py**
- Valorizaciones periodicas
- Certificados de avance
- Estado de pago

---

### Estrategia de Migracion

#### Fase 1: Preparacion (1-2 dias)
1. Crear estructura de directorios
2. Crear archivos de submodulos vacios
3. Mapear funciones del model.py a submodulos

#### Fase 2: Extraccion (3-5 dias)
1. Mover codigo a submodulos respectivos
2. Crear metodos proxy en model.py
3. Mantener codigo original como fallback

#### Fase 3: Validacion (2-3 dias)
1. Ejecutar tests existentes
2. Crear nuevos tests por submodulo
3. Verificar funcionalidad completa

#### Fase 4: Limpieza (1-2 dias)
1. Eliminar codigo fallback
2. Actualizar documentacion
3. Eliminar codigo duplicado

---

### Metricas de Exito

| Metrica | Antes | Despues | Objetivo |
|---------|-------|---------|----------|
| Lineas model.py | 3,149 | <500 | -85% |
| Complejidad ciclomatica | Alta | Baja | <10 por metodo |
| Tests por modulo | 0 | >5 | Cobertura >70% |
| Tiempo de ejecucion | Baseline | = o < | Sin degradacion |

---

### Cronograma Estimado

| Tarea | Duracion | Comienzo | Fin |
|-------|----------|----------|-----|
| UsuariosModel refactor | 8-10 horas | Dia 1 | Dia 2 |
| ObrasModel refactor | 6-8 horas | Dia 3 | Dia 4 |
| Validacion y tests | 4-6 horas | Dia 4 | Dia 5 |
| Documentacion | 2-3 horas | Dia 5 | Dia 5 |

**Total estimado:** 20-27 horas (3-4 dias)

---

## 2. Monitoreo con Prometheus/Grafana - MEDIA PRIORIDAD

### Objetivo
Implementar monitoreo en tiempo real de metricas de aplicacion.

### Componentes a Implementar
- Prometheus metrics exporter
- Metricas personalizadas (queries por segundo, tiempos de respuesta)
- Dashboards en Grafana
- Alertas configuradas
- Integracion con logging actual

### Beneficios Esperados
- Visibilidad en tiempo real
- Deteccion temprana de problemas
- Metricas de performance historicas
- Alertas automaticas

### Estimacion
6-8 horas

---

## 3. Migracion de Modulos a Repository Pattern - MEDIA PRIORIDAD

### Modulos Pendientes
- Herrajes
- Obras
- Compras
- Pedidos
- Usuarios

### Estrategia
1. Crear repositorios especializados por modulo
2. Migrar logica de acceso a datos desde models
3. Actualizar controllers para usar servicios
4. Validar con tests existentes

### Estimacion
2-3 horas por modulo

---

## 4. Aumento de Cobertura de Tests - MEDIA PRIORIDAD

### Objetivo
Aumentar cobertura de tests del 50% al 60%.

### Areas a Mejorar
- Edge cases en servicios
- Tests de integracion para repositorios
- Tests de seguridad
- Tests de performance

### Estimacion
4-6 horas

---

## 5. Feature Flags - BAJA PRIORIDAD

### Objetivo
Implementar sistema de feature flags para deployments mas seguros.

### Componentes
- Sistema de configuracion de features
- Integracion con servicios
- Dashboard de administracion
- Integracion con CI/CD

### Estimacion
6-8 horas

---

## 6. API Documentation - BAJA PRIORIDAD

### Objetivo
Documentacion automatica de APIs con Swagger/OpenAPI.

### Componentes
- Decoradores para documentacion
- Generacion automatica de especificaciones
- UI interactiva de documentacion
- Ejemplos de uso

### Estimacion
4-6 horas

---

## Plantilla de Submodulo

```python
"""
<Nombre>Manager - Gestor especializado para <funcionalidad>

Responsabilidades:
- <lista de responsabilidades>
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class <Nombre>Manager:
    """Gestor de <funcionalidad>."""

    def __init__(self, db_connection=None):
        """Inicializa el gestor."""
        self.db_connection = db_connection

    def metodo_ejemplo(self, param1: str, param2: int) -> Dict[str, Any]:
        """
        Descripcion breve del metodo.

        Args:
            param1: Descripcion
            param2: Descripcion

        Returns:
            Diccionario con resultado
        """
        if not self.db_connection:
            return {'success': False, 'error': 'Sin conexion a BD'}

        try:
            # Logica aqui
            pass
        except Exception as e:
            logger.error(f"Error: {e}")
            return {'success': False, 'error': str(e)}
```

---

## Priorizacion Resumida

| Mejora | Prioridad | Impacto | Esfuerzo | ROI |
|--------|-----------|---------|----------|-----|
| Refactor UsuariosModel | Alta | Alto | Medio | Alto |
| Refactor ObrasModel | Alta | Medio | Medio | Alto |
| Monitoreo Prometheus | Media | Alto | Medio | Alto |
| Migracion Repository | Media | Alto | Alto | Medio |
| Aumento cobertura tests | Media | Medio | Bajo | Medio |
| Feature Flags | Baja | Medio | Medio | Medio |
| API Documentation | Baja | Medio | Bajo | Alto |

---

## Documentacion Relacionada

- [ESTADO_PROYECTO.md](ESTADO_PROYECTO.md) - Estado actual del proyecto
- [CONFIGURACIONES.md](CONFIGURACIONES.md) - Configuraciones del proyecto
- [REPOSITORY_SERVICE_PATTERN.md](REPOSITORY_SERVICE_PATTERN.md) - Arquitectura base

---

**Fecha de actualizacion:** 2025-02-10
**Proxima revision:** Completar refactorizacion de God Objects
