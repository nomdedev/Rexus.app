#!/usr/bin/env python3
"""
Script para crear las tablas adicionales de forma individual
"""

import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def crear_tabla_empleados(db):
    """Crea la tabla empleados"""
    sql = """
    CREATE TABLE empleados (
        id INT PRIMARY KEY IDENTITY(1,1),
        codigo VARCHAR(50) UNIQUE NOT NULL,
        nombre VARCHAR(100) NOT NULL,
        apellido VARCHAR(100) NOT NULL,
        dni VARCHAR(20) UNIQUE NOT NULL,
        telefono VARCHAR(20),
        email VARCHAR(100),
        direccion VARCHAR(255),
        fecha_nacimiento DATE,
        fecha_ingreso DATE NOT NULL,
        salario_base DECIMAL(10,2) NOT NULL,
        cargo VARCHAR(100),
        departamento_id INT,
        estado VARCHAR(20) DEFAULT 'ACTIVO',
        activo BIT DEFAULT 1,
        fecha_creacion DATETIME DEFAULT GETDATE(),
        fecha_modificacion DATETIME DEFAULT GETDATE()
    )
    """
    return db.execute_non_query(sql)

def crear_tabla_departamentos(db):
    """Crea la tabla departamentos"""
    sql = """
    CREATE TABLE departamentos (
        id INT PRIMARY KEY IDENTITY(1,1),
        codigo VARCHAR(50) UNIQUE NOT NULL,
        nombre VARCHAR(100) NOT NULL,
        descripcion VARCHAR(255),
        responsable VARCHAR(100),
        presupuesto_mensual DECIMAL(10,2) DEFAULT 0,
        activo BIT DEFAULT 1,
        fecha_creacion DATETIME DEFAULT GETDATE(),
        fecha_modificacion DATETIME DEFAULT GETDATE()
    )
    """
    return db.execute_non_query(sql)

def crear_tabla_asistencias(db):
    """Crea la tabla asistencias"""
    sql = """
    CREATE TABLE asistencias (
        id INT PRIMARY KEY IDENTITY(1,1),
        empleado_id INT NOT NULL,
        fecha DATE NOT NULL,
        hora_entrada TIME,
        hora_salida TIME,
        horas_trabajadas DECIMAL(4,2) DEFAULT 0,
        horas_extra DECIMAL(4,2) DEFAULT 0,
        tipo VARCHAR(20) DEFAULT 'NORMAL',
        observaciones VARCHAR(255),
        fecha_registro DATETIME DEFAULT GETDATE()
    )
    """
    return db.execute_non_query(sql)

def crear_tabla_nomina(db):
    """Crea la tabla nomina"""
    sql = """
    CREATE TABLE nomina (
        id INT PRIMARY KEY IDENTITY(1,1),
        empleado_id INT NOT NULL,
        mes INT NOT NULL,
        anio INT NOT NULL,
        salario_base DECIMAL(10,2) NOT NULL,
        dias_trabajados INT DEFAULT 0,
        horas_extra DECIMAL(4,2) DEFAULT 0,
        bonos DECIMAL(10,2) DEFAULT 0,
        descuentos DECIMAL(10,2) DEFAULT 0,
        faltas INT DEFAULT 0,
        bruto DECIMAL(10,2) NOT NULL,
        total_descuentos DECIMAL(10,2) DEFAULT 0,
        neto DECIMAL(10,2) NOT NULL,
        fecha_calculo DATETIME DEFAULT GETDATE()
    )
    """
    return db.execute_non_query(sql)

def crear_tabla_bonos_descuentos(db):
    """Crea la tabla bonos_descuentos"""
    sql = """
    CREATE TABLE bonos_descuentos (
        id INT PRIMARY KEY IDENTITY(1,1),
        empleado_id INT NOT NULL,
        tipo VARCHAR(20) NOT NULL,
        concepto VARCHAR(255) NOT NULL,
        monto DECIMAL(10,2) NOT NULL,
        fecha_aplicacion DATE,
        mes_aplicacion INT,
        anio_aplicacion INT,
        estado VARCHAR(20) DEFAULT 'PENDIENTE',
        observaciones VARCHAR(255),
        fecha_creacion DATETIME DEFAULT GETDATE()
    )
    """
    return db.execute_non_query(sql)

