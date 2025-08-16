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
