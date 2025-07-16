#!/usr/bin/env python3
"""
Script para crear las tablas adicionales faltantes
"""

import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def crear_tablas_mantenimiento(db):
    """Crea las tablas para el módulo de mantenimiento"""
    print("\n[MANTENIMIENTO] Creando tablas...")
    
    tablas = [
        {
            'nombre': 'herramientas',
            'sql': """
                CREATE TABLE herramientas (
                    id INT PRIMARY KEY IDENTITY(1,1),
                    codigo VARCHAR(50) UNIQUE NOT NULL,
                    nombre VARCHAR(100) NOT NULL,
                    tipo VARCHAR(50) NOT NULL,
                    marca VARCHAR(100),
                    modelo VARCHAR(100),
                    numero_serie VARCHAR(100),
                    fecha_adquisicion DATE,
                    ubicacion VARCHAR(100),
                    estado VARCHAR(20) DEFAULT 'DISPONIBLE',
                    valor_adquisicion DECIMAL(12,2) DEFAULT 0,
                    vida_util_anos INT DEFAULT 0,
                    observaciones VARCHAR(255),
                    activo BIT DEFAULT 1,
                    fecha_creacion DATETIME DEFAULT GETDATE()
                )
            """
        },
        {
            'nombre': 'mantenimientos',
            'sql': """
                CREATE TABLE mantenimientos (
                    id INT PRIMARY KEY IDENTITY(1,1),
                    equipo_id INT NOT NULL,
                    tipo VARCHAR(50) NOT NULL,
                    descripcion VARCHAR(255),
                    fecha_programada DATE NOT NULL,
                    fecha_realizacion DATE,
                    estado VARCHAR(20) DEFAULT 'PROGRAMADO',
                    observaciones VARCHAR(255),
                    costo_estimado DECIMAL(10,2) DEFAULT 0,
                    costo_real DECIMAL(10,2) DEFAULT 0,
                    responsable VARCHAR(100),
                    fecha_creacion DATETIME DEFAULT GETDATE()
                )
            """
        },
        {
            'nombre': 'programacion_mantenimiento',
            'sql': """
                CREATE TABLE programacion_mantenimiento (
                    id INT PRIMARY KEY IDENTITY(1,1),
                    equipo_id INT NOT NULL,
                    tipo_mantenimiento VARCHAR(50) NOT NULL,
                    frecuencia_dias INT NOT NULL,
                    ultima_fecha DATE,
                    proxima_fecha DATE,
                    activo BIT DEFAULT 1,
                    observaciones VARCHAR(255),
                    fecha_creacion DATETIME DEFAULT GETDATE()
                )
            """
        },
        {
            'nombre': 'tipos_mantenimiento',
            'sql': """
                CREATE TABLE tipos_mantenimiento (
                    id INT PRIMARY KEY IDENTITY(1,1),
                    codigo VARCHAR(50) UNIQUE NOT NULL,
                    nombre VARCHAR(100) NOT NULL,
                    descripcion VARCHAR(255),
                    frecuencia_dias INT DEFAULT 0,
                    activo BIT DEFAULT 1
                )
            """
        },
        {
            'nombre': 'estado_equipos',
            'sql': """
                CREATE TABLE estado_equipos (
                    id INT PRIMARY KEY IDENTITY(1,1),
                    equipo_id INT NOT NULL,
                    estado VARCHAR(20) NOT NULL,
                    fecha_cambio DATE DEFAULT GETDATE(),
                    motivo VARCHAR(255),
                    usuario VARCHAR(50),
                    observaciones VARCHAR(255)
                )
            """
        },
        {
            'nombre': 'historial_mantenimiento',
            'sql': """
                CREATE TABLE historial_mantenimiento (
                    id INT PRIMARY KEY IDENTITY(1,1),
                    equipo_id INT,
                    mantenimiento_id INT,
                    tipo VARCHAR(50) NOT NULL,
                    descripcion VARCHAR(255),
                    fecha DATETIME DEFAULT GETDATE(),
                    usuario VARCHAR(50)
                )
            """
        }
    ]
    
    creadas = 0
    errores = 0
    
    for tabla in tablas:
        try:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM sysobjects WHERE name=? AND xtype='U'", (tabla['nombre'],))
            if cursor.fetchone():
                print(f"[EXISTE] {tabla['nombre']}")
                creadas += 1
            else:
                cursor.execute(tabla['sql'])
                db.commit()
                print(f"[OK] {tabla['nombre']} creada")
                creadas += 1
            cursor.close()
        except Exception as e:
            print(f"[ERROR] {tabla['nombre']}: {str(e)[:100]}...")
            errores += 1
    
    return creadas, errores

