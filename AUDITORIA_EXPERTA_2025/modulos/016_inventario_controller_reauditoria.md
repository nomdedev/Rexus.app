016 - Re-auditoría profunda: `inventario/controller.py`

Resumen rápido
- Archivo auditado: `rexus/modules/inventario/controller.py`.
- Objetivo: verificación de seguridad, manejo de errores, patrones de acceso a DB y conectividad vista-controlador.

Hallazgos clave
- Uso directo de `cursor = self.model.db_connection.cursor()` y `cursor.execute(query)` en `_cargar_datos_inventario_simple`.
  - Riesgo: apertura de cursores sin context manager ni cierre explícito; podría producir fugas de recursos.
  - Observación: la consulta es estática (no concatenación de inputs dinámicos) — riesgo SQL injection bajo en este punto, pero otras rutas reciben entradas de usuario.
- Sanitización: `SecurityUtils.sanitize_sql_input` se usa antes de pasar términos al modelo en `buscar_productos`.
  - Recomendación: asegurar que el modelo usa consultas parametrizadas; preferir pasar parámetros en vez de construir SQL con strings sanitizados.
- Amplio uso de `except Exception` como manejo por defecto.
  - Riesgo: enmascara errores, dificulta diagnósticos y puede ocultar errores lógicos.
  - Recomendación: capturar excepciones específicas y registrar con stacktrace. Re-lanzar o propagar cuando sea crítico.
- Uso de `print` para logging y mensajes de depuración.
  - Recomendación: usar el logger central (`rexus.logger` o `logging`) con niveles (INFO/WARN/ERROR).
- Conexión vista-controlador: `conectar_senales` detecta múltiples métodos en vista y usa fallback razonables.
  - Recomendación: documentar la API esperada de la vista (interfaz) y validar con asserts al inicializar.
- Paginación: implementación defensiva y soporte para distintos métodos del modelo; positivo.

Severidad (prioridad)
- Alto: recursos DB sin context manager (cursores no cerrados). Revisar para evitar leaks.
- Medio: manejo genérico de excepciones y uso de prints en lugar de logger.
- Bajo: dependencia en `SecurityUtils.sanitize_sql_input`; preferir consultas parametrizadas.

Recomendaciones concretas (acciones)
1. Reemplazar: `cursor = conn.cursor()` / `cursor.execute(query)` por `with conn.cursor() as cursor:` y cerrar/commit según el adaptador.
2. Asegurar que `model.*` usa parametrización (placeholders) para cualquier entrada de usuario; añadir tests que inyecten caracteres especiales.
3. Reemplazar `print` por `logger = logging.getLogger(__name__)` y llamadas `logger.debug/info/warning/error`.
4. Cambiar `except Exception` por excepciones concretas (DatabaseError, ValueError, etc.) y registrar stacktrace usando `logger.exception`.
5. Añadir un test unitario que ejecute `cargar_inventario_paginado` con `model` simulado (mock) para verificar comportamientos de paginación y fallback.

Notas adicionales
- La query usa `SELECT TOP 1000` (SQL Server). Verificar compatibilidad de DB si se planea soporte multi-DB.
- Buen diseño: múltiples fallbacks para distintas versiones del modelo y vista.

Estado: listo (archivo de re-auditoría creado).
