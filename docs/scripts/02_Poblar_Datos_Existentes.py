#!/usr/bin/env python3
"""
Script para poblar las tablas existentes con datos de prueba
usando el schema actual de la base de datos
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
import random
import hashlib

# Agregar el directorio raíz al path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.core.database import InventarioDatabaseConnection, UsersDatabaseConnection, AuditoriaDatabaseConnection


class ExistingDataPopulator:
    """Clase para poblar datos usando el schema existente"""
    
    def __init__(self):
        self.db_inventario = None
        self.db_users = None
        self.db_auditoria = None
        self.connect_to_databases()
        
    def connect_to_databases(self):
        """Conecta a las tres bases de datos"""
        try:
            self.db_inventario = InventarioDatabaseConnection()
            self.db_users = UsersDatabaseConnection()
            self.db_auditoria = AuditoriaDatabaseConnection()
            print("OK - Conexion a bases de datos establecida")
        except Exception as e:
            print(f"ERROR - Error conectando a BD: {e}")
            self.db_inventario = None
            self.db_users = None
            self.db_auditoria = None
    
    def populate_users(self):
        """Pobla usuarios en la base de datos users"""
        try:
            # Verificar si ya hay usuarios
            result = self.db_users.execute_query("SELECT COUNT(*) FROM usuarios")
            if result and result[0][0] > 0:
                print("INFO - Usuarios ya existen")
                return
            
            usuarios = [
                ('admin', 'admin123', 'Administrador', 'Sistema', 'admin@rexus.com', '555-0001', 'admin', 'Sistemas'),
                ('supervisor', 'super123', 'Juan Carlos', 'Supervisor', 'supervisor@rexus.com', '555-0002', 'supervisor', 'Obras'),
                ('arquitecto', 'arq123', 'Maria Elena', 'Arquitecta', 'arquitecto@rexus.com', '555-0003', 'usuario', 'Diseno'),
                ('ingeniero', 'ing123', 'Pedro Jose', 'Ingeniero', 'ingeniero@rexus.com', '555-0004', 'usuario', 'Ingenieria'),
                ('compras', 'comp123', 'Ana Maria', 'Compras', 'compras@rexus.com', '555-0005', 'usuario', 'Compras'),
                ('almacen', 'alm123', 'Carlos Eduardo', 'Almacenero', 'almacen@rexus.com', '555-0006', 'usuario', 'Almacen'),
                ('vendedor', 'vend123', 'Laura Patricia', 'Vendedora', 'vendedor@rexus.com', '555-0007', 'usuario', 'Ventas'),
                ('contador', 'cont123', 'Roberto Miguel', 'Contador', 'contador@rexus.com', '555-0008', 'usuario', 'Contabilidad'),
            ]
            
            for usuario, password, nombre, apellido, email, telefono, rol, departamento in usuarios:
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                
                self.db_users.execute_non_query("""
                    INSERT INTO usuarios (usuario, password_hash, nombre, apellido, email, telefono, rol, departamento)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (usuario, password_hash, nombre, apellido, email, telefono, rol, departamento))
            
            print(f"OK - Creados {len(usuarios)} usuarios")
            
        except Exception as e:
            print(f"ERROR - Error poblando usuarios: {e}")
    
    def populate_proveedores(self):
        """Pobla proveedores usando las columnas existentes"""
        try:
            result = self.db_inventario.execute_query("SELECT COUNT(*) FROM proveedores")
            if result and result[0][0] > 0:
                print("INFO - Proveedores ya existen")
                return
            
            # Verificar estructura de la tabla
            cursor = self.db_inventario.cursor()
            cursor.execute("SELECT TOP 1 * FROM proveedores")
            columns = [desc[0] for desc in cursor.description]
            cursor.close()
            print(f"DEBUG - Columnas de proveedores: {columns}")
            
            # Usar solo las columnas básicas que seguramente existen
            proveedores = [
                ('Cementos Nacionales S.A.', 'Jorge Ramirez', '555-1001', 'ventas@cementos.com'),
                ('Aridos del Sur Ltda.', 'Maria Gonzalez', '555-1002', 'info@aridos.com'),
                ('Siderurgica Nacional', 'Carlos Perez', '555-1003', 'pedidos@sider.com'),
                ('Vidrios del Centro', 'Ana Martinez', '555-1004', 'ventas@vidrios.com'),
                ('Herrajes Premium', 'Luis Rodriguez', '555-1005', 'info@herrajes.com'),
                ('Pinturas Profesionales', 'Carmen Silva', '555-1006', 'pedidos@pinturas.com'),
                ('Tuberias Tecnicas', 'Roberto Garcia', '555-1007', 'ventas@tuberias.com'),
                ('Electricos Modernos', 'Patricia Lopez', '555-1008', 'info@electricos.com'),
                ('Maderas del Bosque', 'Diego Fernandez', '555-1009', 'ventas@maderas.com'),
                ('Bloques Constructivos', 'Elena Torres', '555-1010', 'pedidos@bloques.com'),
            ]
            
            for nombre, contacto, telefono, email in proveedores:
                # Usar solo columnas básicas que probablemente existan
                if 'nombre' in columns and 'contacto' in columns:
                    self.db_inventario.execute_non_query("""
                        INSERT INTO proveedores (nombre, contacto, telefono, email)
                        VALUES (?, ?, ?, ?)
                    """, (nombre, contacto, telefono, email))
                else:
                    # Fallback a columnas mínimas
                    self.db_inventario.execute_non_query("""
                        INSERT INTO proveedores (nombre, telefono)
                        VALUES (?, ?)
                    """, (nombre, telefono))
            
            print(f"OK - Creados {len(proveedores)} proveedores")
            
        except Exception as e:
            print(f"ERROR - Error poblando proveedores: {e}")
    
    def populate_obras(self):
        """Pobla obras usando las columnas existentes"""
        try:
            result = self.db_inventario.execute_query("SELECT COUNT(*) FROM obras")
            if result and result[0][0] > 0:
                print("INFO - Obras ya existen")
                return
            
            obras = [
                ('Edificio Residencial "Torres del Parque"', 'Av. Principal 1250, Torre A', '555-2001', 'Constructora ABC S.A.', 'En Proceso'),
                ('Casa Moderna "Villa Esperanza"', 'Urbanizacion Los Pinos, Lote 15', '555-2002', 'Familia Rodriguez Garcia', 'Activa'),
                ('Complejo Comercial "Plaza Central"', 'Av. Comercial 2500, Sector Centro', '555-2003', 'Inversiones Comerciales Norte', 'Planificada'),
                ('Oficinas Corporativas "Business Hub"', 'Zona Empresarial, Edificio Tech', '555-2004', 'TechCorp Internacional S.A.', 'Activa'),
                ('Renovacion Escuela "San Jose"', 'Sector Educativo, Calle 123', '555-2005', 'Ministerio de Educacion', 'Finalizada'),
                ('Condominio "Jardines del Valle"', 'Valle Verde, Fase 1', '555-2006', 'Desarrollos Inmobiliarios SA', 'Planificada'),
                ('Centro Medico "Salud Integral"', 'Av. Medica 500', '555-2007', 'Fundacion Salud para Todos', 'En Proceso'),
                ('Warehouse "Logistica Total"', 'Parque Industrial, Nave 5', '555-2008', 'Distribuidora Nacional Ltda.', 'Activa'),
            ]
            
            for nombre, direccion, telefono, cliente, estado in obras:
                fecha_creacion = datetime.now() - timedelta(days=random.randint(1, 90))
                fecha_entrega = fecha_creacion + timedelta(days=random.randint(30, 365))
                
                self.db_inventario.execute_non_query("""
                    INSERT INTO obras (nombre, direccion, telefono, cliente, estado, fecha_creacion, fecha_entrega, usuario_creador)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (nombre, direccion, telefono, cliente, estado, fecha_creacion, fecha_entrega, 'admin'))
            
            print(f"OK - Creadas {len(obras)} obras")
            
        except Exception as e:
            print(f"ERROR - Error poblando obras: {e}")
    
    def populate_herrajes(self):
        """Pobla herrajes usando las columnas existentes"""
        try:
            result = self.db_inventario.execute_query("SELECT COUNT(*) FROM herrajes")
            if result and result[0][0] > 0:
                print("INFO - Herrajes ya existen")
                return
            
            herrajes = [
                ('HER001', 'Bisagra Puerta 4" Acero', 'Bisagra estandar para puerta', 'Bisagras', 'Herrajes Premium', 12.50, 150, 20, 'Unidad'),
                ('HER002', 'Bisagra Puerta 5" Bronce', 'Bisagra premium de bronce', 'Bisagras', 'Herrajes Premium', 18.75, 100, 15, 'Unidad'),
                ('HER003', 'Cerradura Seguridad Exterior', 'Cerradura con cilindro europeo', 'Cerraduras', 'Herrajes Premium', 145.00, 80, 10, 'Unidad'),
                ('HER004', 'Cerradura Interior Paso', 'Cerradura para interiores', 'Cerraduras', 'Herrajes Premium', 95.00, 120, 15, 'Unidad'),
                ('HER005', 'Manija Puerta Dorada', 'Manija decorativa dorada', 'Manijas', 'Herrajes Premium', 42.00, 80, 10, 'Unidad'),
                ('HER006', 'Manija Puerta Plateada', 'Manija cromada estandar', 'Manijas', 'Herrajes Premium', 35.00, 100, 12, 'Unidad'),
                ('HER007', 'Aldaba Porton Grande', 'Aldaba para portones pesados', 'Aldabas', 'Herrajes Premium', 65.00, 40, 8, 'Unidad'),
                ('HER008', 'Candado Seguridad 60mm', 'Candado con arco templado', 'Candados', 'Herrajes Premium', 35.00, 100, 15, 'Unidad'),
                ('HER009', 'Riel Corredizo 2m', 'Riel con rodamientos incluidos', 'Rieles', 'Herrajes Premium', 85.00, 30, 5, 'Unidad'),
                ('HER010', 'Tornillo Madera 3" Caja', 'Tornillos galvanizados', 'Tornilleria', 'Herrajes Premium', 12.50, 200, 25, 'Caja'),
            ]
            
            for codigo, nombre, descripcion, categoria, proveedor, precio, stock, minimo, unidad in herrajes:
                self.db_inventario.execute_non_query("""
                    INSERT INTO herrajes (codigo, nombre, descripcion, categoria, proveedor, precio_unitario, stock_actual, stock_minimo, unidad_medida, activo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (codigo, nombre, descripcion, categoria, proveedor, precio, stock, minimo, unidad, 1))
            
            print(f"OK - Creados {len(herrajes)} herrajes")
            
        except Exception as e:
            print(f"ERROR - Error poblando herrajes: {e}")
    
    def populate_vidrios(self):
        """Pobla vidrios usando las columnas existentes"""
        try:
            result = self.db_inventario.execute_query("SELECT COUNT(*) FROM vidrios")
            if result and result[0][0] > 0:
                print("INFO - Vidrios ya existen")
                return
            
            vidrios = [
                ('Vidrio Templado', 6.0, 'Transparente', 95.00, 'Vidrios del Centro', 'Vidrio de seguridad templado', 'Resistente, antirrotura'),
                ('Vidrio Templado', 8.0, 'Transparente', 110.00, 'Vidrios del Centro', 'Extra resistente', 'Alta resistencia'),
                ('Vidrio Laminado', 6.38, 'Transparente', 115.00, 'Vidrios del Centro', 'Laminado con PVB', 'Seguridad, antirrotura'),
                ('Vidrio Laminado', 8.76, 'Transparente', 135.00, 'Vidrios del Centro', 'Alta seguridad', 'Maximo nivel de seguridad'),
                ('Vidrio Comun', 4.0, 'Transparente', 42.00, 'Vidrios del Centro', 'Uso general', 'Estandar, economico'),
                ('Vidrio Comun', 6.0, 'Transparente', 55.00, 'Vidrios del Centro', 'Uso general', 'Estandar, mas grueso'),
                ('Vidrio Esmerilado', 6.0, 'Esmerilado', 75.00, 'Vidrios del Centro', 'Para privacidad', 'Translucido, privacidad'),
                ('Vidrio Tintado', 6.0, 'Bronce', 88.00, 'Vidrios del Centro', 'Reduce calor solar', 'Control solar'),
                ('Vidrio Tintado', 6.0, 'Gris', 88.00, 'Vidrios del Centro', 'Reduce calor solar', 'Control solar'),
                ('Vidrio Espejo', 4.0, 'Espejo', 65.00, 'Vidrios del Centro', 'Espejo de primera', 'Reflectante, decorativo'),
            ]
            
            for tipo, espesor, color, precio, proveedor, especificaciones, propiedades in vidrios:
                self.db_inventario.execute_non_query("""
                    INSERT INTO vidrios (tipo, espesor, color, precio_m2, proveedor, especificaciones, propiedades, activo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (tipo, espesor, color, precio, proveedor, especificaciones, propiedades, 1))
            
            print(f"OK - Creados {len(vidrios)} vidrios")
            
        except Exception as e:
            print(f"ERROR - Error poblando vidrios: {e}")
    
    def populate_empleados(self):
        """Pobla empleados usando las columnas existentes"""
        try:
            result = self.db_inventario.execute_query("SELECT COUNT(*) FROM empleados")
            if result and result[0][0] > 0:
                print("INFO - Empleados ya existen")
                return
            
            empleados = [
                ('EMP001', 'Carlos Alberto', 'Rodriguez Silva', '12345678', '555-3001', 'carlos@rexus.com', 'Av. Central 123', 'Supervisor de Obra', 48000.00, 'Activo'),
                ('EMP002', 'Maria Elena', 'Gonzalez Lopez', '87654321', '555-3002', 'maria@rexus.com', 'Calle Norte 456', 'Arquitecta Senior', 62000.00, 'Activo'),
                ('EMP003', 'Juan Carlos', 'Perez Martinez', '11223344', '555-3003', 'juan@rexus.com', 'Av. Sur 789', 'Maestro Albanil', 38000.00, 'Activo'),
                ('EMP004', 'Ana Patricia', 'Lopez Garcia', '44332211', '555-3004', 'ana@rexus.com', 'Sector Este 321', 'Ingeniera Civil', 58000.00, 'Activo'),
                ('EMP005', 'Pedro Miguel', 'Martinez Torres', '55667788', '555-3005', 'pedro@rexus.com', 'Zona Oeste 654', 'Operario Especializado', 32000.00, 'Activo'),
                ('EMP006', 'Laura Cristina', 'Sanchez Ruiz', '99887766', '555-3006', 'laura@rexus.com', 'Av. Principal 987', 'Contadora', 45000.00, 'Activo'),
                ('EMP007', 'Diego Fernando', 'Fernandez Castro', '66778899', '555-3007', 'diego@rexus.com', 'Calle Industrial 147', 'Electricista', 42000.00, 'Activo'),
                ('EMP008', 'Carmen Rosa', 'Torres Vega', '33445566', '555-3008', 'carmen@rexus.com', 'Av. Comercial 258', 'Diseñadora', 44000.00, 'Activo'),
                ('EMP009', 'Roberto Carlos', 'Silva Mendoza', '77889900', '555-3009', 'roberto@rexus.com', 'Sector Residencial 369', 'Soldador', 36000.00, 'Activo'),
                ('EMP010', 'Patricia Isabel', 'Morales Jimenez', '22334455', '555-3010', 'patricia@rexus.com', 'Calle Tecnica 741', 'Jefa de Compras', 52000.00, 'Activo'),
            ]
            
            for codigo, nombre, apellido, dni, telefono, email, direccion, cargo, salario, estado in empleados:
                fecha_nacimiento = datetime.now() - timedelta(days=random.randint(7300, 18250))  # 20-50 años
                fecha_ingreso = datetime.now() - timedelta(days=random.randint(30, 1095))
                
                self.db_inventario.execute_non_query("""
                    INSERT INTO empleados (codigo, nombre, apellido, dni, telefono, email, direccion, fecha_nacimiento, fecha_ingreso, salario_base, cargo, estado, activo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (codigo, nombre, apellido, dni, telefono, email, direccion, fecha_nacimiento, fecha_ingreso, salario, cargo, estado, 1))
            
            print(f"OK - Creados {len(empleados)} empleados")
            
        except Exception as e:
            print(f"ERROR - Error poblando empleados: {e}")
    
    def populate_equipos(self):
        """Pobla equipos usando las columnas existentes"""
        try:
            result = self.db_inventario.execute_query("SELECT COUNT(*) FROM equipos")
            if result and result[0][0] > 0:
                print("INFO - Equipos ya existen")
                return
            
            equipos = [
                ('EQU001', 'Mezcladora de Concreto Movil', 'Mezcladora', 'CM-500', 'Caterpillar', 'CAT500M2024', 'Obra Torres del Parque', 'Operativo', 28000.00, 7),
                ('EQU002', 'Grua Torre 50 Toneladas', 'Grua', 'LTM-1050', 'Liebherr', 'LH1050T2023', 'Obra Plaza Central', 'Operativo', 220000.00, 15),
                ('EQU003', 'Excavadora Hidraulica', 'Excavadora', '320D', 'Caterpillar', 'CAT320D2022', 'Obra Business Hub', 'Operativo', 185000.00, 12),
                ('EQU004', 'Soldadora Industrial TIG', 'Soldadora', 'Power Wave AC/DC', 'Lincoln', 'LN-PWAC2024', 'Taller Principal', 'Operativo', 12500.00, 10),
                ('EQU005', 'Compresor de Aire Estacionario', 'Compresor', 'GA-55', 'Atlas Copco', 'AC-GA55-2023', 'Taller Principal', 'Operativo', 18500.00, 8),
                ('EQU006', 'Camion Volquete 15 Toneladas', 'Transporte', 'FH16-750', 'Volvo', 'VLV-FH16-2023', 'Base Logistica', 'Operativo', 145000.00, 20),
                ('EQU007', 'Martillo Neumatico Pesado', 'Herramienta', 'GSH-27VC', 'Bosch', 'BSH-27VC-2024', 'Almacen Herramientas', 'Operativo', 1450.00, 5),
                ('EQU008', 'Cortadora de Concreto', 'Cortadora', 'K-970', 'Husqvarna', 'HSQ-K970-2023', 'Taller Reparaciones', 'Mantenimiento', 4200.00, 8),
                ('EQU009', 'Andamio Movil 8 Metros', 'Andamio', 'Topic', 'Layher', 'LY-TOP8-2024', 'Obra Villa Esperanza', 'Operativo', 8500.00, 15),
                ('EQU010', 'Vibrador de Concreto', 'Vibrador', 'M-3000', 'Wacker', 'WK-M3000-2024', 'Obra Torres del Parque', 'Operativo', 2800.00, 6),
            ]
            
            for codigo, nombre, tipo, modelo, marca, numero_serie, ubicacion, estado, valor, vida_util in equipos:
                fecha_adquisicion = datetime.now() - timedelta(days=random.randint(30, 730))
                fecha_instalacion = fecha_adquisicion + timedelta(days=random.randint(1, 30))
                ultima_revision = datetime.now() - timedelta(days=random.randint(1, 90))
                proxima_revision = ultima_revision + timedelta(days=random.randint(90, 180))
                
                self.db_inventario.execute_non_query("""
                    INSERT INTO equipos (codigo, nombre, tipo, modelo, marca, numero_serie, fecha_adquisicion, fecha_instalacion, ubicacion, estado, valor_adquisicion, vida_util_anos, ultima_revision, proxima_revision, activo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (codigo, nombre, tipo, modelo, marca, numero_serie, fecha_adquisicion, fecha_instalacion, ubicacion, estado, valor, vida_util, ultima_revision, proxima_revision, 1))
            
            print(f"OK - Creados {len(equipos)} equipos")
            
        except Exception as e:
            print(f"ERROR - Error poblando equipos: {e}")
    
    def populate_all_data(self):
        """Pobla todas las tablas con datos"""
        print("INICIANDO POBLACION DE DATOS CON SCHEMA EXISTENTE")
        print("=" * 60)
        
        try:
            print("\nPOBLANDO DATOS BASE...")
            self.populate_users()
            self.populate_proveedores()
            
            print("\nPOBLANDO DATOS OPERATIVOS...")
            self.populate_obras()
            self.populate_herrajes()
            self.populate_vidrios()
            self.populate_empleados()
            self.populate_equipos()
            
            print("\n" + "=" * 60)
            print("POBLACION DE DATOS COMPLETADA")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"ERROR - Error poblando datos: {e}")
            return False
    
    def cleanup(self):
        """Limpia recursos"""
        if self.db_inventario:
            self.db_inventario.disconnect()
        if self.db_users:
            self.db_users.disconnect()
        if self.db_auditoria:
            self.db_auditoria.disconnect()


def main():
    """Función principal"""
    print("SISTEMA DE POBLACION DE DATOS REXUS.APP - SCHEMA EXISTENTE")
    print("=" * 70)
    
    populator = ExistingDataPopulator()
    
    try:
        if not populator.db_inventario or not populator.db_users or not populator.db_auditoria:
            print("ERROR - No se pudieron conectar a las bases de datos")
            return 1
        
        success = populator.populate_all_data()
        
        if success:
            print("\nDATOS POBLADOS EXITOSAMENTE!")
            print("La aplicacion Rexus.app ahora tiene datos de prueba para:")
            print("- Obras con datos reales")
            print("- Herrajes con stock y precios")
            print("- Vidrios con especificaciones")
            print("- Empleados con información completa")
            print("- Equipos con seguimiento")
            print("- Proveedores activos")
            print("- Usuarios para login")
            print("\nCredenciales de acceso:")
            print("- admin / admin123")
            print("- supervisor / super123")
            print("- compras / comp123")
            print("- almacen / alm123")
            return 0
        else:
            print("\nERROR - Error poblando datos")
            return 1
            
    except Exception as e:
        print(f"\nFATAL - Error fatal: {e}")
        return 1
    finally:
        populator.cleanup()


if __name__ == "__main__":
    sys.exit(main())