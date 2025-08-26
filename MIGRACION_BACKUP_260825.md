# Módulos y utilidades migrados desde backup a estructura principal
# Fecha: 26/08/2025

## Archivos migrados de backup a estructura oficial

### logistica/components/
- panel_manager.py
- table_manager.py
- transport_manager.py
- __init__.py

### logistica/
- constants.py
- controller.py
- dialogo_servicios.py
- dialogo_transporte.py
- model.py
- view.py
- view_refactored.py
- __init__.py

## Observaciones
- Se migraron solo archivos que no estaban presentes en la estructura principal.
- Si existía un archivo con el mismo nombre, se priorizó el de la estructura principal.
- Se recomienda eliminar los archivos migrados del backup para evitar confusión.

---

Este documento debe actualizarse tras cada migración de módulos o utilidades desde backups.
