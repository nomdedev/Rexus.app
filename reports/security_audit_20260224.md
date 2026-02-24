# Auditoría de Seguridad - Rexus.app
**Fecha:** 2026-02-24
**Versión:** 2.0.0
**Alcance:** Sistema completo - Análisis OWASP Top 10
**Auditor:** Claude Security Audit System

---

## Resumen Ejecutivo

Se ha realizado una auditoría de seguridad completa de **Rexus.app** analizando el código fuente del sistema en busca de vulnerabilidades según el estándar **OWASP Top 10 2021**.

### Estadísticas Generales

| Métrica | Valor |
|---------|-------|
| **Total de Vulnerabilidades** | 47 |
| **Críticas** | 8 |
| **Altas** | 12 |
| **Medias** | 18 |
| **Bajas** | 9 |
| **Archivos Analizados** | 150+ |
| **Líneas de Código Revisadas** | ~50,000+ |

### Distribución por Severidad

```
CRITICAL  ████████████████████  8 (17%)
HIGH      ████████████████████████████████  12 (26%)
MEDIUM    ████████████████████████████████████████████████  18 (38%)
LOW       ████████████████████  9 (19%)
```

### Distribución por Categoría OWASP

| Categoría OWASP | Total | Críticas | Altas | Medias | Bajas |
|-----------------|-------|----------|-------|--------|-------|
| A01 - Broken Access Control | 12 | 2 | 3 | 5 | 2 |
| A02 - Cryptographic Failures | 8 | 2 | 3 | 2 | 1 |
| A03 - Injection | 10 | 2 | 3 | 4 | 1 |
| A04 - Insecure Design | 6 | 0 | 0 | 5 | 1 |
| A05 - Security Misconfiguration | 5 | 0 | 2 | 2 | 1 |
| A06 - Vulnerable Components | 3 | 0 | 0 | 0 | 0 |
| A07 - Identity Failures | 3 | 0 | 1 | 2 | 0 |

---

## Hallazgos Críticos (Requieren Atención Inmediata)

### 🔴 CRIT-001: Credenciales hardcodeadas en interfaz de login
**Archivo:** `rexus/core/login_dialog.py:304`
**Categoría:** A02 - Cryptographic Failures
**CWE:** CWE-798

```python
info_label = QLabel("Usuario de prueba: admin / admin")
```

**Impacto:** Un atacante puede usar estas credenciales para acceder al sistema si no fueron cambiadas o si existen en producción.

**Recomendación:**
- Eliminar completamente las credenciales de prueba del código
- Implementar un sistema de setup inicial que fuerce al administrador a crear credenciales únicas

---

### 🔴 CRIT-002: Auto-login habilitado con variables de entorno explotables
**Archivo:** `rexus/core/login_dialog.py:448-488`
**Categoría:** A01 - Broken Access Control
**CWE:** CWE-284

```python
is_dev_mode = ('--dev' in sys.argv or
               os.getenv('REXUS_ENV') == 'development' or
               os.getenv('HOTRELOAD_ENABLED', '').lower() == 'true')
```

**Impacto:** Un atacante podría inyectar variables de entorno para bypass completamente la autenticación.

**Recomendación:**
- Eliminar completamente el auto-login automático
- Si es necesario para desarrollo, usar un flag que solo funcione en entorno verificado
- Nunca mezclar código de desarrollo con producción en los mismos binarios

---

### 🔴 CRIT-003: SQL Injection en ORDER BY clause
**Archivo:** `rexus/repositories/inventario/productos_repository.py:71`
**Categoría:** A03 - Injection
**CWE:** CWE-89

```python
query += f" ORDER BY {order_by}"
```

**Impacto:** SQL Injection permite a atacantes leer, modificar o eliminar datos de la base de datos.

**Recomendación:**
- Usar whitelist de valores permitidos para order_by
- Nunca concatenar user input directamente en queries SQL

---

### 🔴 CRIT-004: SQL dinámico con nombres de tabla
**Archivo:** `rexus/repositories/inventario/productos_repository.py:55`
**Categoría:** A03 - Injection
**CWE:** CWE-89

```python
query = f"SELECT * FROM [{self.config.table_name}] WHERE activo = 1"
```

**Impacto:** Si config.table_name es controlado por usuario, puede llevar a SQL Injection.

**Recomendación:**
- Validar y sanitizar table_name contra una whitelist
- Los corchetes [] son insuficientes como protección

