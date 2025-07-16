# Estándares de Seguridad Crítica para Rexus.app

## 1. Variables de entorno y credenciales
- **Nunca** se deben incluir credenciales, contraseñas, usuarios, servidores ni claves sensibles en el código fuente.
- Todas las variables críticas deben ser cargadas exclusivamente desde un archivo `.env` o el entorno del sistema.
- Si falta alguna variable crítica, la app debe abortar y mostrar un error claro.
- El archivo `.env` **no** debe subirse a ningún repositorio público.

## 2. Configuración por defecto prohibida
- No se permite ningún valor por defecto para credenciales, usuarios, contraseñas, servidores, ni claves de seguridad en el código.
- Los modelos de configuración deben dejar los campos sensibles vacíos o con advertencia.

## 3. Herramientas de análisis estático
- Bandit, Pylance y otras herramientas de análisis **no deben inspeccionar** los archivos de tests ni los scripts de pruebas temporales.
- Se debe excluir la carpeta `tests/` y cualquier script de verificación temporal en la configuración de Bandit y Pylance.

### Ejemplo de exclusión para Bandit (`.bandit`):
```
[bandit]
exclude: tests/*,scripts/verificacion/*
```

### Ejemplo de exclusión para Pylance (`pyrightconfig.json`):
```
{
  "exclude": ["tests", "scripts/verificacion"]
}
```

## 4. Alta prioridad
- El cumplimiento de estos estándares es **obligatorio** y de máxima prioridad para el equipo de desarrollo.
- Cualquier excepción debe ser documentada y aprobada por el responsable de seguridad.

---

**Última actualización:** 2025-07-16