def crear_tablas_logistica(db):
    """Crea las tablas para el módulo de logística"""
    print("\n[LOGÍSTICA] Creando tablas...")
    
    tablas = [
        {
            'nombre': 'transportes',
            'sql': """
                CREATE TABLE transportes (
                    id INT PRIMARY KEY IDENTITY(1,1),
                    codigo VARCHAR(50) UNIQUE NOT NULL,
                    tipo VARCHAR(50) NOT NULL,
                    proveedor VARCHAR(255) NOT NULL,
                    capacidad_kg DECIMAL(10,2) DEFAULT 0,
                    capacidad_m3 DECIMAL(10,2) DEFAULT 0,
                    costo_km DECIMAL(10,2) DEFAULT 0,
                    disponible BIT DEFAULT 1,
                    observaciones VARCHAR(255),
                    activo BIT DEFAULT 1,
                    fecha_creacion DATETIME DEFAULT GETDATE(),
                    fecha_modificacion DATETIME DEFAULT GETDATE()
                )
            """
        },
        {
            'nombre': 'entregas',
            'sql': """
                CREATE TABLE entregas (
                    id INT PRIMARY KEY IDENTITY(1,1),
                    obra_id INT NOT NULL,
                    transporte_id INT NOT NULL,
                    fecha_programada DATE NOT NULL,
                    fecha_entrega DATE,
                    direccion_entrega VARCHAR(255),
                    contacto VARCHAR(100),
                    telefono VARCHAR(20),
                    estado VARCHAR(20) DEFAULT 'PROGRAMADA',
                    observaciones VARCHAR(255),
                    costo_envio DECIMAL(10,2) DEFAULT 0,
                    usuario_creacion VARCHAR(50),
                    fecha_creacion DATETIME DEFAULT GETDATE()
                )
            """
        },
        {
            'nombre': 'detalle_entregas',
            'sql': """
                CREATE TABLE detalle_entregas (
                    id INT PRIMARY KEY IDENTITY(1,1),
                    entrega_id INT NOT NULL,
                    producto VARCHAR(255) NOT NULL,
                    cantidad DECIMAL(10,2) NOT NULL,
                    peso_kg DECIMAL(10,2) DEFAULT 0,
                    volumen_m3 DECIMAL(10,2) DEFAULT 0,
                    observaciones VARCHAR(255)
                )
            """
        },
        {
            'nombre': 'proveedores_transporte',
            'sql': """
                CREATE TABLE proveedores_transporte (
                    id INT PRIMARY KEY IDENTITY(1,1),
                    nombre VARCHAR(255) NOT NULL,
                    contacto VARCHAR(100),
                    telefono VARCHAR(20),
                    email VARCHAR(100),
                    direccion VARCHAR(255),
                    activo BIT DEFAULT 1,
                    fecha_creacion DATETIME DEFAULT GETDATE()
                )
            """
        },
        {
            'nombre': 'rutas',
            'sql': """
                CREATE TABLE rutas (
                    id INT PRIMARY KEY IDENTITY(1,1),
                    origen VARCHAR(255) NOT NULL,
                    destino VARCHAR(255) NOT NULL,
                    distancia_km DECIMAL(10,2) NOT NULL,
                    tiempo_estimado INT DEFAULT 0,
                    observaciones VARCHAR(255),
                    activo BIT DEFAULT 1
                )
            """
        },
        {
            'nombre': 'costos_logisticos',
            'sql': """
                CREATE TABLE costos_logisticos (
                    id INT PRIMARY KEY IDENTITY(1,1),
                    transporte_id INT NOT NULL,
                    fecha DATE NOT NULL,
                    concepto VARCHAR(255) NOT NULL,
                    monto DECIMAL(10,2) NOT NULL,
                    tipo VARCHAR(50) NOT NULL,
                    observaciones VARCHAR(255),
                    fecha_creacion DATETIME DEFAULT GETDATE()
                )
            """
        }
    ]
    
    creadas = 0
    errores = 0
    
    for tabla in tablas:
        try:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM sysobjects WHERE name=? AND xtype='U'", (tabla['nombre'],))
            if cursor.fetchone():
                print(f"[EXISTE] {tabla['nombre']}")
                creadas += 1
            else:
                cursor.execute(tabla['sql'])
                db.commit()
                print(f"[OK] {tabla['nombre']} creada")
                creadas += 1
            cursor.close()
        except Exception as e:
            print(f"[ERROR] {tabla['nombre']}: {str(e)[:100]}...")
            errores += 1
    
    return creadas, errores