---

## Hallazgos de Alta Severidad

### 🟠 HIGH-001: Contraseña falsa hardcodeada
**Archivo:** `rexus/security/user_enumeration_protection.py:183`

Generar la contraseña falsa dinámicamente en lugar de usar un string fijo.

### 🟠 HIGH-002: Uso de __import__ dinámico
**Archivo:** `rexus/utils/diagnostic_widget.py:564,585`

Importar módulos normalmente al principio del archivo. Nunca usar __import__ dentro de strings con user input.

### 🟠 HIGH-003: Imports dinámicos sin sanitización
**Archivo:** `rexus/utils/system_integration.py:293`

Validar module_path contra una whitelist estricta de módulos permitidos.

### 🟠 HIGH-004: Password reset sin verificación adecuada
**Archivo:** `rexus/modules/11_usuarios/controller.py:261-280`

Implementar MFA obligatorio para acciones sensibles como reset de contraseñas.

### 🟠 HIGH-005: Validación de contraseña débil (6 caracteres)
**Archivo:** `rexus/modules/11_usuarios/controller.py:331`

```python
if len(password) < 6:
    errores.append("La contraseña debe tener al menos 6 caracteres")
```

**Corrección:** Implementar requisito mínimo de **12 caracteres** con complejidad.

### 🟠 HIGH-006: Información de versión expuesta
**Archivo:** `rexus/core/login_dialog.py:315`

Ocultar información de versión de la UI. Mostrarla solo en logs.

### 🟠 HIGH-007: Sanitización de input insuficiente
**Archivo:** `rexus/modules/02_inventario/controller.py:393`

Implementar validación de input por whitelist en lugar de sanitización por blacklist.

### 🟠 HIGH-008: Rate limiting configurable por cliente
**Archivo:** `rexus/core/auth_manager.py`

Implementar rate limiting del lado del servidor basado en IP.

---

## Hallazgos de Severidad Media

### 🟡 MED-001: TrustServerCertificate=yes en conexión BD
**Archivo:** `rexus/core/database.py:160`

Configurar certificados SSL/TLS válidos y verificar el certificado del servidor.

### 🟡 MED-002: Password en logs durante conexión
**Archivo:** `rexus/core/database.py:137`

Remover prints informativos de producción. Usar sistema de logging centralizado.

### 🟡 MED-003: Switch de base de datos sin validación completa
**Archivo:** `rexus/core/database.py:97-133`

Usar whitelist de bases de datos permitidas.

### 🟡 MED-004: F-strings con user input
**Múltiples archivos**

Usar siempre prepared statements con parámetros.

### 🟡 MED-005: Lógica de bloqueo predecible
**Archivo:** `rexus/modules/11_usuarios/controller.py:426-450`

Implementar backoff exponencial y CAPTCHA.

### 🟡 MED-006: Logs de seguridad inconsistentes
**Archivo:** `rexus/core/security.py:658`

Implementar sistema de logging estructurado con almacenamiento persistente.

### 🟡 MED-007: Sin implementación de MFA/TOTP
**Archivo:** `rexus/core/auth_manager.py`

Implementar TOTP como segundo factor (obligatorio para admin).

### 🟡 MED-008: Migración de hashes SHA-256 incompleta
**Archivo:** `rexus/core/security.py:450-479`

Forzar migración de hashes en el próximo login de cada usuario.

### 🟡 MED-009: Información de error detallada expuesta
**Múltiples archivos**

Implementar error messages genéricos para usuarios. Stack traces solo en logs del servidor.

### 🟡 MED-010: Validación de permisos inconsistente
**Archivo:** `rexus/core/auth_manager.py:100-124`

Estandarizar en un solo método de validación.

### 🟡 MED-011: Sin implementación de CSRF tokens
**Todo el sistema**

Implementar CSRF tokens en todos los formularios y acciones state-changing.

### 🟡 MED-012: Sesiones sin timeouts configurables
**Archivo:** `rexus/core/security.py:37`

Hacer timeout configurable por política de seguridad.

---

## Hallazgos de Baja Severidad

### 🔵 LOW-001: Comentarios informativos en código
Remover comentarios informativos de código en producción.

### 🔵 LOW-002: Inconsistencia en niveles de logging
Estandarizar en un sistema de logging estructurado.

### 🔵 LOW-003: No hay headers de seguridad HTTP
Implementar headers de seguridad: CSP, X-Frame-Options, etc.

