# 🔍 Auditoría de Seguridad Consolidada - Rexus.app

**Fecha:** 24 de Febrero de 2026  
**Versión:** 2.2.0  
**Estado:** Corte operativo en cierre  
**Riesgo General Vigente:** **5.4/10** (Medio-Alto)

---

## 📊 Resumen Ejecutivo

El sistema mantiene una reducción significativa de superficie de ataque respecto de la línea base inicial.  
El estado actual se concentra en residuales operativos y deuda transversal de autorización, no en múltiples frentes críticos abiertos.

### Estado consolidado del corte

| Métrica | Valor |
|---|---|
| Riesgo general del corte | **5.4/10** |
| Vectores críticos abiertos | **1** |
| Módulos revalidados en este ciclo | **Pedidos, Notificaciones, Compras, Usuarios (auth transversal)** |
| Pendientes operativos reales | **2** |

---

## ✅ Evidencia Técnica Verificada

### Revalidaciones por módulos
- `python -m pytest tests/unit/pedidos/test_pedidos_model.py -q -o addopts=''` → **13 passed**
- `python -m pytest tests/unit/notificaciones/test_notificaciones_model.py -q -o addopts=''` → **11 passed**
- `python -m pytest tests/unit/compras/test_compras_model.py tests/unit/compras/test_compras_controller.py tests/unit/compras/test_compras_view.py -q -o addopts=''` → **21 passed, 16 skipped**
- `python -m pytest tests/integration/test_compras_inventario_integration.py -q -o addopts=''` → **9 passed**

### Revalidación autorización transversal
- `python -m pytest tests/unit/usuarios/test_auth.py tests/unit/usuarios/test_permisos.py tests/unit/usuarios/test_sesiones.py tests/unit/usuarios/test_usuarios_controller.py -q -o addopts=''` → **19 passed, 14 skipped**
- `python -m pytest tests/unit/usuarios/test_auth.py tests/unit/usuarios/test_permisos.py tests/unit/usuarios/test_sesiones.py tests/unit/usuarios/test_usuarios_controller.py tests/unit/pedidos/test_pedidos_model.py -q -o addopts=''` → **32 passed, 14 skipped**

### Hardening aplicado en código
- Eliminación de fallback abierto en autenticación en submódulos críticos de usuarios y controlador de pedidos.
- Política **fail-closed** fuera de entorno de test (bypass solo explícito para pruebas).

### Validación estática de despliegue (sin Docker CLI)
- `docker-compose.dev.yml` y `docker-compose.monitoring.yml` mantienen exposición local (`127.0.0.1`) para puertos sensibles (`6379`, `1433`, `9090`, `3000`, `9121`).
- Redis en compose exige contraseña (`--requirepass ${REDIS_PASSWORD:?...}`).
- `docker/redis/redis.conf` conserva `bind 0.0.0.0` para contexto de desarrollo en contenedor; requiere verificación runtime antes de endurecerlo adicionalmente.

---

## ⚠️ Riesgo Residual Vigente

1. **Autorización transversal (deuda arquitectónica)**
   - Estado: mitigación reforzada, cierre aún parcial.
   - Riesgo actual de vector: **7.6/10**.

2. **Validación runtime de hardening Docker en host**
   - Estado: **pendiente por entorno**.
   - Bloqueo actual: Docker CLI no disponible en este host (`docker` no reconocido).

3. **Migración/rotación final operativa de secretos en entorno objetivo**
   - Estado: pendiente de ejecución final operativa.

---

## 🎯 Priorización de Cierre

### Inmediata (24-48h)
1. Cierre de controles de autorización transversales (deuda arquitectónica residual).

### Alta (1-2 semanas)
2. Validación runtime de hardening Docker en host con CLI (`docker compose ... config` + smoke up/down).
3. Migración/rotación final operativa de secretos en entorno objetivo.

### Media (2-4 semanas)
4. Reducción de deuda de diseño en componentes monolíticos de mayor impacto.

---

## 📚 Referencias del Corte

- `reports/MATRIZ_VULNERABILIDADES_ACTUALIZADA_20260224.md`
- `reports/VALIDACION_INFORME_VECTORES_ATAQUE_20260224.md`
- `reports/ANALISIS_VECTORES_ATAQUE_REXUS_20260224.md`

---

## 📌 Conclusión

El sistema no está en escenario de compromiso total inmediato según la evidencia del corte.  
El riesgo permanece en nivel medio-alto por residuales puntuales y operativos, con ruta clara de cierre.

**Próxima revisión recomendada:** al completar validación runtime Docker + rotación final de secretos.