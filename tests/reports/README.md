# Reportes de Tests

Esta carpeta contiene todos los reportes generados por los tests del proyecto.

## Archivos generados:

### Cobertura
- `coverage_html/index.html` - Reporte HTML de cobertura de código
- `coverage.json` - Datos de cobertura en formato JSON

### Results de Tests
- `junit.xml` - Resultados de tests en formato JUnit
- `security_junit.xml` - Resultados de tests de seguridad

### Reportes Resumen
- `reporte_resumen.json` - Resumen de la última ejecución

## Última actualización: 2025-06-25 22:54:18

## Uso:

```bash
# Generar reporte completo
python scripts/testing/generar_reporte_ejemplo.py

# Ver cobertura en navegador
open tests/reports/coverage_html/index.html
```