def crear_tabla_historial_laboral(db):
    """Crea la tabla historial_laboral"""
    sql = """
    CREATE TABLE historial_laboral (
        id INT PRIMARY KEY IDENTITY(1,1),
        empleado_id INT NOT NULL,
        tipo VARCHAR(50) NOT NULL,
        descripcion VARCHAR(255),
        fecha DATE DEFAULT GETDATE(),
        valor_anterior VARCHAR(100),
        valor_nuevo VARCHAR(100),
        usuario_creacion VARCHAR(50)
    )
    """
    return db.execute_non_query(sql)

def crear_tabla_libro_contable(db):
    """Crea la tabla libro_contable"""
    sql = """
    CREATE TABLE libro_contable (
        id INT PRIMARY KEY IDENTITY(1,1),
        numero_asiento INT NOT NULL,
        fecha_asiento DATE NOT NULL,
        tipo_asiento VARCHAR(50) NOT NULL,
        concepto VARCHAR(255) NOT NULL,
        referencia VARCHAR(100),
        debe DECIMAL(12,2) DEFAULT 0,
        haber DECIMAL(12,2) DEFAULT 0,
        saldo DECIMAL(12,2) DEFAULT 0,
        estado VARCHAR(20) DEFAULT 'ACTIVO',
        usuario_creacion VARCHAR(50),
        fecha_creacion DATETIME DEFAULT GETDATE(),
        fecha_modificacion DATETIME DEFAULT GETDATE()
    )
    """
    return db.execute_non_query(sql)

def crear_tabla_recibos(db):
    """Crea la tabla recibos"""
    sql = """
    CREATE TABLE recibos (
        id INT PRIMARY KEY IDENTITY(1,1),
        numero_recibo INT NOT NULL,
        fecha_emision DATE NOT NULL,
        tipo_recibo VARCHAR(50) NOT NULL,
        concepto VARCHAR(255) NOT NULL,
        beneficiario VARCHAR(255) NOT NULL,
        monto DECIMAL(12,2) NOT NULL,
        moneda VARCHAR(10) DEFAULT 'USD',
        estado VARCHAR(20) DEFAULT 'EMITIDO',
        impreso BIT DEFAULT 0,
        fecha_impresion DATETIME,
        usuario_creacion VARCHAR(50),
        fecha_creacion DATETIME DEFAULT GETDATE()
    )
    """
    return db.execute_non_query(sql)

def crear_tabla_pagos_materiales(db):
    """Crea la tabla pagos_materiales"""
    sql = """
    CREATE TABLE pagos_materiales (
        id INT PRIMARY KEY IDENTITY(1,1),
        producto VARCHAR(255) NOT NULL,
        proveedor VARCHAR(255) NOT NULL,
        cantidad DECIMAL(10,2) NOT NULL,
        precio_unitario DECIMAL(10,2) NOT NULL,
        total DECIMAL(12,2) NOT NULL,
        pagado DECIMAL(12,2) DEFAULT 0,
        pendiente DECIMAL(12,2) DEFAULT 0,
        estado VARCHAR(20) DEFAULT 'PENDIENTE',
        fecha_compra DATE NOT NULL,
        fecha_pago DATE,
        usuario_creacion VARCHAR(50)
    )
    """
    return db.execute_non_query(sql)

def crear_tabla_equipos(db):
    """Crea la tabla equipos"""
    sql = """
    CREATE TABLE equipos (
        id INT PRIMARY KEY IDENTITY(1,1),
        codigo VARCHAR(50) UNIQUE NOT NULL,
        nombre VARCHAR(100) NOT NULL,
        tipo VARCHAR(50) NOT NULL,
        modelo VARCHAR(100),
        marca VARCHAR(100),
        numero_serie VARCHAR(100),
        fecha_adquisicion DATE,
        fecha_instalacion DATE,
        ubicacion VARCHAR(100),
        estado VARCHAR(20) DEFAULT 'OPERATIVO',
        valor_adquisicion DECIMAL(12,2) DEFAULT 0,
        vida_util_anos INT DEFAULT 0,
        ultima_revision DATE,
        proxima_revision DATE,
        observaciones VARCHAR(255),
        activo BIT DEFAULT 1,
        fecha_creacion DATETIME DEFAULT GETDATE(),
        fecha_modificacion DATETIME DEFAULT GETDATE()
    )
    """
    return db.execute_non_query(sql)