def crear_tablas_configuracion(db):
    """Crea las tablas para el módulo de configuración"""
    print("\n[CONFIGURACIÓN] Creando tablas...")
    
    tablas = [
        {
            'nombre': 'configuracion_sistema',
            'sql': """
                CREATE TABLE configuracion_sistema (
                    id INT PRIMARY KEY IDENTITY(1,1),
                    clave VARCHAR(100) UNIQUE NOT NULL,
                    valor VARCHAR(500),
                    descripcion VARCHAR(255),
                    tipo VARCHAR(50) DEFAULT 'STRING',
                    categoria VARCHAR(50) DEFAULT 'GENERAL',
                    activo BIT DEFAULT 1,
                    fecha_creacion DATETIME DEFAULT GETDATE(),
                    fecha_modificacion DATETIME DEFAULT GETDATE()
                )
            """
        },
        {
            'nombre': 'parametros_modulos',
            'sql': """
                CREATE TABLE parametros_modulos (
                    id INT PRIMARY KEY IDENTITY(1,1),
                    modulo VARCHAR(50) NOT NULL,
                    parametro VARCHAR(100) NOT NULL,
                    valor VARCHAR(500),
                    tipo VARCHAR(50) DEFAULT 'STRING',
                    descripcion VARCHAR(255),
                    activo BIT DEFAULT 1,
                    fecha_creacion DATETIME DEFAULT GETDATE(),
                    fecha_modificacion DATETIME DEFAULT GETDATE()
                )
            """
        },
        {
            'nombre': 'auditoria_cambios',
            'sql': """
                CREATE TABLE auditoria_cambios (
                    id INT PRIMARY KEY IDENTITY(1,1),
                    tabla VARCHAR(50) NOT NULL,
                    registro_id INT NOT NULL,
                    accion VARCHAR(20) NOT NULL,
                    campo VARCHAR(50),
                    valor_anterior VARCHAR(500),
                    valor_nuevo VARCHAR(500),
                    usuario VARCHAR(50),
                    fecha_cambio DATETIME DEFAULT GETDATE(),
                    ip_address VARCHAR(45),
                    observaciones VARCHAR(255)
                )
            """
        },
        {
            'nombre': 'logs_sistema',
            'sql': """
                CREATE TABLE logs_sistema (
                    id INT PRIMARY KEY IDENTITY(1,1),
                    nivel VARCHAR(20) NOT NULL,
                    modulo VARCHAR(50) NOT NULL,
                    mensaje VARCHAR(1000) NOT NULL,
                    detalle VARCHAR(2000),
                    usuario VARCHAR(50),
                    ip_address VARCHAR(45),
                    fecha_log DATETIME DEFAULT GETDATE()
                )
            """
        }
    ]
    
    creadas = 0
    errores = 0
    
    for tabla in tablas:
        try:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM sysobjects WHERE name=? AND xtype='U'", (tabla['nombre'],))
            if cursor.fetchone():
                print(f"[EXISTE] {tabla['nombre']}")
                creadas += 1
            else:
                cursor.execute(tabla['sql'])
                db.commit()
                print(f"[OK] {tabla['nombre']} creada")
                creadas += 1
            cursor.close()
        except Exception as e:
            print(f"[ERROR] {tabla['nombre']}: {str(e)[:100]}...")
            errores += 1
    
    return creadas, errores