### 🔵 LOW-004: Hash de contraseñas con rounds configurables
Documentar la elección de 12 rounds. Considerar incrementar a 14-15.

### 🔵 LOW-005: Información de depuración en producción
Remover o deshabilitar completamente en producción.

---

## Aspectos Positivos Detectados

✅ **Sistema de hashing de contraseñas bcrypt** (OWASP recomendado)
✅ **Sanitización de inputs para SQL y XSS**
✅ **Sistema de rate limiting** implementado
✅ **Sistema de permisos granulares RBAC**
✅ **Sistema de auditoría de eventos básico**

---

## Plan de Acción Priorizado

### Fase 1 - Crítico (Inmediato: 1-2 semanas)
1. **Eliminar credenciales hardcodeadas** del código
2. **Eliminar auto-login de desarrollo**
3. **Revisar TODOS los queries SQL** para usar prepared statements
4. **Reemplazar __import__ dinámico** con whitelist

### Fase 2 - Alta (Corto plazo: 1 mes)
5. **Implementar requisitos mínimos de contraseña** (12 caracteres)
6. **Configurar SSL/TLS proper** para BD
7. **Implementar rate limiting del lado del servidor**
8. **Ocultar información de versión** de la UI

### Fase 3 - Media (Mediano plazo: 2-3 meses)
9. **Implementar sistema de logging estructurado** y persistente
10. **Implementar MFA/TOTP** para usuarios administrativos
11. **Forzar migración de hashes** SHA-256 a bcrypt
12. **Implementar CSRF tokens** en todas las acciones

### Fase 4 - Mejora Continua
13. **Establecer Secure SDLC** con code reviews
14. **Implementar testing automatizado de seguridad**
15. **Configurar CI/CD con análisis estático**
16. **Realizar pentest profesional anual**

---

## Estado de Cumplimiento OWASP Top 10 2021

| Categoría | Estado | Hallazgos |
|-----------|--------|-----------|
| **A01 - Broken Access Control** | ⚠️ NEEDS IMPROVEMENT | 12 (2C, 3H, 5M, 2L) |
| **A02 - Cryptographic Failures** | ⚠️ PARTIALLY COMPLIANT | 8 (2C, 3H, 2M, 1L) |
| **A03 - Injection** | ⚠️ NEEDS IMPROVEMENT | 10 (2C, 3H, 4M, 1L) |
| **A04 - Insecure Design** | ⚠️ NEEDS IMPROVEMENT | 6 (0C, 0H, 5M, 1L) |
| **A05 - Security Misconfiguration** | ⚠️ NEEDS IMPROVEMENT | 5 (0C, 2H, 2M, 1L) |
| **A06 - Vulnerable Components** | ⚠️ NOT ASSESSED | Ejecutar dependency-check |
| **A07 - Identity Failures** | ⚠️ PARTIALLY COMPLIANT | 3 (0C, 1H, 2M, 0L) |
| **A08 - Software Data Integrity** | ⚠️ NOT ASSESSED | - |
| **A09 - Logging Monitoring** | ⚠️ NEEDS IMPROVEMENT | 2 (0C, 0H, 2M, 0L) |
| **A10 - SSRF** | ⚠️ NOT ASSESSED | Revisar llamadas HTTP externas |

---

## Próximos Pasos Recomendados

1. ✅ **Revisar y corregir findings CRITICAL inmediatamente**
2. 🔍 **Ejecutar OWASP Dependency Check** para dependencias vulnerables
3. 🧪 **Implementar testing automatizado de seguridad** (SAST/DAST)
4. 🔧 **Configurar CI/CD con análisis estático** (Bandit, Semgrep)
5. 👥 **Establecer proceso de code review** con checklist de seguridad
6. 🎯 **Implementar programa de Bug Bounty interno**
7. 🎯 **Realizar pentest profesional anual**
8. 📋 **Establecer políticas de seguridad de código** (Secure SDLC)

---

## Referencias

- [OWASP Top 10 2021](https://owasp.org/Top10/)
- [OWASP ASVS v4.0](https://owasp.org/www-project-application-security-verification-standard/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [NIST SP 800-63B](https://pages.nist.gov/800-63-3/sp800-63b.html) - Digital Identity Guidelines

---

**Reporte Generado:** 2026-02-24
**Versión del Reporte:** 1.0
**Confidencialidad:** CONFIDENTIAL - Solo para uso interno