def crear_tablas_principales():
    """Crea las tablas principales necesarias"""
    print("CREANDO TABLAS PRINCIPALES - REXUS.APP")
    print("=" * 60)
    
    try:
        from src.core.database import InventarioDatabaseConnection
        
        db = InventarioDatabaseConnection()
        if not db._connection:
            print("[ERROR] No se pudo conectar a la base de datos")
            return False
        
        print("[OK] Conexion a base de datos exitosa")
        
        # Lista de tablas a crear
        tablas_funciones = [
            ("empleados", crear_tabla_empleados),
            ("departamentos", crear_tabla_departamentos),
            ("asistencias", crear_tabla_asistencias),
            ("nomina", crear_tabla_nomina),
            ("bonos_descuentos", crear_tabla_bonos_descuentos),
            ("historial_laboral", crear_tabla_historial_laboral),
            ("libro_contable", crear_tabla_libro_contable),
            ("recibos", crear_tabla_recibos),
            ("pagos_materiales", crear_tabla_pagos_materiales),
            ("equipos", crear_tabla_equipos)
        ]
        
        creadas = 0
        errores = 0
        
        for nombre_tabla, funcion in tablas_funciones:
            try:
                # Verificar si la tabla ya existe
                cursor = db.cursor()
                cursor.execute("SELECT * FROM sysobjects WHERE name=? AND xtype='U'", (nombre_tabla,))
                if cursor.fetchone():
                    print(f"[EXISTE] {nombre_tabla}")
                    creadas += 1
                else:
                    if funcion(db):
                        print(f"[OK] {nombre_tabla} creada")
                        creadas += 1
                    else:
                        print(f"[ERROR] {nombre_tabla} fallo")
                        errores += 1
                cursor.close()
                
            except Exception as e:
                print(f"[ERROR] {nombre_tabla}: {str(e)[:100]}...")
                errores += 1
        
        print(f"\nResultados:")
        print(f"  Tablas creadas/existentes: {creadas}")
        print(f"  Errores: {errores}")
        print(f"  Total: {len(tablas_funciones)}")
        
        return errores == 0
        
    except Exception as e:
        print(f"[ERROR] Error general: {e}")
        return False

def insertar_datos_iniciales():
    """Inserta datos iniciales básicos"""
    print("\n" + "=" * 60)
    print("INSERTANDO DATOS INICIALES")
    print("=" * 60)
    
    try:
        from src.core.database import InventarioDatabaseConnection
        
        db = InventarioDatabaseConnection()
        
        # Insertar departamentos básicos
        departamentos = [
            ("ADMIN", "Administración", "Departamento administrativo"),
            ("PROD", "Producción", "Departamento de producción"),
            ("MANT", "Mantenimiento", "Departamento de mantenimiento"),
            ("COMP", "Compras", "Departamento de compras"),
            ("VENT", "Ventas", "Departamento de ventas")
        ]
        
        for codigo, nombre, descripcion in departamentos:
            try:
                cursor = db.cursor()
                cursor.execute("SELECT * FROM departamentos WHERE codigo = ?", (codigo,))
                if not cursor.fetchone():
                    sql = "INSERT INTO departamentos (codigo, nombre, descripcion) VALUES (?, ?, ?)"
                    db.execute_non_query(sql, (codigo, nombre, descripcion))
                    print(f"[OK] Departamento {nombre} insertado")
                else:
                    print(f"[EXISTE] Departamento {nombre}")
                cursor.close()
            except Exception as e:
                print(f"[ERROR] Departamento {nombre}: {str(e)[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error insertando datos iniciales: {e}")
        return False

def main():
    """Función principal"""
    print("INICIO DEL PROCESO DE CREACION DE TABLAS")
    print("=" * 60)
    
    # Crear tablas principales
    if crear_tablas_principales():
        print("\n[OK] Tablas principales creadas")
    else:
        print("\n[ERROR] Error creando tablas principales")
    
    # Insertar datos iniciales
    if insertar_datos_iniciales():
        print("\n[OK] Datos iniciales insertados")
    else:
        print("\n[ERROR] Error insertando datos iniciales")
    
    print("\n" + "=" * 60)
    print("PROCESO COMPLETADO")
    print("=" * 60)

if __name__ == "__main__":
    main()