================================================================================
ANÁLISIS DE PROBLEMAS DE ATRIBUTOS None - REXUS.APP
================================================================================

RESUMEN GENERAL: 12 problemas encontrados

2. ACCESOS DIRECTOS A VIEW SIN VERIFICACIÓN (5 problemas)
------------------------------------------------------------
   rexus/modules\auditoria\controller.py:67
   -> self.view.cargar_registros_auditoría(registros)

   rexus/modules\auditoria\controller.py:128
   -> # FIXME: Specify concrete exception types instead of generic Exceptionself.view.mostrar_error(f"Error aplicando filtros: {e}")

   rexus/modules\auditoria\controller.py:188
   -> # FIXME: Specify concrete exception types instead of generic Exceptionself.view.mostrar_error(f"Error exportando datos: {e}")

   rexus/modules\auditoria\controller.py:308
   -> # FIXME: Specify concrete exception types instead of generic Exceptionself.view.mostrar_error(f"Error limpiando registros: {e}")

   rexus/modules\auditoria\controller.py:364
   -> self.view.actualizar_estadisticas(estadisticas)

3. HASATTR SIN VERIFICACIÓN DE None (7 problemas)
------------------------------------------------------------
   rexus/modules\administracion\contabilidad\controller.py:269 (view)
   -> if reporte and hasattr(self.view, 'mostrar_reporte'):

   rexus/modules\compras\controller.py:609 (view)
   -> if reporte and hasattr(self.view, 'mostrar_reporte'):

   rexus/modules\inventario\controller.py:478 (view)
   -> if not hasattr(self.view, 'tabla_materiales'):

   rexus/modules\inventario\controller.py:505 (view)
   -> if not hasattr(self.view, 'tabla_materiales'):

   rexus/modules\inventario\controller.py:532 (view)
   -> if not hasattr(self.view, 'tabla_materiales'):

   rexus/modules\inventario\controller.py:631 (view)
   -> if not hasattr(self.view, 'cargar_datos_materiales'):

   rexus/modules\inventario\controller.py:678 (view)
   -> if not hasattr(self.view, 'tabla_materiales'):

RECOMENDACIONES DE CORRECCIÓN
========================================

1. Para accesos directos a model:
   ANTES: self.model.metodo()
   DESPUÉS: if self.model and hasattr(self.model, 'metodo'):
              self.model.metodo()

2. Para accesos directos a view:
   ANTES: self.view.metodo()
   DESPUÉS: if self.view and hasattr(self.view, 'metodo'):
              self.view.metodo()

3. Para hasattr sin verificación de None:
   ANTES: if hasattr(self.model, 'metodo'):
   DESPUÉS: if self.model and hasattr(self.model, 'metodo'):
