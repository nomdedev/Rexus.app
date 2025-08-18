## Auditoría: rexus/modules/pedidos/controller.py

Resumen
- Archivo: `rexus/modules/pedidos/controller.py`
- Alcance: Gestión de pedidos (creación, validación, paginación y estados)

Hallazgos clave
- Buenas prácticas: validación detallada en `validar_datos_pedido`, manejo de paginación y separación de responsabilidades.
- Hay `TODO` y funciones no implementadas (actualizar/eliminar realmente). Esto indica deuda técnica activa.
- En `cargar_pagina` hay manejo de excepciones que llama `self.mostrar_error` con firma distinta — posible bug de API de mensaje.
- Uso de `model` asumido no nulo; defensas limitadas para modelos faltantes.

Riesgos y severidad
- Funcionalidad incompleta: medio — operaciones críticas (actualizar/eliminar) no implementadas.
- Robustez: medio — errores en llamadas a funciones de UI con firmas distintas.

Recomendaciones
1. Completar implementaciones TODO.
2. Unificar API de mensajería (mostrar_error, mostrar_info, etc.).
3. Añadir cheques defensivos para `model` y `view` antes de operar.
4. Escribir tests de integración para paginación y validación.

Estado: informe creado.

### Estado de migración y mejoras (2025-08-18)
- Migración de prints a logger: EN PROGRESO
- Consolidación de mensajes hardcodeados: EN PROGRESO
- Migración SQL: EN PROGRESO
- No se detectaron señales faltantes críticas, pero se recomienda revisar consistencia de API de mensajes.
- Pendiente completar TODOs y funciones no implementadas.

Recomendaciones adicionales:
- Unificar el sistema de mensajería usando `message_system` y logger centralizado.
- Completar migración SQL y eliminar queries hardcodeadas.
- Documentar contratos de métodos y señales para facilitar testing.
- Añadir tests unitarios para paginación, validación y flujos críticos.
