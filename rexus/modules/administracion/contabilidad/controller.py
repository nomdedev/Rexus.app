"""
Controlador de Contabilidad

Maneja la lógica de control para:
- Libro contable
- Recibos y comprobantes
- Pagos por obra
- Materiales y compras
- Reportes financieros
"""

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox, QFileDialog
from datetime import datetime, date
import csv
import os


class ContabilidadController(QObject):
    
    # Señales para libro contable
    asiento_agregado = pyqtSignal(dict)
    asiento_actualizado = pyqtSignal(dict)
    asiento_eliminado = pyqtSignal(int)
    
    # Señales para recibos
    recibo_creado = pyqtSignal(dict)
    recibo_impreso = pyqtSignal(int)
    
    # Señales para pagos
    pago_obra_creado = pyqtSignal(dict)
    pago_material_creado = pyqtSignal(dict)
    
    # Señales para reportes
    reporte_generado = pyqtSignal(str)
    estadisticas_actualizadas = pyqtSignal(dict)
    
    def __init__(self, model=None, view=None, db_connection=None):
        super().__init__()
        self.model = model
        self.view = view
        self.db_connection = db_connection
        self.usuario_actual = "ADMIN"
        self.conectar_senales()

    def conectar_senales(self):
        """Conecta las señales de la vista con los métodos del controlador."""
        if self.view:
            # Señales de libro contable
            self.view.crear_asiento_signal.connect(self.crear_asiento_contable)
            self.view.actualizar_asiento_signal.connect(self.actualizar_asiento_contable)
            
            # Señales de recibos
            self.view.crear_recibo_signal.connect(self.crear_recibo)
            self.view.imprimir_recibo_signal.connect(self.imprimir_recibo)
            
            # Señales de pagos
            self.view.crear_pago_obra_signal.connect(self.crear_pago_obra)
            self.view.crear_pago_material_signal.connect(self.crear_pago_material)
            
            # Señales de reportes
            self.view.generar_reporte_signal.connect(self.generar_reporte)

    # MÉTODOS PARA LIBRO CONTABLE

    def cargar_asientos_contables(self, filtros=None):
        """Carga los asientos contables en la vista."""
        if not self.model:
            return
            
        try:
            fecha_desde = filtros.get('fecha_desde') if filtros else None
            fecha_hasta = filtros.get('fecha_hasta') if filtros else None
            tipo = filtros.get('tipo') if filtros else None
            
            asientos = self.model.obtener_asientos_contables(fecha_desde, fecha_hasta, tipo)
            
            if self.view:
                self.view.actualizar_tabla_asientos(asientos)
                
            # Cargar estadísticas
            self.cargar_estadisticas_financieras()
                
        except Exception as e:
            self.mostrar_error(f"Error cargando asientos: {e}")

    def buscar_asientos(self, filtros):
        """Busca asientos contables con filtros específicos."""
        self.cargar_asientos_contables(filtros)

    def crear_asiento_contable(self, datos_asiento):
        """Crea un nuevo asiento contable."""
        if not self.model:
            return
            
        try:
            # Validar datos del asiento
            if not self._validar_datos_asiento(datos_asiento):
                return
                
            # Agregar usuario actual
            datos_asiento['usuario_creacion'] = self.usuario_actual
            
            asiento_id = self.model.crear_asiento_contable(datos_asiento)
            if asiento_id:
                self.mostrar_mensaje("Asiento contable creado exitosamente")
                self.cargar_asientos_contables()
                self.asiento_agregado.emit(datos_asiento)
                self.cargar_estadisticas_financieras()
            else:
                self.mostrar_error("Error al crear asiento contable")
                
        except Exception as e:
            self.mostrar_error(f"Error creando asiento: {e}")

    def actualizar_asiento_contable(self, asiento_id, datos_asiento):
        """Actualiza un asiento contable existente."""
        if not self.model:
            return
            
        try:
            # Validar datos del asiento
            if not self._validar_datos_asiento(datos_asiento):
                return
                
            if self.model.actualizar_asiento_contable(asiento_id, datos_asiento):
                self.mostrar_mensaje("Asiento contable actualizado exitosamente")
                self.cargar_asientos_contables()
                self.asiento_actualizado.emit(datos_asiento)
                self.cargar_estadisticas_financieras()
            else:
                self.mostrar_error("Error al actualizar asiento contable")
                
        except Exception as e:
            self.mostrar_error(f"Error actualizando asiento: {e}")

    # MÉTODOS PARA RECIBOS

    def cargar_recibos(self, filtros=None):
        """Carga los recibos en la vista."""
        if not self.model:
            return
            
        try:
            fecha_desde = filtros.get('fecha_desde') if filtros else None
            fecha_hasta = filtros.get('fecha_hasta') if filtros else None
            tipo = filtros.get('tipo') if filtros else None
            
            recibos = self.model.obtener_recibos(fecha_desde, fecha_hasta, tipo)
            
            if self.view:
                self.view.actualizar_tabla_recibos(recibos)
                
        except Exception as e:
            self.mostrar_error(f"Error cargando recibos: {e}")

    def buscar_recibos(self, filtros):
        """Busca recibos con filtros específicos."""
        self.cargar_recibos(filtros)

    def crear_recibo(self, datos_recibo):
        """Crea un nuevo recibo."""
        if not self.model:
            return
            
        try:
            # Validar datos del recibo
            if not self._validar_datos_recibo(datos_recibo):
                return
                
            # Agregar usuario actual
            datos_recibo['usuario_creacion'] = self.usuario_actual
            
            recibo_id = self.model.crear_recibo(datos_recibo)
            if recibo_id:
                self.mostrar_mensaje("Recibo creado exitosamente")
                self.cargar_recibos()
                self.recibo_creado.emit(datos_recibo)
                self.cargar_estadisticas_financieras()
            else:
                self.mostrar_error("Error al crear recibo")
                
        except Exception as e:
            self.mostrar_error(f"Error creando recibo: {e}")

    def imprimir_recibo(self, recibo_id):
        """Marca un recibo como impreso y genera el archivo."""
        if not self.model:
            return
            
        try:
            if self.model.marcar_recibo_impreso(recibo_id):
                self.mostrar_mensaje("Recibo marcado como impreso")
                self.cargar_recibos()
                self.recibo_impreso.emit(recibo_id)
                
                # Generar archivo de recibo
                self._generar_archivo_recibo(recibo_id)
                
            else:
                self.mostrar_error("Error al marcar recibo como impreso")
                
        except Exception as e:
            self.mostrar_error(f"Error imprimiendo recibo: {e}")

    # MÉTODOS PARA PAGOS POR OBRA

    def cargar_pagos_obra(self, filtros=None):
        """Carga los pagos por obra en la vista."""
        if not self.model:
            return
            
        try:
            obra_id = filtros.get('obra_id') if filtros else None
            categoria = filtros.get('categoria') if filtros else None
            
            pagos = self.model.obtener_pagos_obra(obra_id, categoria)
            
            if self.view:
                self.view.actualizar_tabla_pagos_obra(pagos)
                
        except Exception as e:
            self.mostrar_error(f"Error cargando pagos por obra: {e}")

    def buscar_pagos_obra(self, filtros):
        """Busca pagos por obra con filtros específicos."""
        self.cargar_pagos_obra(filtros)

    def crear_pago_obra(self, datos_pago):
        """Crea un nuevo pago por obra."""
        if not self.model:
            return
            
        try:
            # Validar datos del pago
            if not self._validar_datos_pago_obra(datos_pago):
                return
                
            # Agregar usuario actual
            datos_pago['usuario_creacion'] = self.usuario_actual
            
            pago_id = self.model.crear_pago_obra(datos_pago)
            if pago_id:
                self.mostrar_mensaje("Pago por obra creado exitosamente")
                self.cargar_pagos_obra()
                self.pago_obra_creado.emit(datos_pago)
                self.cargar_estadisticas_financieras()
            else:
                self.mostrar_error("Error al crear pago por obra")
                
        except Exception as e:
            self.mostrar_error(f"Error creando pago por obra: {e}")

    # MÉTODOS PARA PAGOS DE MATERIALES

    def cargar_pagos_materiales(self, filtros=None):
        """Carga los pagos de materiales en la vista."""
        if not self.model:
            return
            
        try:
            proveedor = filtros.get('proveedor') if filtros else None
            estado = filtros.get('estado') if filtros else None
            
            pagos = self.model.obtener_pagos_materiales(proveedor, estado)
            
            if self.view:
                self.view.actualizar_tabla_pagos_materiales(pagos)
                
        except Exception as e:
            self.mostrar_error(f"Error cargando pagos de materiales: {e}")

    def buscar_pagos_materiales(self, filtros):
        """Busca pagos de materiales con filtros específicos."""
        self.cargar_pagos_materiales(filtros)

    def crear_pago_material(self, datos_pago):
        """Crea un nuevo pago de material."""
        if not self.model:
            return
            
        try:
            # Validar datos del pago
            if not self._validar_datos_pago_material(datos_pago):
                return
                
            # Agregar usuario actual
            datos_pago['usuario_creacion'] = self.usuario_actual
            
            pago_id = self.model.crear_pago_material(datos_pago)
            if pago_id:
                self.mostrar_mensaje("Pago de material creado exitosamente")
                self.cargar_pagos_materiales()
                self.pago_material_creado.emit(datos_pago)
                self.cargar_estadisticas_financieras()
            else:
                self.mostrar_error("Error al crear pago de material")
                
        except Exception as e:
            self.mostrar_error(f"Error creando pago de material: {e}")

    # MÉTODOS PARA REPORTES Y ESTADÍSTICAS

    def cargar_estadisticas_financieras(self):
        """Carga las estadísticas financieras en la vista."""
        if not self.model:
            return
            
        try:
            estadisticas = self.model.obtener_estadisticas_financieras()
            
            if self.view:
                self.view.actualizar_estadisticas_financieras(estadisticas)
                
            self.estadisticas_actualizadas.emit(estadisticas)
                
        except Exception as e:
            self.mostrar_error(f"Error cargando estadísticas: {e}")

    def generar_reporte(self, tipo_reporte, parametros=None):
        """Genera un reporte específico."""
        if not self.model:
            return
            
        try:
            if tipo_reporte == 'BALANCE_GENERAL':
                self._generar_reporte_balance(parametros)
            elif tipo_reporte == 'FLUJO_CAJA':
                self._generar_reporte_flujo_caja(parametros)
            elif tipo_reporte == 'LIBRO_CONTABLE':
                self._generar_reporte_libro_contable(parametros)
            elif tipo_reporte == 'RECIBOS':
                self._generar_reporte_recibos(parametros)
            elif tipo_reporte == 'PAGOS_OBRA':
                self._generar_reporte_pagos_obra(parametros)
            elif tipo_reporte == 'PAGOS_MATERIALES':
                self._generar_reporte_pagos_materiales(parametros)
            else:
                self.mostrar_error("Tipo de reporte no válido")
                
        except Exception as e:
            self.mostrar_error(f"Error generando reporte: {e}")

    def _generar_reporte_balance(self, parametros):
        """Genera reporte de balance general."""
        fecha_desde = parametros.get('fecha_desde') if parametros else None
        fecha_hasta = parametros.get('fecha_hasta') if parametros else None
        
        balance = self.model.obtener_balance_general(fecha_desde, fecha_hasta)
        
        if balance:
            nombre_archivo = f"balance_general_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            self._escribir_reporte_balance(balance, nombre_archivo)
            self.mostrar_mensaje(f"Reporte de balance generado: {nombre_archivo}")
            self.reporte_generado.emit(nombre_archivo)
        else:
            self.mostrar_error("No hay datos para generar el reporte de balance")

    def _generar_reporte_flujo_caja(self, parametros):
        """Genera reporte de flujo de caja."""
        fecha_desde = parametros.get('fecha_desde') if parametros else None
        fecha_hasta = parametros.get('fecha_hasta') if parametros else None
        
        flujo = self.model.obtener_flujo_caja(fecha_desde, fecha_hasta)
        
        if flujo:
            nombre_archivo = f"flujo_caja_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            self._escribir_reporte_flujo_caja(flujo, nombre_archivo)
            self.mostrar_mensaje(f"Reporte de flujo de caja generado: {nombre_archivo}")
            self.reporte_generado.emit(nombre_archivo)
        else:
            self.mostrar_error("No hay datos para generar el reporte de flujo de caja")

    def _generar_reporte_libro_contable(self, parametros):
        """Genera reporte del libro contable."""
        fecha_desde = parametros.get('fecha_desde') if parametros else None
        fecha_hasta = parametros.get('fecha_hasta') if parametros else None
        tipo = parametros.get('tipo') if parametros else None
        
        asientos = self.model.obtener_asientos_contables(fecha_desde, fecha_hasta, tipo)
        
        if asientos:
            nombre_archivo = f"libro_contable_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            self._escribir_reporte_csv(asientos, nombre_archivo)
            self.mostrar_mensaje(f"Reporte del libro contable generado: {nombre_archivo}")
            self.reporte_generado.emit(nombre_archivo)
        else:
            self.mostrar_error("No hay datos para generar el reporte del libro contable")

    def _generar_reporte_recibos(self, parametros):
        """Genera reporte de recibos."""
        fecha_desde = parametros.get('fecha_desde') if parametros else None
        fecha_hasta = parametros.get('fecha_hasta') if parametros else None
        tipo = parametros.get('tipo') if parametros else None
        
        recibos = self.model.obtener_recibos(fecha_desde, fecha_hasta, tipo)
        
        if recibos:
            nombre_archivo = f"recibos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            self._escribir_reporte_csv(recibos, nombre_archivo)
            self.mostrar_mensaje(f"Reporte de recibos generado: {nombre_archivo}")
            self.reporte_generado.emit(nombre_archivo)
        else:
            self.mostrar_error("No hay datos para generar el reporte de recibos")

    def _generar_reporte_pagos_obra(self, parametros):
        """Genera reporte de pagos por obra."""
        obra_id = parametros.get('obra_id') if parametros else None
        categoria = parametros.get('categoria') if parametros else None
        
        pagos = self.model.obtener_pagos_obra(obra_id, categoria)
        
        if pagos:
            nombre_archivo = f"pagos_obra_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            self._escribir_reporte_csv(pagos, nombre_archivo)
            self.mostrar_mensaje(f"Reporte de pagos por obra generado: {nombre_archivo}")
            self.reporte_generado.emit(nombre_archivo)
        else:
            self.mostrar_error("No hay datos para generar el reporte de pagos por obra")

    def _generar_reporte_pagos_materiales(self, parametros):
        """Genera reporte de pagos de materiales."""
        proveedor = parametros.get('proveedor') if parametros else None
        estado = parametros.get('estado') if parametros else None
        
        pagos = self.model.obtener_pagos_materiales(proveedor, estado)
        
        if pagos:
            nombre_archivo = f"pagos_materiales_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            self._escribir_reporte_csv(pagos, nombre_archivo)
            self.mostrar_mensaje(f"Reporte de pagos de materiales generado: {nombre_archivo}")
            self.reporte_generado.emit(nombre_archivo)
        else:
            self.mostrar_error("No hay datos para generar el reporte de pagos de materiales")

    # MÉTODOS AUXILIARES PRIVADOS

    def _validar_datos_asiento(self, datos):
        """Valida los datos de un asiento contable."""
        campos_requeridos = ['fecha_asiento', 'tipo_asiento', 'concepto']
        
        for campo in campos_requeridos:
            if not datos.get(campo):
                self.mostrar_error(f"El campo {campo} es requerido")
                return False
                
        # Validar que al menos debe o haber tenga valor
        debe = float(datos.get('debe', 0))
        haber = float(datos.get('haber', 0))
        
        if debe == 0 and haber == 0:
            self.mostrar_error("El asiento debe tener al menos un valor en debe o haber")
            return False
            
        return True

    def _validar_datos_recibo(self, datos):
        """Valida los datos de un recibo."""
        campos_requeridos = ['fecha_emision', 'tipo_recibo', 'concepto', 'beneficiario', 'monto']
        
        for campo in campos_requeridos:
            if not datos.get(campo):
                self.mostrar_error(f"El campo {campo} es requerido")
                return False
                
        # Validar monto
        try:
            monto = float(datos.get('monto', 0))
            if monto <= 0:
                self.mostrar_error("El monto debe ser mayor a 0")
                return False
        except ValueError:
            self.mostrar_error("El monto debe ser un número válido")
            return False
            
        return True

    def _validar_datos_pago_obra(self, datos):
        """Valida los datos de un pago por obra."""
        campos_requeridos = ['obra_id', 'concepto', 'categoria', 'monto', 'fecha_pago', 'metodo_pago']
        
        for campo in campos_requeridos:
            if not datos.get(campo):
                self.mostrar_error(f"El campo {campo} es requerido")
                return False
                
        # Validar monto
        try:
            monto = float(datos.get('monto', 0))
            if monto <= 0:
                self.mostrar_error("El monto debe ser mayor a 0")
                return False
        except ValueError:
            self.mostrar_error("El monto debe ser un número válido")
            return False
            
        return True

    def _validar_datos_pago_material(self, datos):
        """Valida los datos de un pago de material."""
        campos_requeridos = ['producto', 'proveedor', 'cantidad', 'precio_unitario', 'fecha_compra']
        
        for campo in campos_requeridos:
            if not datos.get(campo):
                self.mostrar_error(f"El campo {campo} es requerido")
                return False
                
        # Validar valores numéricos
        try:
            cantidad = float(datos.get('cantidad', 0))
            precio_unitario = float(datos.get('precio_unitario', 0))
            
            if cantidad <= 0:
                self.mostrar_error("La cantidad debe ser mayor a 0")
                return False
                
            if precio_unitario <= 0:
                self.mostrar_error("El precio unitario debe ser mayor a 0")
                return False
        except ValueError:
            self.mostrar_error("La cantidad y precio unitario deben ser números válidos")
            return False
            
        return True

    def _generar_archivo_recibo(self, recibo_id):
        """Genera el archivo físico del recibo."""
        try:
            # Obtener datos del recibo
            recibos = self.model.obtener_recibos()
            recibo = next((r for r in recibos if r['id'] == recibo_id), None)
            
            if not recibo:
                return
                
            # Crear directorio para recibos si no existe
            directorio_recibos = os.path.join(os.getcwd(), "recibos")
            os.makedirs(directorio_recibos, exist_ok=True)
            
            # Generar archivo
            nombre_archivo = f"recibo_{recibo['numero_recibo']}.txt"
            ruta_archivo = os.path.join(directorio_recibos, nombre_archivo)
            
            with open(ruta_archivo, 'w', encoding='utf-8') as file:
                file.write("=" * 50 + "\n")
                file.write("RECIBO DE PAGO\n")
                file.write("=" * 50 + "\n\n")
                file.write(f"Número: {recibo['numero_recibo']}\n")
                file.write(f"Fecha: {recibo['fecha_emision']}\n")
                file.write(f"Tipo: {recibo['tipo_recibo']}\n")
                file.write(f"Beneficiario: {recibo['beneficiario']}\n")
                file.write(f"Concepto: {recibo['concepto']}\n")
                file.write(f"Monto: {recibo['moneda']} {recibo['monto']:,.2f}\n")
                file.write("=" * 50 + "\n")
                
        except Exception as e:
            print(f"Error generando archivo de recibo: {e}")

    def _escribir_reporte_balance(self, balance, nombre_archivo):
        """Escribe el reporte de balance en un archivo."""
        with open(nombre_archivo, 'w', encoding='utf-8') as file:
            file.write("BALANCE GENERAL\n")
            file.write("=" * 50 + "\n\n")
            
            for tipo, datos in balance.items():
                file.write(f"{tipo}:\n")
                file.write(f"  Debe: ${datos['debe']:,.2f}\n")
                file.write(f"  Haber: ${datos['haber']:,.2f}\n")
                file.write(f"  Saldo: ${datos['saldo']:,.2f}\n\n")

    def _escribir_reporte_flujo_caja(self, flujo, nombre_archivo):
        """Escribe el reporte de flujo de caja en un archivo."""
        with open(nombre_archivo, 'w', encoding='utf-8') as file:
            file.write("FLUJO DE CAJA\n")
            file.write("=" * 50 + "\n\n")
            
            if 'ingresos' in flujo:
                file.write("INGRESOS:\n")
                for tipo, monto in flujo['ingresos'].items():
                    file.write(f"  {tipo}: ${monto:,.2f}\n")
                file.write("\n")
                
            if 'egresos' in flujo:
                file.write("EGRESOS:\n")
                for categoria, monto in flujo['egresos'].items():
                    file.write(f"  {categoria}: ${monto:,.2f}\n")
                file.write("\n")

    def _escribir_reporte_csv(self, datos, nombre_archivo):
        """Escribe un reporte en formato CSV."""
        if not datos:
            return
            
        with open(nombre_archivo, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=datos[0].keys())
            writer.writeheader()
            writer.writerows(datos)

    def mostrar_mensaje(self, mensaje):
        """Muestra un mensaje informativo."""
        if self.view:
            QMessageBox.information(self.view, "Contabilidad", mensaje)

    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error."""
        if self.view:
            QMessageBox.critical(self.view, "Error - Contabilidad", mensaje)
        print(f"[ERROR CONTABILIDAD] {mensaje}")

    def actualizar_datos(self):
        """Actualiza todos los datos de la interfaz."""
        self.cargar_asientos_contables()
        self.cargar_recibos()
        self.cargar_pagos_obra()
        self.cargar_pagos_materiales()
        self.cargar_estadisticas_financieras()