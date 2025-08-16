## Auditoría: rexus/modules/vidrios/controller.py

Resumen
- Archivo: `rexus/modules/vidrios/controller.py`
- Alcance: Lógica del módulo Vidrios (C/R/U/D, búsqueda, asignación a obras, pedidos)

Hallazgos clave
- Buen patrón MVC: señales (pyqtSignal) para eventos inter-módulo.
- Uso directo de `QMessageBox` en `mostrar_mensaje` y `mostrar_error` — inconsistencia frente a otros módulos que usan `message_system`.
- Mezcla de return types: algunos métodos retornan valores (`crear_vidrio` devuelve tupla en variantes) y otros no, lo que complica su uso programático.
- Decoradores de autorización (`@admin_required`, `@auth_required`) están presentes, pero dependen de la implementación del framework de seguridad; no hay control de excepciones detallado alrededor.
- Falta de validación/normalización de `datos_vidrio` antes de enviarlos al modelo.

Riesgos y severidad
- Seguridad: medio — uso de decoradores mitigante, pero sin validación de inputs.
- Robustez: medio — manejo de errores con mensajes al usuario, pero sin logging estructurado.
- API: bajo-medio — inconsistencia en firmas y tipos de retorno.

Recomendaciones
1. Normalizar retornos: métodos CRUD deberían tener contratos claros (ej.: boolean + mensaje o raise on error).
2. Centralizar mensajería: usar `rexus.utils.message_system` o un wrapper para tests y consistencia.
3. Añadir validación/sanitización de `datos_vidrio` antes del modelo.
4. Añadir logging estructurado en catch blocks.
5. Escribir tests unitarios para señales emitidas y comportamiento de error.

Estado: informe creado.
