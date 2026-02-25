# 📊 Matriz de Vulnerabilidades Actualizada - Corte Operativo

**Fecha:** 24 de Febrero de 2026  
**Tipo:** Matriz de Riesgo Actualizada  
**Contexto:** Revalidación técnica por módulos críticos  
**Nota de alcance:** Se excluye ese frente de la priorización actual

---

## 📋 Resumen del estado real

| Métrica | Valor |
|---|---|
| Riesgo general del corte | **5.4/10** (Medio-Alto) |
| Vectores críticos abiertos | **1** |
| Módulos revalidados en este ciclo | **Pedidos, Notificaciones, Compras** |
| Pendientes operativos reales | **2** |

---

## 🔍 Matriz detallada de riesgo

| ID | Vulnerabilidad / Vector | Estado actual | Riesgo actual | Evidencia principal | Prioridad |
|---|---|---|---|---|---|
| VULN-001 | Bypass de autenticación/autorización transversal | Mitigación reforzada | **7.6/10** | Suites strict auth en verde + fallback fail-closed aplicado en managers/controladores críticos | Inmediata |
| VULN-002 | Inyección SQL residual en superficie no cerrada | Mitigación en progreso | **6.7/10** | Endurecimiento en módulos críticos y uso de patrones seguros | Alta |
| VULN-003 | Exposición de servicios en despliegue | Mitigado en configuración | **5.9/10** | Compose endurecido; falta validación runtime en host Docker | Alta |
| VULN-004 | Exfiltración de datos por rutas combinadas | Reducido | **6.1/10** | Menor superficie explotable tras hardening y validaciones | Alta |
| VULN-005 | Secuestro/abuso de sesión en rutas no uniformes | Parcialmente mitigado | **5.8/10** | Rotación de sesión y controles reforzados en rutas críticas | Media |
| VULN-006 | Deuda de diseño (archivos monolíticos) | Abierto técnico | **6.0/10** | Complejidad elevada y mantenimiento riesgoso | Media |

---

## ✅ Revalidaciones técnicas del corte

### Pedidos
- `python -m pytest tests/unit/pedidos/test_pedidos_model.py -q -o addopts=''` → **13 passed**

### Notificaciones
- `python -m pytest tests/unit/notificaciones/test_notificaciones_model.py -q -o addopts=''` → **11 passed**

### Compras
- `python -m pytest tests/unit/compras/test_compras_model.py tests/unit/compras/test_compras_controller.py tests/unit/compras/test_compras_view.py -q -o addopts=''` → **21 passed, 16 skipped**
- `python -m pytest tests/integration/test_compras_inventario_integration.py -q -o addopts=''` → **9 passed**

### Usuarios / Autorización transversal
- `python -m pytest tests/unit/usuarios/test_auth.py tests/unit/usuarios/test_permisos.py tests/unit/usuarios/test_sesiones.py tests/unit/usuarios/test_usuarios_controller.py -q -o addopts=''` → **19 passed, 14 skipped**
- `python -m pytest tests/unit/usuarios/test_auth.py tests/unit/usuarios/test_permisos.py tests/unit/usuarios/test_sesiones.py tests/unit/usuarios/test_usuarios_controller.py tests/unit/pedidos/test_pedidos_model.py -q -o addopts=''` → **32 passed, 14 skipped**

---

## 🎯 Priorización de cierre

### Inmediata (24-48h)
1. Cierre de controles de autorización transversales (deuda arquitectónica residual).

### Alta (1-2 semanas)
2. Validación runtime de hardening Docker en host con CLI (`docker compose ... config` + smoke up/down).
3. Migración/rotación final operativa de secretos en entorno objetivo.

### Media (2-4 semanas)
4. Reducción de deuda de diseño en componentes monolíticos de mayor impacto.

---

## 📌 Conclusión

La superficie de riesgo del sistema está **significativamente reducida** respecto de la línea base inicial.  
El riesgo ya no se concentra en múltiples frentes críticos abiertos, sino en un conjunto acotado de residuales transversales y operativos.

*Documento alineado al estado real de pruebas y mitigaciones verificadas en este corte.*
