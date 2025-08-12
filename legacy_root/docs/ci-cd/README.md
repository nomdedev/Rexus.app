# 🚀 Guía de CI/CD - Stock.app

## 📋 Resumen

Esta guía describe la configuración y uso del sistema de integración continua y entrega continua (CI/CD) para el proyecto stock.app.

## 🏗️ Configuración Automática

El proyecto incluye configuración automática para:

- **GitHub Actions**: Workflows para testing, análisis de calidad y seguridad
- **Pre-commit hooks**: Verificaciones automáticas antes de cada commit
- **Docker**: Containerización para entornos consistentes
- **VS Code**: Configuración optimizada para desarrollo

## 🧪 Pipelines de Testing

### Tests Críticos
```bash
# Ejecutar tests esenciales
python -m pytest tests/utils/ tests/test_schema_consistency.py -v

# Con make
make test
```

### Edge Cases
```bash
# Ejecutar tests de casos límite
python -m pytest tests/inventario/test_inventario_edge_cases.py -v

# Con make
make test-edge
```

### Cobertura Completa
```bash
# Generar reporte de cobertura
python -m pytest tests/ --cov=modules --cov=core --cov=utils --cov-report=html

# Con make
make coverage
```

## 🔒 Análisis de Seguridad

### Verificación SQL
```bash
python scripts/verificacion/analizar_seguridad_sql_codigo.py
```

### Escaneo de Vulnerabilidades
```bash
python scripts/verificacion/escanear_vulnerabilidades.py
```

## 📊 Métricas y Análisis

### Métricas Rápidas
```bash
python scripts/verificacion/metricas_rapidas.py
```

### Análisis de Módulos
```bash
python scripts/verificacion/analizador_modulos.py
```

## 🐳 Docker

### Construcción
```bash
docker build -t stock-app .
```

### Ejecución de Tests
```bash
docker-compose run test-runner
```

### Verificación de Calidad
```bash
docker-compose run code-quality
```

## 📋 Comandos Make Disponibles

- `make test` - Tests críticos
- `make test-all` - Todos los tests
- `make coverage` - Reporte de cobertura
- `make security` - Análisis de seguridad
- `make format` - Formatear código
- `make lint` - Análisis estático
- `make ci` - Pipeline completo de CI
- `make help` - Ver todos los comandos

## 🔄 Flujo de Desarrollo

1. **Desarrollo local**:
   ```bash
   make dev-check  # Verificación rápida
   ```

2. **Antes de commit**:
   ```bash
   pre-commit run --all-files
   ```

3. **Antes de merge**:
   ```bash
   make ci  # Pipeline completo
   ```

## ⚙️ Configuración de Entorno

### Configurar pre-commit
```bash
pip install pre-commit
pre-commit install
```

### Configurar entorno de desarrollo
```bash
make setup-dev
```

## 📈 Métricas Actuales

- **Total de tests**: 560
- **Cobertura de módulos**: 100%
- **Ratio test/código**: 1.72
- **Edge cases**: 29
- **Tests de integración**: 35

## 🎯 Próximos Pasos

1. Configurar webhooks para notificaciones
2. Implementar deployment automático
3. Agregar más tests de performance
4. Configurar monitoring en producción

---
*Generado automáticamente el 2025-06-25 21:53:36*
