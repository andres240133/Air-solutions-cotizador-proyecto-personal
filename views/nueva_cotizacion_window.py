"""
nueva_cotizacion_window.py - Ventana para crear nueva cotizacion

Esta ventana permite:
1. Seleccionar cliente
2. Agregar equipos
3. Agregar materiales
4. Agregar gastos adicionales
5. Calcular totales automaticamente
6. Generar PDF
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.database import DatabaseManager


class NuevaCotizacionWindow:
    """Ventana modal para crear nueva cotizacion"""

    def __init__(self, parent, db=None, id_cliente_preseleccionado=None, id_proyecto=None, descripcion_proyecto=None):
        """
        Inicializa la ventana

        Args:
            parent: Ventana padre (MainWindow o dialog)
            db: DatabaseManager (opcional, si viene de proyecto)
            id_cliente_preseleccionado: ID del cliente a preseleccionar
            id_proyecto: ID del proyecto al que pertenece esta cotización
            descripcion_proyecto: Descripción del proyecto para mostrar
        """
        self.parent = parent
        self.id_proyecto = id_proyecto
        self.descripcion_proyecto = descripcion_proyecto

        # Detectar si parent tiene root o es un dialog
        if hasattr(parent, 'root'):
            parent_window = parent.root
        else:
            parent_window = parent

        self.dialog = tk.Toplevel(parent_window)
        self.dialog.title("Nueva Cotización - AirSolutions")
        self.dialog.geometry("1000x700")
        self.dialog.resizable(True, True)

        # Para compatibilidad con código antiguo
        self.window = self.dialog

        # Centrar ventana
        self.centrar_ventana()

        # Hacer modal (bloquea la ventana padre)
        self.dialog.transient(parent_window)
        self.dialog.grab_set()

        # Base de datos
        if db:
            self.db = db
        else:
            self.db = DatabaseManager()
            self.db.conectar()

        self.id_cliente_preseleccionado = id_cliente_preseleccionado

        # Variables
        self.cliente_seleccionado = None
        self.equipos_agregados = []
        self.materiales_agregados = []
        self.gastos_agregados = []
        self.ductos_agregados = []
        self.difusores_agregados = []
        self.rejillas_agregadas = []
        self.tuberias_agregadas = []
        self.mano_obra_agregada = []

        # Configuracion del sistema
        self.factor_venta = float(self.db.obtener_configuracion('factor_venta') or 1.5)
        self.iva = float(self.db.obtener_configuracion('iva') or 0.13)
        self.tipo_cambio = float(self.db.obtener_configuracion('tipo_cambio') or 515)
        self.costo_hora = float(self.db.obtener_configuracion('costo_hora_tecnico') or 15)

        # Crear interfaz
        self.crear_interfaz()

        # Cargar datos iniciales
        self.cargar_clientes()
        self.cargar_equipos_disponibles()
        self.cargar_materiales_disponibles()

    def centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        self.window.update_idletasks()
        width = 1000
        height = 700
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def crear_interfaz(self):
        """Crea todos los elementos de la interfaz"""

        # Frame principal con scroll
        main_container = tk.Frame(self.window, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True)

        # Header
        header = tk.Frame(main_container, bg='#2563eb', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Nueva Cotizacion",
            font=("Arial", 18, "bold"),
            bg='#2563eb',
            fg='white'
        ).pack(side=tk.LEFT, padx=20, pady=15)

        # Contenedor con scroll
        canvas = tk.Canvas(main_container, bg='white')
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Contenido
        content = tk.Frame(scrollable_frame, bg='white')
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        # Seccion 1: Informacion General
        self.crear_seccion_info_general(content)

        # Seccion 2: Equipos
        self.crear_seccion_equipos(content)

        # Seccion 3: Ductos
        self.crear_seccion_ductos(content)

        # Seccion 4: Difusores
        self.crear_seccion_difusores(content)

        # Seccion 5: Rejillas
        self.crear_seccion_rejillas(content)

        # Seccion 6: Tuberias
        self.crear_seccion_tuberias(content)

        # Seccion 7: Mano de Obra
        self.crear_seccion_mano_obra(content)

        # Seccion 8: Materiales
        self.crear_seccion_materiales(content)

        # Seccion 9: Gastos Adicionales
        self.crear_seccion_gastos(content)

        # Seccion 10: Totales
        self.crear_seccion_totales(content)

        # Botones finales
        self.crear_botones_finales(content)

    def crear_seccion_info_general(self, parent):
        """Seccion de informacion general"""
        frame = tk.LabelFrame(
            parent,
            text="Informacion General",
            font=("Arial", 12, "bold"),
            bg='white',
            padx=20,
            pady=15
        )
        frame.pack(fill=tk.X, pady=(0, 20))

        # Fila 1: Cliente y Fecha
        row1 = tk.Frame(frame, bg='white')
        row1.pack(fill=tk.X, pady=5)

        # Cliente
        tk.Label(row1, text="Cliente:", font=("Arial", 10), bg='white').pack(side=tk.LEFT, padx=(0, 10))

        self.combo_cliente = ttk.Combobox(row1, width=40, state='readonly')
        self.combo_cliente.pack(side=tk.LEFT, padx=(0, 20))

        tk.Button(
            row1,
            text="Nuevo Cliente",
            bg='#10b981',
            fg='white',
            relief=tk.FLAT,
            padx=15,
            command=self.nuevo_cliente
        ).pack(side=tk.LEFT)

        # Fecha
        tk.Label(row1, text="Fecha:", font=("Arial", 10), bg='white').pack(side=tk.LEFT, padx=(30, 10))

        self.fecha_actual = datetime.now().strftime("%Y-%m-%d")
        tk.Label(row1, text=self.fecha_actual, font=("Arial", 10, "bold"), bg='white').pack(side=tk.LEFT)

        # Fila 2: Tipo de servicio y Visitas
        row2 = tk.Frame(frame, bg='white')
        row2.pack(fill=tk.X, pady=10)

        tk.Label(row2, text="Tipo de Servicio:", font=("Arial", 10), bg='white').pack(side=tk.LEFT, padx=(0, 10))

        self.tipo_servicio_var = tk.StringVar(value="Mantenimiento")
        tipos = ["Mantenimiento", "Instalacion", "Reparacion", "Otro"]
        self.combo_tipo_servicio = ttk.Combobox(row2, textvariable=self.tipo_servicio_var, values=tipos, width=20)
        self.combo_tipo_servicio.pack(side=tk.LEFT, padx=(0, 30))

        tk.Label(row2, text="Visitas Anuales:", font=("Arial", 10), bg='white').pack(side=tk.LEFT, padx=(0, 10))

        self.visitas_var = tk.StringVar(value="1")
        tk.Spinbox(row2, from_=1, to=12, textvariable=self.visitas_var, width=10).pack(side=tk.LEFT)

    def crear_seccion_equipos(self, parent):
        """Seccion de equipos HVAC"""
        frame = tk.LabelFrame(
            parent,
            text="Equipos",
            font=("Arial", 12, "bold"),
            bg='white',
            padx=20,
            pady=15
        )
        frame.pack(fill=tk.X, pady=(0, 20))

        # Controles para agregar equipo
        control_frame = tk.Frame(frame, bg='white')
        control_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(control_frame, text="Equipo:", font=("Arial", 10), bg='white').pack(side=tk.LEFT, padx=(0, 10))

        self.combo_equipo = ttk.Combobox(control_frame, width=40, state='readonly')
        self.combo_equipo.pack(side=tk.LEFT, padx=(0, 10))

        tk.Label(control_frame, text="Cantidad:", font=("Arial", 10), bg='white').pack(side=tk.LEFT, padx=(0, 10))

        self.cantidad_equipo_var = tk.StringVar(value="1")
        tk.Spinbox(control_frame, from_=1, to=100, textvariable=self.cantidad_equipo_var, width=10).pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(
            control_frame,
            text="Agregar Equipo",
            bg='#2563eb',
            fg='white',
            relief=tk.FLAT,
            padx=15,
            command=self.agregar_equipo
        ).pack(side=tk.LEFT)

        # Tabla de equipos agregados
        self.tree_equipos = ttk.Treeview(
            frame,
            columns=('Equipo', 'Cantidad', 'Horas', 'Subtotal'),
            show='headings',
            height=5
        )
        self.tree_equipos.heading('Equipo', text='Equipo')
        self.tree_equipos.heading('Cantidad', text='Cantidad')
        self.tree_equipos.heading('Horas', text='Horas')
        self.tree_equipos.heading('Subtotal', text='Subtotal')

        self.tree_equipos.column('Equipo', width=400)
        self.tree_equipos.column('Cantidad', width=80)
        self.tree_equipos.column('Horas', width=80)
        self.tree_equipos.column('Subtotal', width=100)

        self.tree_equipos.pack(fill=tk.X)

        # Boton eliminar
        tk.Button(
            frame,
            text="Eliminar Seleccionado",
            bg='#ef4444',
            fg='white',
            relief=tk.FLAT,
            padx=15,
            command=lambda: self.eliminar_item(self.tree_equipos, self.equipos_agregados)
        ).pack(anchor=tk.E, pady=(5, 0))

    def crear_seccion_ductos(self, parent):
        """Seccion de ductos"""
        frame = tk.LabelFrame(
            parent,
            text="Ductos",
            font=("Arial", 12, "bold"),
            bg='white',
            padx=20,
            pady=15
        )
        frame.pack(fill=tk.X, pady=(0, 20))

        # Controles
        control_frame = tk.Frame(frame, bg='white')
        control_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(control_frame, text="Tipo:", font=("Arial", 10), bg='white').grid(row=0, column=0, padx=(0, 10), sticky=tk.W)
        self.tipo_ducto_var = tk.StringVar()
        tipo_combo = ttk.Combobox(
            control_frame,
            textvariable=self.tipo_ducto_var,
            values=['Fibra Vidrio', 'Lamina Galvanizada', 'Flexible'],
            width=25,
            state='readonly'
        )
        tipo_combo.grid(row=0, column=1, padx=(0, 20), sticky=tk.W)
        tipo_combo.current(0)

        tk.Label(control_frame, text="Largo Suministro (m):", font=("Arial", 10), bg='white').grid(row=0, column=2, padx=(0, 10), sticky=tk.W)
        self.largo_suministro_var = tk.StringVar(value="0")
        tk.Entry(control_frame, textvariable=self.largo_suministro_var, width=10).grid(row=0, column=3, padx=(0, 20))

        tk.Label(control_frame, text="Largo Retorno (m):", font=("Arial", 10), bg='white').grid(row=1, column=0, padx=(0, 10), pady=(10, 0), sticky=tk.W)
        self.largo_retorno_var = tk.StringVar(value="0")
        tk.Entry(control_frame, textvariable=self.largo_retorno_var, width=10).grid(row=1, column=1, padx=(0, 20), pady=(10, 0), sticky=tk.W)

        tk.Label(control_frame, text="Precio/metro:", font=("Arial", 10), bg='white').grid(row=1, column=2, padx=(0, 10), pady=(10, 0), sticky=tk.W)
        self.precio_ducto_var = tk.StringVar(value="0")
        tk.Entry(control_frame, textvariable=self.precio_ducto_var, width=10).grid(row=1, column=3, padx=(0, 20), pady=(10, 0))

        tk.Button(
            control_frame,
            text="Agregar Ducto",
            bg='#2563eb',
            fg='white',
            relief=tk.FLAT,
            padx=15,
            command=self.agregar_ducto
        ).grid(row=1, column=4, pady=(10, 0))

        # Tabla
        self.tree_ductos = ttk.Treeview(
            frame,
            columns=('Tipo', 'Largo Sum', 'Largo Ret', 'Precio/m', 'Subtotal'),
            show='headings',
            height=4
        )
        self.tree_ductos.heading('Tipo', text='Tipo Ducto')
        self.tree_ductos.heading('Largo Sum', text='Largo Sum (m)')
        self.tree_ductos.heading('Largo Ret', text='Largo Ret (m)')
        self.tree_ductos.heading('Precio/m', text='Precio/metro')
        self.tree_ductos.heading('Subtotal', text='Subtotal')

        self.tree_ductos.column('Tipo', width=150)
        self.tree_ductos.column('Largo Sum', width=100)
        self.tree_ductos.column('Largo Ret', width=100)
        self.tree_ductos.column('Precio/m', width=100)
        self.tree_ductos.column('Subtotal', width=100)

        self.tree_ductos.pack(fill=tk.X, pady=(10, 0))

        tk.Button(
            frame,
            text="Eliminar Seleccionado",
            bg='#ef4444',
            fg='white',
            relief=tk.FLAT,
            padx=15,
            command=lambda: self.eliminar_item(self.tree_ductos, self.ductos_agregados)
        ).pack(anchor=tk.E, pady=(5, 0))

    def crear_seccion_difusores(self, parent):
        """Seccion de difusores"""
        frame = tk.LabelFrame(
            parent,
            text="Difusores",
            font=("Arial", 12, "bold"),
            bg='white',
            padx=20,
            pady=15
        )
        frame.pack(fill=tk.X, pady=(0, 20))

        # Controles
        control_frame = tk.Frame(frame, bg='white')
        control_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(control_frame, text="Tipo:", font=("Arial", 10), bg='white').pack(side=tk.LEFT, padx=(0, 10))
        self.tipo_difusor_var = tk.StringVar()
        tipo_combo = ttk.Combobox(
            control_frame,
            textvariable=self.tipo_difusor_var,
            values=['JS-OB', 'AVP-OB', 'LD SIN DAMPER', 'ASD SIN DAMPER', 'Otros'],
            width=20,
            state='readonly'
        )
        tipo_combo.pack(side=tk.LEFT, padx=(0, 20))
        tipo_combo.current(0)

        tk.Label(control_frame, text="Cantidad:", font=("Arial", 10), bg='white').pack(side=tk.LEFT, padx=(0, 10))
        self.cantidad_difusor_var = tk.StringVar(value="1")
        tk.Entry(control_frame, textvariable=self.cantidad_difusor_var, width=10).pack(side=tk.LEFT, padx=(0, 20))

        tk.Label(control_frame, text="Precio Unitario:", font=("Arial", 10), bg='white').pack(side=tk.LEFT, padx=(0, 10))
        self.precio_difusor_var = tk.StringVar(value="0")
        tk.Entry(control_frame, textvariable=self.precio_difusor_var, width=10).pack(side=tk.LEFT, padx=(0, 20))

        tk.Button(
            control_frame,
            text="Agregar Difusor",
            bg='#2563eb',
            fg='white',
            relief=tk.FLAT,
            padx=15,
            command=self.agregar_difusor
        ).pack(side=tk.LEFT)

        # Tabla
        self.tree_difusores = ttk.Treeview(
            frame,
            columns=('Tipo', 'Cantidad', 'Precio Unit', 'Subtotal'),
            show='headings',
            height=4
        )
        self.tree_difusores.heading('Tipo', text='Tipo Difusor')
        self.tree_difusores.heading('Cantidad', text='Cantidad')
        self.tree_difusores.heading('Precio Unit', text='Precio Unitario')
        self.tree_difusores.heading('Subtotal', text='Subtotal')

        self.tree_difusores.pack(fill=tk.X, pady=(10, 0))

        tk.Button(
            frame,
            text="Eliminar Seleccionado",
            bg='#ef4444',
            fg='white',
            relief=tk.FLAT,
            padx=15,
            command=lambda: self.eliminar_item(self.tree_difusores, self.difusores_agregados)
        ).pack(anchor=tk.E, pady=(5, 0))

    def crear_seccion_rejillas(self, parent):
        """Seccion de rejillas"""
        frame = tk.LabelFrame(
            parent,
            text="Rejillas",
            font=("Arial", 12, "bold"),
            bg='white',
            padx=20,
            pady=15
        )
        frame.pack(fill=tk.X, pady=(0, 20))

        # Controles
        control_frame = tk.Frame(frame, bg='white')
        control_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(control_frame, text="Tipo:", font=("Arial", 10), bg='white').pack(side=tk.LEFT, padx=(0, 10))
        self.tipo_rejilla_var = tk.StringVar()
        tipo_combo = ttk.Combobox(
            control_frame,
            textvariable=self.tipo_rejilla_var,
            values=['VH-OB (suministro)', 'RA (retorno)', 'LD SIN DAMPER (retorno)', 'ASD SIN DAMPER (retorno)', 'Otros'],
            width=25,
            state='readonly'
        )
        tipo_combo.pack(side=tk.LEFT, padx=(0, 20))
        tipo_combo.current(0)

        tk.Label(control_frame, text="Cantidad:", font=("Arial", 10), bg='white').pack(side=tk.LEFT, padx=(0, 10))
        self.cantidad_rejilla_var = tk.StringVar(value="1")
        tk.Entry(control_frame, textvariable=self.cantidad_rejilla_var, width=10).pack(side=tk.LEFT, padx=(0, 20))

        tk.Label(control_frame, text="Precio Unitario:", font=("Arial", 10), bg='white').pack(side=tk.LEFT, padx=(0, 10))
        self.precio_rejilla_var = tk.StringVar(value="0")
        tk.Entry(control_frame, textvariable=self.precio_rejilla_var, width=10).pack(side=tk.LEFT, padx=(0, 20))

        tk.Button(
            control_frame,
            text="Agregar Rejilla",
            bg='#2563eb',
            fg='white',
            relief=tk.FLAT,
            padx=15,
            command=self.agregar_rejilla
        ).pack(side=tk.LEFT)

        # Tabla
        self.tree_rejillas = ttk.Treeview(
            frame,
            columns=('Tipo', 'Cantidad', 'Precio Unit', 'Subtotal'),
            show='headings',
            height=4
        )
        self.tree_rejillas.heading('Tipo', text='Tipo Rejilla')
        self.tree_rejillas.heading('Cantidad', text='Cantidad')
        self.tree_rejillas.heading('Precio Unit', text='Precio Unitario')
        self.tree_rejillas.heading('Subtotal', text='Subtotal')

        self.tree_rejillas.pack(fill=tk.X, pady=(10, 0))

        tk.Button(
            frame,
            text="Eliminar Seleccionado",
            bg='#ef4444',
            fg='white',
            relief=tk.FLAT,
            padx=15,
            command=lambda: self.eliminar_item(self.tree_rejillas, self.rejillas_agregadas)
        ).pack(anchor=tk.E, pady=(5, 0))

    def crear_seccion_tuberias(self, parent):
        """Seccion de tuberias"""
        frame = tk.LabelFrame(
            parent,
            text="Tuberias",
            font=("Arial", 12, "bold"),
            bg='white',
            padx=20,
            pady=15
        )
        frame.pack(fill=tk.X, pady=(0, 20))

        # Controles
        control_frame = tk.Frame(frame, bg='white')
        control_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(control_frame, text="Tipo:", font=("Arial", 10), bg='white').pack(side=tk.LEFT, padx=(0, 10))
        self.tipo_tuberia_var = tk.StringVar()
        tipo_combo = ttk.Combobox(
            control_frame,
            textvariable=self.tipo_tuberia_var,
            values=['Refrigeracion (evap-cond)', 'Agua (Surfasyl)', 'Drenaje (3/4)'],
            width=25,
            state='readonly'
        )
        tipo_combo.pack(side=tk.LEFT, padx=(0, 20))
        tipo_combo.current(0)

        tk.Label(control_frame, text="Largo (m):", font=("Arial", 10), bg='white').pack(side=tk.LEFT, padx=(0, 10))
        self.largo_tuberia_var = tk.StringVar(value="0")
        tk.Entry(control_frame, textvariable=self.largo_tuberia_var, width=10).pack(side=tk.LEFT, padx=(0, 20))

        tk.Label(control_frame, text="Precio/metro:", font=("Arial", 10), bg='white').pack(side=tk.LEFT, padx=(0, 10))
        self.precio_tuberia_var = tk.StringVar(value="0")
        tk.Entry(control_frame, textvariable=self.precio_tuberia_var, width=10).pack(side=tk.LEFT, padx=(0, 20))

        tk.Button(
            control_frame,
            text="Agregar Tuberia",
            bg='#2563eb',
            fg='white',
            relief=tk.FLAT,
            padx=15,
            command=self.agregar_tuberia
        ).pack(side=tk.LEFT)

        # Tabla
        self.tree_tuberias = ttk.Treeview(
            frame,
            columns=('Tipo', 'Largo (m)', 'Precio/m', 'Subtotal'),
            show='headings',
            height=4
        )
        self.tree_tuberias.heading('Tipo', text='Tipo Tuberia')
        self.tree_tuberias.heading('Largo (m)', text='Largo (m)')
        self.tree_tuberias.heading('Precio/m', text='Precio/metro')
        self.tree_tuberias.heading('Subtotal', text='Subtotal')

        self.tree_tuberias.pack(fill=tk.X, pady=(10, 0))

        tk.Button(
            frame,
            text="Eliminar Seleccionado",
            bg='#ef4444',
            fg='white',
            relief=tk.FLAT,
            padx=15,
            command=lambda: self.eliminar_item(self.tree_tuberias, self.tuberias_agregadas)
        ).pack(anchor=tk.E, pady=(5, 0))

    def crear_seccion_mano_obra(self, parent):
        """Seccion de mano de obra"""
        frame = tk.LabelFrame(
            parent,
            text="Mano de Obra",
            font=("Arial", 12, "bold"),
            bg='white',
            padx=20,
            pady=15
        )
        frame.pack(fill=tk.X, pady=(0, 20))

        # Controles
        control_frame = tk.Frame(frame, bg='white')
        control_frame.pack(fill=tk.X, pady=(0, 10))

        # Fila 0: Tipo y Descripción
        tk.Label(control_frame, text="Tipo:", font=("Arial", 10), bg='white').grid(row=0, column=0, padx=(0, 10), sticky=tk.W)
        self.tipo_mano_obra_var = tk.StringVar()
        tipo_combo = ttk.Combobox(
            control_frame,
            textvariable=self.tipo_mano_obra_var,
            values=['Técnicos', 'Contratistas'],
            width=15,
            state='readonly'
        )
        tipo_combo.grid(row=0, column=1, padx=(0, 20), sticky=tk.W)
        tipo_combo.current(0)

        tk.Label(control_frame, text="Descripcion:", font=("Arial", 10), bg='white').grid(row=0, column=2, padx=(0, 10), sticky=tk.W)
        self.desc_mano_obra_var = tk.StringVar()
        desc_combo = ttk.Combobox(
            control_frame,
            textvariable=self.desc_mano_obra_var,
            values=['Paquete hasta 10 TR', 'Paquete hasta 20 TR', 'Instalacion Fibra Vidrio', 'Instalacion Rejillas', 'Instalacion Drenaje', 'Otros'],
            width=30,
            state='readonly'
        )
        desc_combo.grid(row=0, column=3, padx=(0, 20), sticky=tk.W)
        desc_combo.current(0)

        # Fila 1: Cantidad/Horas y Precio Unitario
        tk.Label(control_frame, text="Cantidad/Horas:", font=("Arial", 10), bg='white').grid(row=1, column=0, padx=(0, 10), pady=(10, 0), sticky=tk.W)
        self.cantidad_mano_obra_var = tk.StringVar(value="1")
        tk.Entry(control_frame, textvariable=self.cantidad_mano_obra_var, width=10).grid(row=1, column=1, padx=(0, 20), pady=(10, 0), sticky=tk.W)

        tk.Label(control_frame, text="Precio Unitario:", font=("Arial", 10), bg='white').grid(row=1, column=2, padx=(0, 10), pady=(10, 0), sticky=tk.W)
        self.precio_mano_obra_var = tk.StringVar(value="0")
        tk.Entry(control_frame, textvariable=self.precio_mano_obra_var, width=10).grid(row=1, column=3, padx=(0, 20), pady=(10, 0), sticky=tk.W)

        tk.Button(
            control_frame,
            text="Agregar Mano de Obra",
            bg='#2563eb',
            fg='white',
            relief=tk.FLAT,
            padx=15,
            command=self.agregar_mano_obra
        ).grid(row=2, column=1, columnspan=2, pady=(10, 0))

        # Tabla
        self.tree_mano_obra = ttk.Treeview(
            frame,
            columns=('Tipo', 'Descripcion', 'Cantidad', 'Precio Unit', 'Subtotal'),
            show='headings',
            height=4
        )
        self.tree_mano_obra.heading('Tipo', text='Tipo')
        self.tree_mano_obra.heading('Descripcion', text='Descripcion')
        self.tree_mano_obra.heading('Cantidad', text='Cantidad/Horas')
        self.tree_mano_obra.heading('Precio Unit', text='Precio Unitario')
        self.tree_mano_obra.heading('Subtotal', text='Subtotal')

        self.tree_mano_obra.column('Tipo', width=100)
        self.tree_mano_obra.column('Descripcion', width=250)

        self.tree_mano_obra.pack(fill=tk.X, pady=(10, 0))

        tk.Button(
            frame,
            text="Eliminar Seleccionado",
            bg='#ef4444',
            fg='white',
            relief=tk.FLAT,
            padx=15,
            command=lambda: self.eliminar_item(self.tree_mano_obra, self.mano_obra_agregada)
        ).pack(anchor=tk.E, pady=(5, 0))

    def crear_seccion_materiales(self, parent):
        """Seccion de materiales"""
        frame = tk.LabelFrame(
            parent,
            text="Materiales y Repuestos",
            font=("Arial", 12, "bold"),
            bg='white',
            padx=20,
            pady=15
        )
        frame.pack(fill=tk.X, pady=(0, 20))

        # Controles
        control_frame = tk.Frame(frame, bg='white')
        control_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(control_frame, text="Material:", font=("Arial", 10), bg='white').pack(side=tk.LEFT, padx=(0, 10))

        self.combo_material = ttk.Combobox(control_frame, width=40, state='readonly')
        self.combo_material.pack(side=tk.LEFT, padx=(0, 10))

        tk.Label(control_frame, text="Cantidad:", font=("Arial", 10), bg='white').pack(side=tk.LEFT, padx=(0, 10))

        self.cantidad_material_var = tk.StringVar(value="1")
        tk.Entry(control_frame, textvariable=self.cantidad_material_var, width=10).pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(
            control_frame,
            text="Agregar Material",
            bg='#2563eb',
            fg='white',
            relief=tk.FLAT,
            padx=15,
            command=self.agregar_material
        ).pack(side=tk.LEFT)

        # Tabla
        self.tree_materiales = ttk.Treeview(
            frame,
            columns=('Material', 'Cantidad', 'Precio Unit', 'Subtotal'),
            show='headings',
            height=5
        )
        self.tree_materiales.heading('Material', text='Material')
        self.tree_materiales.heading('Cantidad', text='Cantidad')
        self.tree_materiales.heading('Precio Unit', text='Precio Unit')
        self.tree_materiales.heading('Subtotal', text='Subtotal')

        self.tree_materiales.pack(fill=tk.X)

        tk.Button(
            frame,
            text="Eliminar Seleccionado",
            bg='#ef4444',
            fg='white',
            relief=tk.FLAT,
            padx=15,
            command=lambda: self.eliminar_item(self.tree_materiales, self.materiales_agregados)
        ).pack(anchor=tk.E, pady=(5, 0))

    def crear_seccion_gastos(self, parent):
        """Seccion de gastos adicionales"""
        frame = tk.LabelFrame(
            parent,
            text="Gastos Adicionales (Viaticos, Transporte, etc)",
            font=("Arial", 12, "bold"),
            bg='white',
            padx=20,
            pady=15
        )
        frame.pack(fill=tk.X, pady=(0, 20))

        # Controles
        control_frame = tk.Frame(frame, bg='white')
        control_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(control_frame, text="Concepto:", font=("Arial", 10), bg='white').pack(side=tk.LEFT, padx=(0, 10))

        self.concepto_gasto_var = tk.StringVar()
        tk.Entry(control_frame, textvariable=self.concepto_gasto_var, width=30).pack(side=tk.LEFT, padx=(0, 10))

        tk.Label(control_frame, text="Monto ($):", font=("Arial", 10), bg='white').pack(side=tk.LEFT, padx=(0, 10))

        self.monto_gasto_var = tk.StringVar()
        tk.Entry(control_frame, textvariable=self.monto_gasto_var, width=15).pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(
            control_frame,
            text="Agregar Gasto",
            bg='#2563eb',
            fg='white',
            relief=tk.FLAT,
            padx=15,
            command=self.agregar_gasto
        ).pack(side=tk.LEFT)

        # Tabla
        self.tree_gastos = ttk.Treeview(
            frame,
            columns=('Concepto', 'Monto'),
            show='headings',
            height=3
        )
        self.tree_gastos.heading('Concepto', text='Concepto')
        self.tree_gastos.heading('Monto', text='Monto')

        self.tree_gastos.pack(fill=tk.X)

        tk.Button(
            frame,
            text="Eliminar Seleccionado",
            bg='#ef4444',
            fg='white',
            relief=tk.FLAT,
            padx=15,
            command=lambda: self.eliminar_item(self.tree_gastos, self.gastos_agregados)
        ).pack(anchor=tk.E, pady=(5, 0))

    def crear_seccion_totales(self, parent):
        """Seccion de totales calculados"""
        frame = tk.LabelFrame(
            parent,
            text="Totales",
            font=("Arial", 12, "bold"),
            bg='white',
            padx=20,
            pady=15
        )
        frame.pack(fill=tk.X, pady=(0, 20))

        # Labels para mostrar totales
        self.label_total_equipos = tk.Label(frame, text="Total Equipos: $0.00", font=("Arial", 11), bg='white')
        self.label_total_equipos.pack(anchor=tk.W, pady=3)

        self.label_total_ductos = tk.Label(frame, text="Total Ductos: $0.00", font=("Arial", 11), bg='white')
        self.label_total_ductos.pack(anchor=tk.W, pady=3)

        self.label_total_difusores = tk.Label(frame, text="Total Difusores: $0.00", font=("Arial", 11), bg='white')
        self.label_total_difusores.pack(anchor=tk.W, pady=3)

        self.label_total_rejillas = tk.Label(frame, text="Total Rejillas: $0.00", font=("Arial", 11), bg='white')
        self.label_total_rejillas.pack(anchor=tk.W, pady=3)

        self.label_total_tuberias = tk.Label(frame, text="Total Tuberias: $0.00", font=("Arial", 11), bg='white')
        self.label_total_tuberias.pack(anchor=tk.W, pady=3)

        self.label_total_mano_obra = tk.Label(frame, text="Total Mano de Obra: $0.00", font=("Arial", 11), bg='white')
        self.label_total_mano_obra.pack(anchor=tk.W, pady=3)

        self.label_total_materiales = tk.Label(frame, text="Total Materiales: $0.00", font=("Arial", 11), bg='white')
        self.label_total_materiales.pack(anchor=tk.W, pady=3)

        self.label_total_gastos = tk.Label(frame, text="Total Gastos: $0.00", font=("Arial", 11), bg='white')
        self.label_total_gastos.pack(anchor=tk.W, pady=3)

        # Separador
        tk.Frame(frame, height=2, bg='#e5e7eb').pack(fill=tk.X, pady=10)

        self.label_subtotal = tk.Label(frame, text="Subtotal: $0.00", font=("Arial", 11, "bold"), bg='white')
        self.label_subtotal.pack(anchor=tk.W, pady=3)

        # Checkbox para INS y CCSS
        self.incluir_ins_ccss_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            frame,
            text="Incluir INS y CCSS (aprox. 35%)",
            variable=self.incluir_ins_ccss_var,
            font=("Arial", 10),
            bg='white',
            command=self.calcular_totales
        ).pack(anchor=tk.W, pady=5)

        self.label_ins_ccss = tk.Label(frame, text="INS y CCSS: $0.00", font=("Arial", 11), bg='white', fg='#6b7280')
        self.label_ins_ccss.pack(anchor=tk.W, pady=3)

        # Configuración de IVA
        iva_frame = tk.Frame(frame, bg='white')
        iva_frame.pack(anchor=tk.W, pady=5, fill=tk.X)

        tk.Label(
            iva_frame,
            text="IVA:",
            font=("Arial", 10, "bold"),
            bg='white'
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.iva_var = tk.StringVar(value="13%")
        iva_opciones = ["0%", "1%", "2%", "4%", "8%", "13%", "Otro"]

        self.combo_iva = ttk.Combobox(
            iva_frame,
            textvariable=self.iva_var,
            values=iva_opciones,
            width=10,
            state='readonly'
        )
        self.combo_iva.pack(side=tk.LEFT, padx=(0, 10))
        self.combo_iva.bind('<<ComboboxSelected>>', lambda e: self.cambiar_iva())

        # Entry para IVA personalizado (inicialmente oculto)
        self.entry_iva_custom = tk.Entry(
            iva_frame,
            font=("Arial", 10),
            width=8
        )
        self.entry_iva_custom_visible = False

        self.label_iva = tk.Label(frame, text="IVA (13%): $0.00", font=("Arial", 11), bg='white')
        self.label_iva.pack(anchor=tk.W, pady=3)

        # Opción de mostrar en colones
        moneda_frame = tk.Frame(frame, bg='white')
        moneda_frame.pack(anchor=tk.W, pady=5, fill=tk.X)

        self.mostrar_colones_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            moneda_frame,
            text="Mostrar totales en Colones (₡)",
            variable=self.mostrar_colones_var,
            font=("Arial", 10),
            bg='white',
            command=self.calcular_totales
        ).pack(side=tk.LEFT)

        # Label para mostrar tipo de cambio
        tipo_cambio = self.db.obtener_configuracion('tipo_cambio') or '515'
        self.label_tipo_cambio = tk.Label(
            moneda_frame,
            text=f"(Tipo cambio: ₡{tipo_cambio})",
            font=("Arial", 9),
            bg='white',
            fg='#666'
        )
        self.label_tipo_cambio.pack(side=tk.LEFT, padx=10)

        self.label_total = tk.Label(frame, text="TOTAL: $0.00", font=("Arial", 14, "bold"), bg='white', fg='#2563eb')
        self.label_total.pack(anchor=tk.W, pady=5)

        # Boton calcular
        tk.Button(
            frame,
            text="Calcular Totales",
            bg='#10b981',
            fg='white',
            relief=tk.FLAT,
            font=("Arial", 11, "bold"),
            padx=30,
            pady=10,
            command=self.calcular_totales
        ).pack(anchor=tk.E, pady=(10, 0))

    def crear_botones_finales(self, parent):
        """Botones de guardar y cancelar"""
        frame = tk.Frame(parent, bg='white')
        frame.pack(fill=tk.X, pady=20)

        tk.Button(
            frame,
            text="Guardar Cotizacion",
            bg='#2563eb',
            fg='white',
            relief=tk.FLAT,
            font=("Arial", 12, "bold"),
            padx=40,
            pady=12,
            command=self.guardar_cotizacion
        ).pack(side=tk.RIGHT, padx=5)

        tk.Button(
            frame,
            text="Cancelar",
            bg='#64748b',
            fg='white',
            relief=tk.FLAT,
            font=("Arial", 12),
            padx=40,
            pady=12,
            command=self.cancelar
        ).pack(side=tk.RIGHT, padx=5)

    # Metodos de carga de datos
    def cargar_clientes(self):
        """Carga clientes desde la base de datos"""
        try:
            query = "SELECT id_cliente, nombre_empresa FROM clientes WHERE activo = 1 ORDER BY nombre_empresa"
            result = self.db.ejecutar_query(query)

            clientes = result.fetchall()
            self.clientes_dict = {f"{c[1]}": c[0] for c in clientes}

            if not clientes:
                self.combo_cliente['values'] = ["(No hay clientes registrados)"]
            else:
                self.combo_cliente['values'] = list(self.clientes_dict.keys())

        except Exception as e:
            print(f"Error al cargar clientes: {e}")

    def cargar_equipos_disponibles(self):
        """Carga equipos desde la base de datos"""
        try:
            query = "SELECT id_equipo, tipo_equipo, horas_mantenimiento FROM productos_equipos WHERE activo = 1 ORDER BY tipo_equipo"
            result = self.db.ejecutar_query(query)

            equipos = result.fetchall()
            self.equipos_dict = {f"{e[1]}": {'id': e[0], 'horas': e[2]} for e in equipos}
            self.combo_equipo['values'] = list(self.equipos_dict.keys())

        except Exception as e:
            print(f"Error al cargar equipos: {e}")

    def cargar_materiales_disponibles(self):
        """Carga materiales desde la base de datos"""
        try:
            query = "SELECT id_material, nombre_material, precio_unitario FROM materiales_repuestos WHERE activo = 1 ORDER BY nombre_material"
            result = self.db.ejecutar_query(query)

            materiales = result.fetchall()
            self.materiales_dict = {f"{m[1]}": {'id': m[0], 'precio': m[2]} for m in materiales}
            self.combo_material['values'] = list(self.materiales_dict.keys())

        except Exception as e:
            print(f"Error al cargar materiales: {e}")

    # Metodos de agregar items
    def agregar_equipo(self):
        """Agrega un equipo a la cotizacion"""
        equipo_nombre = self.combo_equipo.get()
        if not equipo_nombre or equipo_nombre not in self.equipos_dict:
            messagebox.showwarning("Advertencia", "Selecciona un equipo")
            return

        try:
            cantidad = int(self.cantidad_equipo_var.get())
            if cantidad <= 0:
                raise ValueError()
        except:
            messagebox.showwarning("Advertencia", "La cantidad debe ser un numero positivo")
            return

        equipo_info = self.equipos_dict[equipo_nombre]
        horas_total = equipo_info['horas'] * cantidad
        subtotal = horas_total * self.costo_hora * self.factor_venta

        self.equipos_agregados.append({
            'id': equipo_info['id'],
            'nombre': equipo_nombre,
            'cantidad': cantidad,
            'horas': horas_total,
            'subtotal': subtotal
        })

        self.tree_equipos.insert('', 'end', values=(
            equipo_nombre,
            cantidad,
            f"{horas_total:.2f}h",
            f"${subtotal:.2f}"
        ))

        print(f"Equipo agregado: {equipo_nombre} x{cantidad}")

    def agregar_material(self):
        """Agrega un material a la cotizacion"""
        material_nombre = self.combo_material.get()
        if not material_nombre or material_nombre not in self.materiales_dict:
            messagebox.showwarning("Advertencia", "Selecciona un material")
            return

        try:
            cantidad = float(self.cantidad_material_var.get())
            if cantidad <= 0:
                raise ValueError()
        except:
            messagebox.showwarning("Advertencia", "La cantidad debe ser un numero positivo")
            return

        material_info = self.materiales_dict[material_nombre]
        precio_unit = material_info['precio']
        subtotal = cantidad * precio_unit

        self.materiales_agregados.append({
            'id': material_info['id'],
            'nombre': material_nombre,
            'cantidad': cantidad,
            'precio_unit': precio_unit,
            'subtotal': subtotal
        })

        self.tree_materiales.insert('', 'end', values=(
            material_nombre,
            cantidad,
            f"${precio_unit:.2f}",
            f"${subtotal:.2f}"
        ))

        print(f"Material agregado: {material_nombre} x{cantidad}")

    def agregar_gasto(self):
        """Agrega un gasto adicional"""
        concepto = self.concepto_gasto_var.get().strip()
        if not concepto:
            messagebox.showwarning("Advertencia", "Ingresa un concepto")
            return

        try:
            monto = float(self.monto_gasto_var.get())
            if monto <= 0:
                raise ValueError()
        except:
            messagebox.showwarning("Advertencia", "El monto debe ser un numero positivo")
            return

        self.gastos_agregados.append({
            'concepto': concepto,
            'monto': monto
        })

        self.tree_gastos.insert('', 'end', values=(concepto, f"${monto:.2f}"))

        self.concepto_gasto_var.set("")
        self.monto_gasto_var.set("")

        print(f"Gasto agregado: {concepto} - ${monto}")

    def agregar_ducto(self):
        """Agrega un ducto a la cotizacion"""
        tipo = self.tipo_ducto_var.get()
        if not tipo:
            messagebox.showwarning("Advertencia", "Selecciona un tipo de ducto")
            return

        try:
            largo_sum = float(self.largo_suministro_var.get())
            largo_ret = float(self.largo_retorno_var.get())
            precio_metro = float(self.precio_ducto_var.get())

            if largo_sum < 0 or largo_ret < 0 or precio_metro < 0:
                raise ValueError()
        except:
            messagebox.showwarning("Advertencia", "Los valores deben ser numeros positivos")
            return

        largo_total = largo_sum + largo_ret
        subtotal = largo_total * precio_metro

        self.ductos_agregados.append({
            'tipo': tipo,
            'largo_suministro': largo_sum,
            'largo_retorno': largo_ret,
            'precio_metro': precio_metro,
            'subtotal': subtotal
        })

        self.tree_ductos.insert('', 'end', values=(
            tipo,
            f"{largo_sum:.2f}",
            f"{largo_ret:.2f}",
            f"${precio_metro:.2f}",
            f"${subtotal:.2f}"
        ))

        print(f"Ducto agregado: {tipo} - {largo_total}m total")

    def agregar_difusor(self):
        """Agrega un difusor a la cotizacion"""
        tipo = self.tipo_difusor_var.get()
        if not tipo:
            messagebox.showwarning("Advertencia", "Selecciona un tipo de difusor")
            return

        try:
            cantidad = int(self.cantidad_difusor_var.get())
            precio_unit = float(self.precio_difusor_var.get())

            if cantidad <= 0 or precio_unit < 0:
                raise ValueError()
        except:
            messagebox.showwarning("Advertencia", "Valores invalidos")
            return

        subtotal = cantidad * precio_unit

        self.difusores_agregados.append({
            'tipo': tipo,
            'cantidad': cantidad,
            'precio_unit': precio_unit,
            'subtotal': subtotal
        })

        self.tree_difusores.insert('', 'end', values=(
            tipo,
            cantidad,
            f"${precio_unit:.2f}",
            f"${subtotal:.2f}"
        ))

        print(f"Difusor agregado: {tipo} x{cantidad}")

    def agregar_rejilla(self):
        """Agrega una rejilla a la cotizacion"""
        tipo = self.tipo_rejilla_var.get()
        if not tipo:
            messagebox.showwarning("Advertencia", "Selecciona un tipo de rejilla")
            return

        try:
            cantidad = int(self.cantidad_rejilla_var.get())
            precio_unit = float(self.precio_rejilla_var.get())

            if cantidad <= 0 or precio_unit < 0:
                raise ValueError()
        except:
            messagebox.showwarning("Advertencia", "Valores invalidos")
            return

        subtotal = cantidad * precio_unit

        self.rejillas_agregadas.append({
            'tipo': tipo,
            'cantidad': cantidad,
            'precio_unit': precio_unit,
            'subtotal': subtotal
        })

        self.tree_rejillas.insert('', 'end', values=(
            tipo,
            cantidad,
            f"${precio_unit:.2f}",
            f"${subtotal:.2f}"
        ))

        print(f"Rejilla agregada: {tipo} x{cantidad}")

    def agregar_tuberia(self):
        """Agrega una tuberia a la cotizacion"""
        tipo = self.tipo_tuberia_var.get()
        if not tipo:
            messagebox.showwarning("Advertencia", "Selecciona un tipo de tuberia")
            return

        try:
            largo = float(self.largo_tuberia_var.get())
            precio_metro = float(self.precio_tuberia_var.get())

            if largo <= 0 or precio_metro < 0:
                raise ValueError()
        except:
            messagebox.showwarning("Advertencia", "Valores invalidos")
            return

        subtotal = largo * precio_metro

        self.tuberias_agregadas.append({
            'tipo': tipo,
            'largo': largo,
            'precio_metro': precio_metro,
            'subtotal': subtotal
        })

        self.tree_tuberias.insert('', 'end', values=(
            tipo,
            f"{largo:.2f}",
            f"${precio_metro:.2f}",
            f"${subtotal:.2f}"
        ))

        print(f"Tuberia agregada: {tipo} - {largo}m")

    def agregar_mano_obra(self):
        """Agrega mano de obra a la cotizacion"""
        tipo = self.tipo_mano_obra_var.get()
        descripcion = self.desc_mano_obra_var.get()

        if not tipo:
            messagebox.showwarning("Advertencia", "Selecciona un tipo de mano de obra")
            return

        if not descripcion:
            messagebox.showwarning("Advertencia", "Selecciona una descripcion")
            return

        try:
            cantidad = float(self.cantidad_mano_obra_var.get())
            precio_unit = float(self.precio_mano_obra_var.get())

            if cantidad <= 0 or precio_unit < 0:
                raise ValueError()
        except:
            messagebox.showwarning("Advertencia", "Valores invalidos")
            return

        subtotal = cantidad * precio_unit

        self.mano_obra_agregada.append({
            'tipo': tipo,
            'descripcion': descripcion,
            'cantidad': cantidad,
            'precio_unit': precio_unit,
            'subtotal': subtotal
        })

        self.tree_mano_obra.insert('', 'end', values=(
            tipo,
            descripcion,
            cantidad,
            f"${precio_unit:.2f}",
            f"${subtotal:.2f}"
        ))

        print(f"Mano de obra agregada: {tipo} - {descripcion}")

    def eliminar_item(self, tree, lista):
        """Elimina un item seleccionado"""
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona un item para eliminar")
            return

        index = tree.index(selection[0])
        tree.delete(selection[0])
        lista.pop(index)

    def cambiar_iva(self):
        """Maneja el cambio de IVA personalizado"""
        iva_seleccionado = self.iva_var.get()

        if iva_seleccionado == "Otro":
            # Mostrar entry para IVA personalizado
            if not self.entry_iva_custom_visible:
                self.entry_iva_custom.pack(side=tk.LEFT, padx=(0, 10))
                self.entry_iva_custom_visible = True
                self.entry_iva_custom.focus()
                self.entry_iva_custom.bind('<KeyRelease>', lambda e: self.calcular_totales())
        else:
            # Ocultar entry si estaba visible
            if self.entry_iva_custom_visible:
                self.entry_iva_custom.pack_forget()
                self.entry_iva_custom_visible = False
            self.calcular_totales()

    def obtener_iva_porcentaje(self):
        """Obtiene el porcentaje de IVA actual"""
        iva_seleccionado = self.iva_var.get()

        if iva_seleccionado == "Otro":
            try:
                return float(self.entry_iva_custom.get() or 0)
            except ValueError:
                return 0
        else:
            # Extraer número del porcentaje
            return float(iva_seleccionado.replace('%', ''))

    def calcular_totales(self):
        """Calcula todos los totales de la cotizacion"""
        # Calcular totales por categoria
        total_equipos = sum(e['subtotal'] for e in self.equipos_agregados)
        total_ductos = sum(d['subtotal'] for d in self.ductos_agregados)
        total_difusores = sum(d['subtotal'] for d in self.difusores_agregados)
        total_rejillas = sum(r['subtotal'] for r in self.rejillas_agregadas)
        total_tuberias = sum(t['subtotal'] for t in self.tuberias_agregadas)
        total_mano_obra = sum(m['subtotal'] for m in self.mano_obra_agregada)
        total_materiales = sum(m['subtotal'] for m in self.materiales_agregados)
        total_gastos = sum(g['monto'] for g in self.gastos_agregados)

        # Subtotal sin impuestos
        subtotal = (total_equipos + total_ductos + total_difusores +
                   total_rejillas + total_tuberias + total_mano_obra +
                   total_materiales + total_gastos)

        # INS y CCSS (35% aproximadamente) - opcional
        total_ins_ccss = 0
        if self.incluir_ins_ccss_var.get():
            total_ins_ccss = subtotal * 0.35

        # IVA configurable
        iva_porcentaje = self.obtener_iva_porcentaje()
        base_iva = subtotal + total_ins_ccss
        total_iva = base_iva * (iva_porcentaje / 100)

        # Total final
        total = base_iva + total_iva

        # Verificar si mostrar en colones
        mostrar_colones = self.mostrar_colones_var.get()
        tipo_cambio = float(self.db.obtener_configuracion('tipo_cambio') or 515)

        # Actualizar labels
        if mostrar_colones:
            # Mostrar en colones
            self.label_total_equipos.config(text=f"Total Equipos: ₡{total_equipos * tipo_cambio:,.2f}")
            self.label_total_ductos.config(text=f"Total Ductos: ₡{total_ductos * tipo_cambio:,.2f}")
            self.label_total_difusores.config(text=f"Total Difusores: ₡{total_difusores * tipo_cambio:,.2f}")
            self.label_total_rejillas.config(text=f"Total Rejillas: ₡{total_rejillas * tipo_cambio:,.2f}")
            self.label_total_tuberias.config(text=f"Total Tuberias: ₡{total_tuberias * tipo_cambio:,.2f}")
            self.label_total_mano_obra.config(text=f"Total Mano de Obra: ₡{total_mano_obra * tipo_cambio:,.2f}")
            self.label_total_materiales.config(text=f"Total Materiales: ₡{total_materiales * tipo_cambio:,.2f}")
            self.label_total_gastos.config(text=f"Total Gastos: ₡{total_gastos * tipo_cambio:,.2f}")

            self.label_subtotal.config(text=f"Subtotal: ₡{subtotal * tipo_cambio:,.2f}")
            self.label_ins_ccss.config(text=f"INS y CCSS: ₡{total_ins_ccss * tipo_cambio:,.2f}")
            self.label_iva.config(text=f"IVA ({iva_porcentaje:.1f}%): ₡{total_iva * tipo_cambio:,.2f}")
            self.label_total.config(text=f"TOTAL: ₡{total * tipo_cambio:,.2f}")
        else:
            # Mostrar en dólares
            self.label_total_equipos.config(text=f"Total Equipos: ${total_equipos:.2f}")
            self.label_total_ductos.config(text=f"Total Ductos: ${total_ductos:.2f}")
            self.label_total_difusores.config(text=f"Total Difusores: ${total_difusores:.2f}")
            self.label_total_rejillas.config(text=f"Total Rejillas: ${total_rejillas:.2f}")
            self.label_total_tuberias.config(text=f"Total Tuberias: ${total_tuberias:.2f}")
            self.label_total_mano_obra.config(text=f"Total Mano de Obra: ${total_mano_obra:.2f}")
            self.label_total_materiales.config(text=f"Total Materiales: ${total_materiales:.2f}")
            self.label_total_gastos.config(text=f"Total Gastos: ${total_gastos:.2f}")

            self.label_subtotal.config(text=f"Subtotal: ${subtotal:.2f}")
            self.label_ins_ccss.config(text=f"INS y CCSS: ${total_ins_ccss:.2f}")
            self.label_iva.config(text=f"IVA ({iva_porcentaje:.1f}%): ${total_iva:.2f}")
            self.label_total.config(text=f"TOTAL: ${total:.2f}")

        # Guardar totales calculados
        self.totales_calculados = {
            'total_equipos': total_equipos,
            'total_ductos': total_ductos,
            'total_difusores': total_difusores,
            'total_rejillas': total_rejillas,
            'total_tuberias': total_tuberias,
            'total_mano_obra': total_mano_obra,
            'total_materiales': total_materiales,
            'total_gastos': total_gastos,
            'subtotal': subtotal,
            'ins_ccss': total_ins_ccss,
            'total_iva': total_iva,
            'total': total
        }

        print(f"Totales calculados: Total=${total:.2f} (INS/CCSS: ${total_ins_ccss:.2f})")

    def guardar_cotizacion(self):
        """Guarda la cotizacion en la base de datos"""
        # Validar cliente
        cliente_nombre = self.combo_cliente.get()
        if not cliente_nombre or cliente_nombre not in self.clientes_dict:
            messagebox.showwarning("Advertencia", "Selecciona un cliente")
            return

        # Validar que tenga items
        tiene_items = (self.equipos_agregados or self.materiales_agregados or
                      self.ductos_agregados or self.difusores_agregados or
                      self.rejillas_agregadas or self.tuberias_agregadas or
                      self.mano_obra_agregada)

        if not tiene_items:
            messagebox.showwarning("Advertencia", "Agrega al menos un item a la cotizacion")
            return

        # Calcular totales si no se han calculado
        if not hasattr(self, 'totales_calculados'):
            self.calcular_totales()

        try:
            # Generar numero de cotizacion
            fecha = datetime.now()
            numero_cot = f"COT-MT-{fecha.strftime('%y')}-{fecha.strftime('%m')}-{fecha.strftime('%d%H%M')}"

            id_cliente = self.clientes_dict[cliente_nombre]

            # Insertar cotizacion principal
            self.db.cursor.execute('''
                INSERT INTO cotizaciones (
                    numero_cotizacion, id_cliente, id_proyecto, fecha_emision, tipo_servicio,
                    visitas_anuales, factor_venta, iva, tipo_cambio,
                    total_mano_obra, total_materiales, total_gastos,
                    total_ductos, total_difusores, total_rejillas, total_tuberias,
                    ins_ccss, subtotal, total_iva, total, estado,
                    iva_porcentaje, mostrar_colones
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                numero_cot, id_cliente, self.id_proyecto, self.fecha_actual, self.tipo_servicio_var.get(),
                int(self.visitas_var.get()), self.factor_venta, self.iva, self.tipo_cambio,
                self.totales_calculados['total_mano_obra'],
                self.totales_calculados['total_materiales'],
                self.totales_calculados['total_gastos'],
                self.totales_calculados['total_ductos'],
                self.totales_calculados['total_difusores'],
                self.totales_calculados['total_rejillas'],
                self.totales_calculados['total_tuberias'],
                self.totales_calculados['ins_ccss'],
                self.totales_calculados['subtotal'],
                self.totales_calculados['total_iva'],
                self.totales_calculados['total'],
                'pendiente',
                self.obtener_iva_porcentaje(),
                1 if self.mostrar_colones_var.get() else 0
            ))

            id_cotizacion = self.db.cursor.lastrowid

            # Insertar detalle equipos
            for equipo in self.equipos_agregados:
                self.db.cursor.execute('''
                    INSERT INTO detalle_cotizacion (
                        id_cotizacion, id_equipo, cantidad, horas_por_equipo,
                        precio_unitario, subtotal
                    ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    id_cotizacion, equipo['id'], equipo['cantidad'],
                    equipo['horas'], equipo['subtotal']/equipo['cantidad'],
                    equipo['subtotal']
                ))

            # Insertar ductos
            for ducto in self.ductos_agregados:
                self.db.cursor.execute('''
                    INSERT INTO cotizacion_ductos (
                        id_cotizacion, tipo_ducto, largo_suministro,
                        largo_retorno, precio_unitario, subtotal
                    ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    id_cotizacion, ducto['tipo'], ducto['largo_suministro'],
                    ducto['largo_retorno'], ducto['precio_metro'], ducto['subtotal']
                ))

            # Insertar difusores
            for difusor in self.difusores_agregados:
                self.db.cursor.execute('''
                    INSERT INTO cotizacion_difusores (
                        id_cotizacion, tipo_difusor, cantidad,
                        precio_unitario, subtotal
                    ) VALUES (?, ?, ?, ?, ?)
                ''', (
                    id_cotizacion, difusor['tipo'], difusor['cantidad'],
                    difusor['precio_unit'], difusor['subtotal']
                ))

            # Insertar rejillas
            for rejilla in self.rejillas_agregadas:
                self.db.cursor.execute('''
                    INSERT INTO cotizacion_rejillas (
                        id_cotizacion, tipo_rejilla, cantidad,
                        precio_unitario, subtotal
                    ) VALUES (?, ?, ?, ?, ?)
                ''', (
                    id_cotizacion, rejilla['tipo'], rejilla['cantidad'],
                    rejilla['precio_unit'], rejilla['subtotal']
                ))

            # Insertar tuberias
            for tuberia in self.tuberias_agregadas:
                self.db.cursor.execute('''
                    INSERT INTO cotizacion_tuberias (
                        id_cotizacion, tipo_tuberia, largo,
                        precio_unitario, subtotal
                    ) VALUES (?, ?, ?, ?, ?)
                ''', (
                    id_cotizacion, tuberia['tipo'], tuberia['largo'],
                    tuberia['precio_metro'], tuberia['subtotal']
                ))

            # Insertar mano de obra
            for mano_obra in self.mano_obra_agregada:
                self.db.cursor.execute('''
                    INSERT INTO cotizacion_mano_obra (
                        id_cotizacion, descripcion, cantidad,
                        precio_unitario, subtotal
                    ) VALUES (?, ?, ?, ?, ?)
                ''', (
                    id_cotizacion, mano_obra['descripcion'], mano_obra['cantidad'],
                    mano_obra['precio_unit'], mano_obra['subtotal']
                ))

            # Insertar materiales
            for material in self.materiales_agregados:
                self.db.cursor.execute('''
                    INSERT INTO cotizacion_materiales (
                        id_cotizacion, id_material, cantidad,
                        precio_unitario, subtotal
                    ) VALUES (?, ?, ?, ?, ?)
                ''', (
                    id_cotizacion, material['id'], material['cantidad'],
                    material['precio_unit'], material['subtotal']
                ))

            # Insertar gastos
            for gasto in self.gastos_agregados:
                self.db.cursor.execute('''
                    INSERT INTO gastos_adicionales (
                        id_cotizacion, concepto, monto
                    ) VALUES (?, ?, ?)
                ''', (id_cotizacion, gasto['concepto'], gasto['monto']))

            self.db.conn.commit()

            messagebox.showinfo(
                "Exito",
                f"Cotizacion guardada exitosamente\n\nNumero: {numero_cot}\nTotal: ${self.totales_calculados['total']:.2f}"
            )

            print(f"Cotizacion guardada: {numero_cot}")

            # Actualizar tabla en ventana principal
            if hasattr(self.parent, 'cargar_cotizaciones'):
                self.parent.cargar_cotizaciones()

            # Cerrar ventana
            self.cerrar()

        except Exception as e:
            print(f"Error al guardar cotizacion: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"No se pudo guardar la cotizacion:\n{e}")

    def nuevo_cliente(self):
        """Abre ventana para crear nuevo cliente"""
        messagebox.showinfo("Proximamente", "Funcion de nuevo cliente en desarrollo")

    def cancelar(self):
        """Cancela y cierra la ventana"""
        if messagebox.askyesno("Confirmar", "Cancelar la cotizacion?\n\nSe perderan los datos ingresados"):
            self.cerrar()

    def cerrar(self):
        """Cierra la ventana"""
        self.db.desconectar()
        self.window.destroy()
