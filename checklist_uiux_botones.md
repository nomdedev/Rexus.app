# Checklist de pendientes de UI/UX y botones en módulos

- [ ] Revisar que todos los botones que deban ser accedidos fuera del método donde se crean estén definidos como atributos de clase (self.btn_xxx) y no como variables locales.
- [ ] En el módulo de logística (view.py):
    - [ ] btn_nuevo_servicio: convertir a atributo si se necesita fuera del método.
    - [ ] btn_editar_servicio: convertir a atributo si se necesita fuera del método.
    - [ ] btn_detalle: convertir a atributo si se necesita fuera del método.
    - [ ] btn_cerrar: convertir a atributo si se necesita fuera del método.
    - [ ] btn_buscar: revisar contexto, convertir a atributo si se accede fuera del método.
- [ ] Repetir revisión en otros módulos críticos (inventario, compras, obras, etc.).
- [ ] Eliminar botones y controles que no se usan en ningún método ni controlador.
- [ ] Mejorar la gestión de destrucción de vistas para evitar errores de objetos eliminados.
- [ ] Documentar buenas prácticas para la creación y uso de botones en la UI.
