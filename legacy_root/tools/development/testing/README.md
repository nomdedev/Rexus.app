# Testing Scripts

Scripts para ejecución y generación de reportes de tests.

**📍 IMPORTANTE:** Todos los reportes se guardan en `tests/reports/`

## Scripts disponibles:

- `generar_reporte_cobertura.py` - Genera reportes de cobertura de código
- `generar_reporte_ejemplo.py` - Ejemplo completo de generación de reportes
- `metricas_rapidas.py` - Métricas rápidas de tests
- `verificacion_completa.py` - Verificación completa del proyecto
- `verificar_seguridad_completa.py` - Verificación de seguridad

## Uso:

```bash
# Desde la raíz del proyecto
python scripts/testing/[script_name].py

# Ejemplo: Generar reporte completo
python scripts/testing/generar_reporte_ejemplo.py
```

## Estructura de Reportes:

```
tests/reports/
├── coverage_html/          # Reportes HTML de cobertura
├── coverage.json          # Datos de cobertura JSON
├── junit.xml              # Resultados JUnit
├── security_junit.xml     # Tests de seguridad
├── reporte_resumen.json   # Resumen de ejecución
└── README.md              # Documentación de reportes
```

---
*Los reportes se organizan automáticamente en tests/reports/ para mantener orden*