def insertar_datos_iniciales_adicionales(db):
    """Inserta datos iniciales para las nuevas tablas"""
    print("\n[DATOS INICIALES] Insertando datos...")
    
    try:
        # Insertar tipos de mantenimiento
        tipos_mantenimiento = [
            ('PREV', 'Preventivo', 'Mantenimiento preventivo regular', 30),
            ('CORR', 'Correctivo', 'Mantenimiento correctivo por falla', 0),
            ('PRED', 'Predictivo', 'Mantenimiento predictivo basado en condiciones', 90),
            ('EMERG', 'Emergencia', 'Mantenimiento de emergencia', 0)
        ]
        
        for codigo, nombre, descripcion, frecuencia in tipos_mantenimiento:
            try:
                cursor = db.cursor()
                cursor.execute("SELECT * FROM tipos_mantenimiento WHERE codigo = ?", (codigo,))
                if not cursor.fetchone():
                    sql = "INSERT INTO tipos_mantenimiento (codigo, nombre, descripcion, frecuencia_dias) VALUES (?, ?, ?, ?)"
                    cursor.execute(sql, (codigo, nombre, descripcion, frecuencia))
                    db.commit()
                    print(f"[OK] Tipo de mantenimiento {nombre} insertado")
                else:
                    print(f"[EXISTE] Tipo de mantenimiento {nombre}")
                cursor.close()
            except Exception as e:
                print(f"[ERROR] Tipo de mantenimiento {nombre}: {str(e)[:50]}...")
        
        # Insertar configuraciones iniciales del sistema
        configuraciones = [
            ('EMPRESA_NOMBRE', 'Rexus Construction', 'Nombre de la empresa', 'STRING', 'GENERAL'),
            ('EMPRESA_RIF', 'J-12345678-9', 'RIF de la empresa', 'STRING', 'GENERAL'),
            ('EMPRESA_TELEFONO', '0212-1234567', 'Teléfono de la empresa', 'STRING', 'GENERAL'),
            ('EMPRESA_EMAIL', 'info@rexus.com', 'Email de la empresa', 'STRING', 'GENERAL'),
            ('MONEDA_PRINCIPAL', 'USD', 'Moneda principal del sistema', 'STRING', 'FINANCIERO'),
            ('BACKUP_AUTOMATICO', '1', 'Activar backup automático', 'BOOLEAN', 'SISTEMA'),
            ('DIAS_BACKUP', '7', 'Días para mantener backups', 'INTEGER', 'SISTEMA')
        ]
        
        for clave, valor, descripcion, tipo, categoria in configuraciones:
            try:
                cursor = db.cursor()
                cursor.execute("SELECT * FROM configuracion_sistema WHERE clave = ?", (clave,))
                if not cursor.fetchone():
                    sql = "INSERT INTO configuracion_sistema (clave, valor, descripcion, tipo, categoria) VALUES (?, ?, ?, ?, ?)"
                    cursor.execute(sql, (clave, valor, descripcion, tipo, categoria))
                    db.commit()
                    print(f"[OK] Configuración {clave} insertada")
                else:
                    print(f"[EXISTE] Configuración {clave}")
                cursor.close()
            except Exception as e:
                print(f"[ERROR] Configuración {clave}: {str(e)[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error insertando datos iniciales: {e}")
        return False

def main():
    """Función principal"""
    print("CREANDO TABLAS ADICIONALES FALTANTES")
    print("="*60)
    
    try:
        from src.core.database import InventarioDatabaseConnection
        
        db = InventarioDatabaseConnection()
        if not db._connection:
            print("[ERROR] No se pudo conectar a la base de datos")
            return False
        
        print("[OK] Conexión a base de datos exitosa")
        
        total_creadas = 0
        total_errores = 0
        
        # Crear tablas de mantenimiento
        creadas, errores = crear_tablas_mantenimiento(db)
        total_creadas += creadas
        total_errores += errores
        
        # Crear tablas de logística
        creadas, errores = crear_tablas_logistica(db)
        total_creadas += creadas
        total_errores += errores
        
        # Crear tablas de configuración
        creadas, errores = crear_tablas_configuracion(db)
        total_creadas += creadas
        total_errores += errores
        
        # Insertar datos iniciales
        if insertar_datos_iniciales_adicionales(db):
            print("\n[OK] Datos iniciales insertados")
        else:
            print("\n[ERROR] Error insertando datos iniciales")
        
        print(f"\n{'='*60}")
        print("RESUMEN FINAL")
        print(f"{'='*60}")
        print(f"Tablas creadas/existentes: {total_creadas}")
        print(f"Errores: {total_errores}")
        print(f"Proceso completado")
        
        return total_errores == 0
        
    except Exception as e:
        print(f"[ERROR] Error general: {e}")
        return False

if __name__ == "__main__":
    main()