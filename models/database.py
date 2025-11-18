"""
db_manager.py - Gestor de Base de Datos

Este módulo maneja toda la interacción con la base de datos SQLite.
SQLite es una base de datos que se guarda en un archivo .db y no necesita servidor.

SEGURIDAD:
- Usa bcrypt para encriptar contraseñas
- Previene SQL injection con parámetros
"""

import sqlite3
import bcrypt
import os
from datetime import datetime

class DatabaseManager:
    """Clase que maneja todas las operaciones de la base de datos"""

    def __init__(self, db_path='models/airsolutions.db'):
        """
        Inicializa el gestor de base de datos

        Args:
            db_path (str): Ruta donde se guardará la base de datos
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def conectar(self):
        """Establece conexión con la base de datos"""
        try:
            # Crear carpeta database si no existe
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

            # Conectar a la base de datos (la crea si no existe)
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()

            # Habilitar foreign keys (restricciones de clave foránea)
            self.cursor.execute("PRAGMA foreign_keys = ON")

            print(f"[OK] Conectado a la base de datos: {self.db_path}")
            return True

        except sqlite3.Error as e:
            print(f"[ERROR] Error al conectar a la base de datos: {e}")
            return False

    def desconectar(self):
        """Cierra la conexión con la base de datos"""
        if self.conn:
            self.conn.close()
            print("[OK] Base de datos cerrada")

    def crear_tablas(self):
        """Crea todas las tablas necesarias si no existen"""
        try:
            # Tabla de usuarios (para login y seguridad)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_usuario TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    nombre_completo TEXT NOT NULL,
                    email TEXT,
                    activo INTEGER DEFAULT 1,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Tabla de clientes
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS clientes (
                    id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_empresa TEXT NOT NULL,
                    contacto_nombre TEXT,
                    telefono TEXT,
                    email TEXT,
                    direccion TEXT,
                    notas TEXT,
                    activo INTEGER DEFAULT 1,
                    cedula_juridica TEXT,
                    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Tabla de productos/equipos HVAC
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS productos_equipos (
                    id_equipo INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo_equipo TEXT NOT NULL,
                    categoria TEXT NOT NULL,
                    precio_base REAL DEFAULT 0,
                    horas_mantenimiento REAL DEFAULT 0,
                    descripcion TEXT,
                    activo INTEGER DEFAULT 1
                )
            ''')

            # Tabla de materiales y repuestos
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS materiales_repuestos (
                    id_material INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_material TEXT NOT NULL,
                    codigo_producto TEXT,
                    precio_unitario REAL DEFAULT 0,
                    unidad_medida TEXT,
                    stock_actual REAL DEFAULT 0,
                    activo INTEGER DEFAULT 1
                )
            ''')

            # Tabla de cotizaciones
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS cotizaciones (
                    id_cotizacion INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_cotizacion TEXT UNIQUE NOT NULL,
                    id_cliente INTEGER NOT NULL,
                    fecha_emision DATE NOT NULL,
                    fecha_vencimiento DATE,
                    tipo_servicio TEXT,
                    visitas_anuales INTEGER DEFAULT 1,
                    factor_venta REAL DEFAULT 1.5,
                    iva REAL DEFAULT 0.13,
                    tipo_cambio REAL DEFAULT 515,
                    subtotal REAL DEFAULT 0,
                    total_materiales REAL DEFAULT 0,
                    total_mano_obra REAL DEFAULT 0,
                    total_gastos REAL DEFAULT 0,
                    total_iva REAL DEFAULT 0,
                    total REAL DEFAULT 0,
                    estado TEXT DEFAULT 'pendiente',
                    notas TEXT,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
                )
            ''')

            # Tabla de detalle de cotización (equipos por cotización)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS detalle_cotizacion (
                    id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_cotizacion INTEGER NOT NULL,
                    id_equipo INTEGER NOT NULL,
                    cantidad INTEGER NOT NULL,
                    horas_por_equipo REAL,
                    precio_unitario REAL NOT NULL,
                    subtotal REAL NOT NULL,
                    FOREIGN KEY (id_cotizacion) REFERENCES cotizaciones(id_cotizacion),
                    FOREIGN KEY (id_equipo) REFERENCES productos_equipos(id_equipo)
                )
            ''')

            # Tabla de materiales por cotización
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS cotizacion_materiales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_cotizacion INTEGER NOT NULL,
                    id_material INTEGER NOT NULL,
                    cantidad REAL NOT NULL,
                    precio_unitario REAL NOT NULL,
                    subtotal REAL NOT NULL,
                    FOREIGN KEY (id_cotizacion) REFERENCES cotizaciones(id_cotizacion),
                    FOREIGN KEY (id_material) REFERENCES materiales_repuestos(id_material)
                )
            ''')

            # Tabla de gastos adicionales
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS gastos_adicionales (
                    id_gasto INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_cotizacion INTEGER NOT NULL,
                    concepto TEXT NOT NULL,
                    descripcion TEXT,
                    monto REAL NOT NULL,
                    FOREIGN KEY (id_cotizacion) REFERENCES cotizaciones(id_cotizacion)
                )
            ''')

            # Tabla de configuración general
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS configuracion (
                    clave TEXT PRIMARY KEY,
                    valor TEXT NOT NULL,
                    descripcion TEXT
                )
            ''')

            # ===== TABLAS PARA PROYECTOS GRANDES =====

            # Tabla de catálogo de componentes HVAC
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS catalogo_hvac (
                    id_componente INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo TEXT UNIQUE NOT NULL,
                    descripcion TEXT NOT NULL,
                    categoria TEXT NOT NULL,
                    unidad_medida TEXT DEFAULT 'unidad',
                    costo_equipo_base REAL DEFAULT 0,
                    costo_material_base REAL DEFAULT 0,
                    costo_mano_obra_base REAL DEFAULT 0,
                    activo INTEGER DEFAULT 1,
                    notas TEXT
                )
            ''')

            # Tabla de proyectos grandes
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS proyectos (
                    id_proyecto INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_proyecto TEXT UNIQUE NOT NULL,
                    nombre_proyecto TEXT NOT NULL,
                    id_cliente INTEGER NOT NULL,
                    ubicacion TEXT,
                    descripcion TEXT,
                    fecha_inicio DATE,
                    fecha_fin_estimada DATE,
                    responsable TEXT,
                    estado TEXT DEFAULT 'en_planificacion',
                    subtotal_equipos REAL DEFAULT 0,
                    subtotal_materiales REAL DEFAULT 0,
                    subtotal_mano_obra REAL DEFAULT 0,
                    total_proyecto REAL DEFAULT 0,
                    notas TEXT,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
                )
            ''')

            # Tabla de niveles/áreas del proyecto
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS proyecto_niveles (
                    id_nivel INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_proyecto INTEGER NOT NULL,
                    codigo_nivel TEXT NOT NULL,
                    nombre_nivel TEXT NOT NULL,
                    orden INTEGER DEFAULT 0,
                    subtotal_equipos REAL DEFAULT 0,
                    subtotal_materiales REAL DEFAULT 0,
                    subtotal_mano_obra REAL DEFAULT 0,
                    total_nivel REAL DEFAULT 0,
                    notas TEXT,
                    FOREIGN KEY (id_proyecto) REFERENCES proyectos(id_proyecto) ON DELETE CASCADE,
                    UNIQUE(id_proyecto, codigo_nivel)
                )
            ''')

            # Tabla de items/especificaciones por nivel
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS proyecto_items (
                    id_item INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_nivel INTEGER NOT NULL,
                    especificacion TEXT NOT NULL,
                    descripcion TEXT,
                    id_componente_catalogo INTEGER,
                    cantidad REAL DEFAULT 1,
                    unidad TEXT DEFAULT 'unidad',
                    costo_equipo REAL DEFAULT 0,
                    costo_materiales REAL DEFAULT 0,
                    costo_mano_obra REAL DEFAULT 0,
                    total_item REAL DEFAULT 0,
                    orden INTEGER DEFAULT 0,
                    notas TEXT,
                    FOREIGN KEY (id_nivel) REFERENCES proyecto_niveles(id_nivel) ON DELETE CASCADE,
                    FOREIGN KEY (id_componente_catalogo) REFERENCES catalogo_hvac(id_componente)
                )
            ''')

            # Tabla de archivos vinculados al proyecto (planos AutoCAD, PDFs, etc.)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS proyecto_archivos (
                    id_archivo INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_proyecto INTEGER NOT NULL,
                    id_nivel INTEGER,
                    nombre_archivo TEXT NOT NULL,
                    ruta_archivo TEXT NOT NULL,
                    tipo_archivo TEXT,
                    descripcion TEXT,
                    fecha_agregado DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_proyecto) REFERENCES proyectos(id_proyecto) ON DELETE CASCADE,
                    FOREIGN KEY (id_nivel) REFERENCES proyecto_niveles(id_nivel) ON DELETE SET NULL
                )
            ''')

            self.conn.commit()
            print("[OK] Tablas creadas exitosamente")
            return True

        except sqlite3.Error as e:
            print(f"[ERROR] Error al crear tablas: {e}")
            return False

    def insertar_datos_iniciales(self):
        """Inserta configuración y usuario por defecto"""
        try:
            # Verificar si ya existen datos
            self.cursor.execute("SELECT COUNT(*) FROM usuarios")
            if self.cursor.fetchone()[0] > 0:
                print("[OK] Ya existen datos en la base de datos")
                return True

            # Usuario por defecto con bcrypt (seguro)
            # IMPORTANTE: Cambiar esta contraseña después de la primera instalación
            default_password = "A240133"  # Contraseña temporal - CAMBIAR EN PRODUCCIÓN
            password_hash = bcrypt.hashpw(default_password.encode('utf-8'), bcrypt.gensalt())

            self.cursor.execute('''
                INSERT INTO usuarios (nombre_usuario, password_hash, nombre_completo)
                VALUES (?, ?, ?)
            ''', ('Mcordero12', password_hash, 'Mauricio Cordero'))

            # Configuración por defecto
            configuraciones = [
                ('factor_venta', '1.5', 'Factor de venta sobre costos'),
                ('iva', '0.13', 'Porcentaje de IVA (13%)'),
                ('tipo_cambio', '515', 'Tipo de cambio colones/dólar'),
                ('costo_hora_tecnico', '15', 'Costo por hora de técnico en dólares'),
                ('nombre_empresa', 'AirSolutions', 'Nombre de la empresa'),
                ('telefono_empresa', '', 'Teléfono de contacto'),
                ('email_empresa', '', 'Email de contacto'),
                ('direccion_empresa', '', 'Dirección de la empresa')
            ]

            self.cursor.executemany('''
                INSERT INTO configuracion (clave, valor, descripcion)
                VALUES (?, ?, ?)
            ''', configuraciones)

            self.conn.commit()
            print("[OK] Datos iniciales insertados")
            print("  Usuario: admin")
            print("  Contraseña: admin123")
            return True

        except sqlite3.Error as e:
            print(f"[ERROR] Error al insertar datos iniciales: {e}")
            return False

    def inicializar(self):
        """Inicializa completamente la base de datos"""
        if self.conectar():
            if self.crear_tablas():
                self.insertar_datos_iniciales()
                return True
        return False

    # --- MÉTODOS DE CONSULTA Y MANIPULACIÓN ---

    def verificar_login(self, usuario, password):
        """
        Verifica credenciales de usuario usando bcrypt

        Args:
            usuario (str): Nombre de usuario
            password (str): Contraseña

        Returns:
            tuple: Datos del usuario si es válido, None si no
        """
        # Obtener hash almacenado
        self.cursor.execute('''
            SELECT id_usuario, nombre_usuario, nombre_completo, password_hash
            FROM usuarios
            WHERE nombre_usuario = ? AND activo = 1
        ''', (usuario,))

        resultado = self.cursor.fetchone()

        if resultado:
            stored_hash = resultado[3]
            # Verificar contraseña con bcrypt
            try:
                if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                    return (resultado[0], resultado[1], resultado[2])
            except:
                # Si falla (ej: hash antiguo), retornar None
                return None

        return None

    def obtener_configuracion(self, clave):
        """Obtiene un valor de configuración"""
        self.cursor.execute('SELECT valor FROM configuracion WHERE clave = ?', (clave,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def actualizar_configuracion(self, clave, valor):
        """Actualiza un valor de configuración"""
        self.cursor.execute('UPDATE configuracion SET valor = ? WHERE clave = ?', (valor, clave))
        self.conn.commit()

    def ejecutar_query(self, query, params=None):
        """Ejecuta una consulta SQL personalizada"""
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        self.conn.commit()
        return self.cursor


# Función auxiliar para inicializar la base de datos
def inicializar_base_datos():
    """Inicializa la base de datos si no existe"""
    db = DatabaseManager()
    exito = db.inicializar()
    db.desconectar()
    return exito


if __name__ == '__main__':
    # Si se ejecuta este archivo directamente, inicializa la BD
    print("="*60)
    print("INICIALIZANDO BASE DE DATOS - AIRSOLUTIONS")
    print("="*60)
    inicializar_base_datos()
