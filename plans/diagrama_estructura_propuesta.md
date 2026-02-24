# Diagrama Visual de la Estructura Propuesta para Rexus.app

## Estructura General del Proyecto

```mermaid
graph TD
    A[Rexus.app] --> B[rexus/]
    A --> C[tests/]
    A --> D[scripts/]
    A --> E[tools/]
    A --> F[temp/]
    A --> G[docs/]
    A --> H[config/]
    A --> I[sql/]
    A --> J[resources/]
    A --> K[logs/]
    A --> L[backups/]
    A --> M[cache/]
    A --> N[monitoring/]
    A --> O[reports/]
    A --> P[docker/]
    A --> Q[examples/]
    A --> R[Archivos de configuración]
    
    R --> R1[.env]
    R --> R2[.gitignore]
    R --> R3[main.py]
    R --> R4[pyproject.toml]
    R --> R5[requirements.txt]
    R --> R6[requirements-dev.txt]
    R --> R7[setup.cfg]
```

## Detalle del Módulo Principal (rexus/)

```mermaid
graph TD
    B[rexus/] --> B1[__init__.py]
    B --> B2[bootstrap.py]
    B --> B3[main/]
    B --> B4[api/]
    B --> B5[core/]
    B --> B6[models/]
    B --> B7[modules/]
    B --> B8[repositories/]
    B --> B9[security/]
    B --> B10[services/]
    B --> B11[ui/]
    B --> B12[utils/]
    
    B7 --> B71[01_inventario/]
    B7 --> B72[02_obras/]
    B7 --> B73[03_herrajes/]
    B7 --> B74[04_compras/]
    B7 --> B75[05_logistica/]
    B7 --> B76[06_pedidos/]
    B7 --> B77[07_vidrios/]
    B7 --> B78[08_administracion/]
    B7 --> B79[09_mantenimiento/]
    B7 --> B710[10_auditoria/]
    B7 --> B711[11_usuarios/]
    B7 --> B712[12_configuracion/]
    B7 --> B713[13_notificaciones/]
    
    B78 --> B781[contabilidad/]
    B78 --> B782[recursos_humanos/]
    
    B11 --> B111[components/]
```

## Detalle de Tests

```mermaid
graph TD
    C[tests/] --> C1[__init__.py]
    C --> C2[conftest.py]
    C --> C3[unit/]
    C --> C4[integration/]
    C --> C5[e2e/]
    C --> C6[security/]
    C --> C7[ui/]
    C --> C8[performance/]
    C --> C9[utils/]
    C --> C10[fixtures/]
    C --> C11[reports/]
    
    C3 --> C31[inventario/]
    C3 --> C32[obras/]
    C3 --> C33[herrajes/]
    C3 --> C34[compras/]
    C3 --> C35[logistica/]
    C3 --> C36[pedidos/]
    C3 --> C37[vidrios/]
    C3 --> C38[administracion/]
    C3 --> C39[mantenimiento/]
    C3 --> C310[auditoria/]
    C3 --> C311[usuarios/]
    C3 --> C312[configuracion/]
    C3 --> C313[notificaciones/]
    C3 --> C314[models/]
    C3 --> C315[repositories/]
    C3 --> C316[security/]
    C3 --> C317[services/]
    C3 --> C318[ui/]
    C3 --> C319[utils/]
```

## Detalle de Scripts

```mermaid
graph TD
    D[scripts/] --> D1[__init__.py]
    D --> D2[development/]
    D --> D3[testing/]
    D --> D4[maintenance/]
    D --> D5[deployment/]
    D --> D6[migration/]
    D --> D7[tools/]
    
    D2 --> D21[dev.py]
    D2 --> D22[start-dev.sh]
    D2 --> D23[validate_env.py]
    
    D3 --> D31[run_tests.py]
    D3 --> D32[generate_coverage.py]
    D3 --> D33[test_runner.py]
    
    D4 --> D41[cleanup.py]
    D4 --> D42[backup.py]
    D4 --> D43[database_maintenance.py]
    
    D5 --> D51[deploy.py]
    D5 --> D52[rollback.py]
    D5 --> D53[environment_setup.py]
    
    D6 --> D61[migrate_secrets.py]
    D6 --> D62[database_migration.py]
    
    D7 --> D71[fix_code_quality.py]
    D7 --> D72[critical_syntax_fixer.py]
```

## Detalle de Herramientas

