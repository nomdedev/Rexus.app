# Icon Naming Policy (Política de Nombres de Íconos)

## Reglas para nombres de íconos en la app

- Todos los nombres de íconos deben estar en inglés, en minúsculas y usar guiones bajos solo si es necesario (ej: add-user.svg, save.svg, close.svg).
- No se permiten nombres en español ni duplicados.
- Si un ícono no existe, se debe usar el placeholder universal (placeholder.svg) hasta que se cree el definitivo.
- Los nombres deben ser descriptivos y cortos, relacionados con la acción o entidad (ej: search_icon.svg, pdf.svg, users.svg, help.svg).
- Cada vez que se agregue un nuevo ícono, debe documentarse en este archivo y en el checklist visual.
- Si se detecta un nombre incorrecto, debe corregirse en el código y en la carpeta de íconos.

## Ejemplos válidos
- add-material.svg
- save.svg
- close.svg
- help.svg
- users.svg
- pdf.svg

## Ejemplo de uso de placeholder
Si un botón requiere un ícono que aún no existe, usar:

```python
from utils.icon_loader import get_icon
btn.setIcon(get_icon("placeholder"))
```

---
Última actualización: 2025-06-24
