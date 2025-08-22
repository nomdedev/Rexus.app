# -*- coding: utf-8 -*-
"""
Dashboard Controller - Controlador central del dashboard
Coordina datos entre módulos y widgets del dashboard
"""

from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from PyQt6.QtWidgets import QApplication

from ...core.base_controller import BaseController
from ...modules.usuarios.controller import UsuariosController
from ...modules.inventario.controller import InventarioController
from ...modules.obras.controller import ObrasController
from ...modules.pedidos.controller import PedidosController
from ...modules.compras.controller import ComprasController
from ...modules.vidrios.controller import VidriosController
from ...modules.notificaciones.controller import NotificacionesController
from .main_dashboard import MainDashboard


class DashboardController(BaseController):
    """Controlador principal del dashboard."""
    
    # Señales
    datos_actualizados = pyqtSignal(dict)
    error_actualizacion = pyqtSignal(str)
    
    def __init__(self, db_manager, parent=None):
        super().__init__(db_manager, parent)
        
        self.dashboard_view = None
        self.module_controllers = {}
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.actualizar_todas_metricas)
        
        self.setup_module_controllers()
        self.setup_timer()
    
    def setup_module_controllers(self):
        """Inicializa los controladores de módulos."""
        try:
            self.module_controllers = {
                'usuarios': UsuariosController(self.db_manager),
                'inventario': InventarioController(self.db_manager),
                'obras': ObrasController(self.db_manager),
                'pedidos': PedidosController(self.db_manager),
                'compras': ComprasController(self.db_manager),
                'vidrios': VidriosController(self.db_manager),
                'notificaciones': NotificacionesController(self.db_manager)
            }
        except Exception as e:
            self.logger.error(f"Error inicializando controladores: {e}")
    
    def setup_timer(self):
        """Configura el timer de actualización automática."""
        self.update_timer.start(30000)  # 30 segundos
    
    def get_view(self):
        """Retorna la vista del dashboard."""
        if self.dashboard_view is None:
            self.dashboard_view = MainDashboard()
            self.conectar_senales()
        return self.dashboard_view
    
    def conectar_senales(self):
        """Conecta las señales del dashboard."""
        if self.dashboard_view:
            self.dashboard_view.modulo_solicitado.connect(self.abrir_modulo)
            self.dashboard_view.reporte_solicitado.connect(self.generar_reporte)
    
    def actualizar_todas_metricas(self):
        """Actualiza todas las métricas del dashboard."""
        try:
            # Actualizar KPIs principales
            self.actualizar_kpis()
            
            # Actualizar métricas del header
            self.actualizar_header_metrics()
            
            # Actualizar métricas de botones de módulos
            self.actualizar_metricas_modulos()
            
            # Actualizar gráficos
            self.actualizar_graficos()
            
            # Actualizar actividad reciente
            self.actualizar_actividad_reciente()
            
        except Exception as e:
            self.logger.error(f"Error actualizando métricas: {e}")
            self.error_actualizacion.emit(str(e))
    
    def actualizar_kpis(self):
        """Actualiza los KPIs principales."""
        if not self.dashboard_view:
            return
        
        try:
            # Usuarios
            total_usuarios = self.obtener_total_usuarios()
            self.dashboard_view.actualizar_kpi('usuarios', total_usuarios, 'stable')
            
            # Inventario
            total_productos = self.obtener_total_productos()
            productos_bajo_stock = self.obtener_productos_bajo_stock()
            tendencia_inv = 'warning' if productos_bajo_stock > 5 else 'stable'
            self.dashboard_view.actualizar_kpi('inventario', total_productos, tendencia_inv)
            
            # Obras
            obras_activas = self.obtener_obras_activas()
            self.dashboard_view.actualizar_kpi('obras', obras_activas, 'stable')
            
            # Pedidos
            pedidos_pendientes = self.obtener_pedidos_pendientes()
            self.dashboard_view.actualizar_kpi('pedidos', pedidos_pendientes, 'stable')
            
            # Métricas financieras
            ventas_mes = self.obtener_ventas_mes()
            compras_mes = self.obtener_compras_mes()
            margen = self.calcular_margen_ganancia(ventas_mes, compras_mes)
            alertas_sistema = self.obtener_alertas_sistema()
            
            self.dashboard_view.actualizar_kpi('ventas', f"${ventas_mes:,.0f}", 'up')
            self.dashboard_view.actualizar_kpi('compras', f"${compras_mes:,.0f}", 'stable')
            self.dashboard_view.actualizar_kpi('margen', f"{margen:.1f}%", 'up' if margen > 15 else 'down')
            self.dashboard_view.actualizar_kpi('alertas', alertas_sistema, 'warning' if alertas_sistema > 0 else 'stable')
            
        except Exception as e:
            self.logger.error(f"Error actualizando KPIs: {e}")
    
    def actualizar_header_metrics(self):
        """Actualiza las métricas del header."""
        if not self.dashboard_view:
            return
        
        try:
            # Usuarios online (simulado)
            usuarios_online = len([u for u in self.get_usuarios_activos() if u.get('activo', False)])
            self.dashboard_view.actualizar_header_metric('usuarios', usuarios_online)
            
            # Alertas
            alertas = self.obtener_alertas_sistema()
            self.dashboard_view.actualizar_header_metric('alertas', alertas)
            
            # Estado del sistema
            estado = "OK" if alertas < 5 else "ALERT"
            self.dashboard_view.actualizar_header_metric('sistema', estado)
            
        except Exception as e:
            self.logger.error(f"Error actualizando header: {e}")
    
    def actualizar_metricas_modulos(self):
        """Actualiza las métricas de los botones de módulos."""
        if not self.dashboard_view:
            return
        
        try:
            metricas = {
                'usuarios': self.obtener_total_usuarios(),
                'inventario': self.obtener_total_productos(),
                'obras': self.obtener_obras_activas(),
                'pedidos': self.obtener_pedidos_pendientes(),
                'compras': self.obtener_compras_pendientes(),
                'vidrios': self.obtener_total_vidrios(),
                'notificaciones': self.obtener_notificaciones_pendientes(),
                'configuracion': "OK"
            }
            
            for modulo, valor in metricas.items():
                self.dashboard_view.actualizar_metrica_modulo(modulo, valor)
                
        except Exception as e:
            self.logger.error(f"Error actualizando métricas de módulos: {e}")
    
    def actualizar_graficos(self):
        """Actualiza los datos de los gráficos."""
        if not self.dashboard_view:
            return
        
        try:
            # Gráfico de ventas (últimas 8 semanas)
            datos_ventas = self.obtener_datos_ventas_semanales()
            self.dashboard_view.actualizar_grafico('ventas', datos_ventas)
            
            # Gráfico de inventario
            datos_inventario = self.obtener_datos_inventario_categorias()
            self.dashboard_view.actualizar_grafico('inventario', datos_inventario)
            
            # Gráfico de obras
            datos_obras = self.obtener_datos_obras_estado()
            self.dashboard_view.actualizar_grafico('obras', datos_obras)
            
        except Exception as e:
            self.logger.error(f"Error actualizando gráficos: {e}")
    
    def actualizar_actividad_reciente(self):
        """Actualiza el feed de actividad reciente."""
        if not self.dashboard_view:
            return
        
        try:
            actividades = self.obtener_actividades_recientes()
            for actividad in actividades:
                self.dashboard_view.agregar_actividad(
                    actividad['icono'],
                    actividad['titulo'],
                    actividad['descripcion'],
                    actividad['timestamp']
                )
        except Exception as e:
            self.logger.error(f"Error actualizando actividad: {e}")
    
    # =================================================================
    # MÉTODOS DE OBTENCIÓN DE DATOS
    # =================================================================
    
    def obtener_total_usuarios(self):
        """Obtiene el total de usuarios registrados."""
        try:
            if 'usuarios' in self.module_controllers:
                usuarios = self.module_controllers['usuarios'].get_all_usuarios()
                return len(usuarios) if usuarios else 0
            return 0
        except:
            return 0
    
    def obtener_total_productos(self):
        """Obtiene el total de productos en inventario."""
        try:
            if 'inventario' in self.module_controllers:
                productos = self.module_controllers['inventario'].get_all_productos()
                return len(productos) if productos else 0
            return 0
        except:
            return 0
    
    def obtener_productos_bajo_stock(self):
        """Obtiene productos con stock bajo."""
        try:
            if 'inventario' in self.module_controllers:
                # Implementar lógica según modelo de inventario
                return 3  # Placeholder
            return 0
        except:
            return 0
    
    def obtener_obras_activas(self):
        """Obtiene obras en estado activo."""
        try:
            if 'obras' in self.module_controllers:
                obras = self.module_controllers['obras'].get_all_obras()
                return len([o for o in obras if o.get('estado') == 'Activa']) if obras else 0
            return 0
        except:
            return 0
    
    def obtener_pedidos_pendientes(self):
        """Obtiene pedidos en estado pendiente."""
        try:
            if 'pedidos' in self.module_controllers:
                pedidos = self.module_controllers['pedidos'].get_all_pedidos()
                return len([p for p in pedidos if p.get('estado') == 'Pendiente']) if pedidos else 0
            return 0
        except:
            return 0
    
    def obtener_compras_pendientes(self):
        """Obtiene compras pendientes."""
        try:
            if 'compras' in self.module_controllers:
                compras = self.module_controllers['compras'].get_all_compras()
                return len([c for c in compras if c.get('estado') == 'Pendiente']) if compras else 0
            return 0
        except:
            return 0
    
    def obtener_total_vidrios(self):
        """Obtiene total de vidrios en catálogo."""
        try:
            if 'vidrios' in self.module_controllers:
                vidrios = self.module_controllers['vidrios'].get_all_vidrios()
                return len(vidrios) if vidrios else 0
            return 0
        except:
            return 0
    
    def obtener_notificaciones_pendientes(self):
        """Obtiene notificaciones no leídas."""
        try:
            if 'notificaciones' in self.module_controllers:
                notificaciones = self.module_controllers['notificaciones'].get_notificaciones_no_leidas()
                return len(notificaciones) if notificaciones else 0
            return 0
        except:
            return 0
    
    def obtener_ventas_mes(self):
        """Obtiene el total de ventas del mes actual."""
        # Placeholder - implementar con datos reales
        return 45000.0
    
    def obtener_compras_mes(self):
        """Obtiene el total de compras del mes actual."""
        # Placeholder - implementar con datos reales
        return 32000.0
    
    def calcular_margen_ganancia(self, ventas, compras):
        """Calcula el margen de ganancia."""
        if ventas > 0:
            return ((ventas - compras) / ventas) * 100
        return 0.0
    
    def obtener_alertas_sistema(self):
        """Obtiene el número de alertas del sistema."""
        alertas = 0
        alertas += self.obtener_productos_bajo_stock()
        alertas += self.obtener_notificaciones_pendientes()
        return alertas
    
    def get_usuarios_activos(self):
        """Obtiene usuarios activos en el sistema."""
        try:
            if 'usuarios' in self.module_controllers:
                return self.module_controllers['usuarios'].get_all_usuarios() or []
            return []
        except:
            return []
    
    def obtener_datos_ventas_semanales(self):
        """Obtiene datos de ventas por semana."""
        # Datos de ejemplo - implementar con datos reales
        return [12000, 19000, 15000, 25000, 22000, 18000, 30000, 28000]
    
    def obtener_datos_inventario_categorias(self):
        """Obtiene datos de inventario por categorías."""
        # Datos de ejemplo - implementar con datos reales
        return [45, 60, 35, 80, 25]
    
    def obtener_datos_obras_estado(self):
        """Obtiene datos de obras por estado."""
        # Datos de ejemplo - implementar con datos reales
        return [30, 25, 20, 15, 10]
    
    def obtener_actividades_recientes(self):
        """Obtiene actividades recientes del sistema."""
        # Datos de ejemplo - implementar con datos reales
        from PyQt6.QtCore import QDateTime
        return [
            {
                'icono': '👤',
                'titulo': 'Nuevo usuario registrado',
                'descripcion': 'Usuario admin se ha conectado al sistema',
                'timestamp': QDateTime.currentDateTime().addSecs(-300)
            },
            {
                'icono': '📦',
                'titulo': 'Stock actualizado',
                'descripcion': 'Inventario de productos actualizado',
                'timestamp': QDateTime.currentDateTime().addSecs(-600)
            }
        ]
    
    # =================================================================
    # MÉTODOS PÚBLICOS DE CONTROL
    # =================================================================
    
    def abrir_modulo(self, modulo):
        """Abre un módulo específico."""
        self.logger.info(f"Solicitando apertura del módulo: {modulo}")
        # Esta señal será conectada por el controlador principal
        if hasattr(self.parent(), 'abrir_modulo'):
            self.parent().abrir_modulo(modulo)
    
    def generar_reporte(self, tipo_reporte):
        """Genera un reporte específico."""
        self.logger.info(f"Solicitando generación de reporte: {tipo_reporte}")
        # Implementar lógica de reportes
    
    def actualizar_dashboard_manual(self):
        """Actualiza el dashboard manualmente."""
        self.actualizar_todas_metricas()
    
    def pausar_actualizaciones(self):
        """Pausa las actualizaciones automáticas."""
        self.update_timer.stop()
    
    def reanudar_actualizaciones(self):
        """Reanuda las actualizaciones automáticas."""
        self.update_timer.start()