```mermaid
graph TD
    E[tools/] --> E1[__init__.py]
    E --> E2[development/]
    E --> E3[security/]
    E --> E4[quality/]
    E --> E5[testing/]
    E --> E6[docker/]
    
    E2 --> E21[Makefile]
    E2 --> E22[.pre-commit-config.yaml]
    E2 --> E23[.flake8]
    E2 --> E24[.pylintrc]
    E2 --> E25[.mypy.ini]
    E2 --> E26[pyrightconfig.json]
    E2 --> E27[pytest.ini]
    
    E3 --> E31[.bandit]
    E3 --> E32[bandit_results.json]
    E3 --> E33[security_validator.py]
    
    E4 --> E41[sonar-project.properties]
    E4 --> E42[check_table_schema.py]
    
    E5 --> E51[test_modulos_integrales.py]
    
    E6 --> E61[.dockerignore]
    E6 --> E62[docker-compose.dev.yml]
    E6 --> E63[docker-compose.monitoring.yml]
```

## Detalle de Archivos Temporales

```mermaid
graph TD
    F[temp/] --> F1[development/]
    F --> F2[cache/]
    F --> F3[logs/]
    F --> F4[reports/]
    F --> F5[.gitkeep]
    
    F1 --> F11[temp_line.txt]
    F1 --> F12[pytest_temp.ini]
    
    F2 --> F21[__init__.py]
    F2 --> F22[.gitkeep]
    
    F3 --> F31[__init__.py]
    F3 --> F32[.gitkeep]
    
    F4 --> F41[__init__.py]
    F4 --> F42[.gitkeep]
```

## Flujo de Migración de Archivos

```mermaid
flowchart LR
    A[Archivos en raíz] --> B{Categorizar}
    
    B --> C[Archivos de pruebas]
    B --> D[Scripts de mantenimiento]
    B --> E[Archivos temporales]
    B --> F[Configuraciones Docker]
    B --> G[Documentación]
    B --> H[Herramientas de desarrollo]
    
    C --> C1[tests/]
    D --> D1[scripts/maintenance/]
    E --> E1[temp/]
    F --> F1[docker/]
    G --> G1[docs/]
    H --> H1[tools/]
    
    style A fill:#ffcccc
    style C1 fill:#ccffcc
    style D1 fill:#ccffcc
    style E1 fill:#ccffcc
    style F1 fill:#ccffcc
    style G1 fill:#ccffcc
    style H1 fill:#ccffcc
```

## Proceso de Limpieza de Archivos Duplicados

```mermaid
flowchart TD
    A[Identificar duplicados] --> B[Analizar dependencias]
    B --> C{¿Es necesario?}
    
    C -->|Sí| D[Conservar y consolidar]
    C -->|No| E[Eliminar]
    
    D --> F[Verificar funcionalidad]
    E --> F
    
    F --> G{¿Funciona correctamente?}
    
    G -->|Sí| H[Commit cambios]
    G -->|No| I[Restaurar desde backup]
    
    I --> J[Revisar problema]
    J --> B
    
    style A fill:#ffcccc
    style E fill:#ffcccc
    style H fill:#ccffcc
```

## Comparación: Antes vs Después

```mermaid
graph LR
    subgraph Antes
        A1[Archivos dispersos en raíz]
        A2[Scripts desorganizados]
        A3[Archivos duplicados]
        A4[Backup antiguo completo]
    end
    
    subgraph Después
        B1[Archivos organizados por propósito]
        B2[Scripts categorizados]
        B3[Sin duplicaciones]
        B4[Solo archivos necesarios]
    end
    
    A1 -.->|mover a| B1
    A2 -.->|organizar en| B2
    A3 -.->|eliminar| B3
    A4 -.->|eliminar| B4
    
    style Antes fill:#ffcccc
    style Después fill:#ccffcc
```

## Resumen de Beneficios

```mermaid
mindmap
  root((Beneficios))
    Organización
      Archivos clasificados
      Estructura clara
      Fácil navegación
    Mantenimiento
      Menos confusión
      Actualizaciones simples
      Debugging eficiente
    Colaboración
      Onboarding rápido
      Trabajo en equipo
      Code reviews efectivas
    Escalabilidad
      Crecimiento ordenado
      Módulos independientes
      Integración sencilla
    Calidad
      Código limpio
      Sin redundancias
      Mejor rendimiento