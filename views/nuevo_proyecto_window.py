"""
nuevo_proyecto_window.py - Ventana para Crear Nuevo Proyecto

Permite crear un nuevo proyecto grande con información básica
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tkcalendar import DateEntry


class NuevoProyectoWindow:
    """Ventana para crear un nuevo proyecto"""

    def __init__(self, parent, db):
        """
        Inicializa la ventana de nuevo proyecto

        Args:
            parent: Ventana padre
            db: Instancia de DatabaseManager
        """
        self.db = db
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Nuevo Proyecto")
        self.dialog.geometry("700x650")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Centrar ventana
        self.centrar_ventana()

        # Crear interfaz
        self.crear_interfaz()

    def centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        self.dialog.update_idletasks()
        width = 700
        height = 650
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')

    def crear_interfaz(self):
        """Crea la interfaz de la ventana"""
        # Header
        header = tk.Frame(self.dialog, bg='#1e293b', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Crear Nuevo Proyecto",
            font=("Arial", 16, "bold"),
            bg='#1e293b',
            fg='white'
        ).pack(pady=15)

        # Contenedor principal con scroll
        main_frame = tk.Frame(self.dialog, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Canvas y scrollbar
        canvas = tk.Canvas(main_frame, bg='white')
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        content_frame = tk.Frame(canvas, bg='white')

        content_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=content_frame, anchor="nw", width=620)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # === INFORMACIÓN BÁSICA ===
        info_frame = tk.LabelFrame(
            content_frame,
            text="Información Básica",
            font=("Arial", 11, "bold"),
            bg='white',
            padx=15,
            pady=15
        )
        info_frame.pack(fill=tk.X, pady=(0, 15))

        # Número de proyecto
        row = 0
        tk.Label(
            info_frame,
            text="Número de Proyecto:",
            font=("Arial", 10),
            bg='white'
        ).grid(row=row, column=0, sticky='w', pady=5)

        self.numero_var = tk.StringVar()
        self.numero_var.set(self.generar_numero_proyecto())
        tk.Entry(
            info_frame,
            textvariable=self.numero_var,
            font=("Arial", 10),
            width=40,
            state='readonly',
            bg='#f3f4f6'
        ).grid(row=row, column=1, sticky='ew', pady=5, padx=(10, 0))

        # Nombre del proyecto
        row += 1
        tk.Label(
            info_frame,
            text="Nombre del Proyecto: *",
            font=("Arial", 10),
            bg='white'
        ).grid(row=row, column=0, sticky='w', pady=5)

        self.nombre_var = tk.StringVar()
        tk.Entry(
            info_frame,
            textvariable=self.nombre_var,
            font=("Arial", 10),
            width=40
        ).grid(row=row, column=1, sticky='ew', pady=5, padx=(10, 0))

        # Cliente
        row += 1
        tk.Label(
            info_frame,
            text="Cliente: *",
            font=("Arial", 10),
            bg='white'
        ).grid(row=row, column=0, sticky='w', pady=5)

        self.cliente_var = tk.StringVar()
        self.cliente_combo = ttk.Combobox(
            info_frame,
            textvariable=self.cliente_var,
            font=("Arial", 10),
            width=38,
            state='readonly'
        )
        self.cliente_combo.grid(row=row, column=1, sticky='ew', pady=5, padx=(10, 0))
        self.cargar_clientes()

        # Ubicación
        row += 1
        tk.Label(
            info_frame,
            text="Ubicación:",
            font=("Arial", 10),
            bg='white'
        ).grid(row=row, column=0, sticky='w', pady=5)

        self.ubicacion_var = tk.StringVar()
        tk.Entry(
            info_frame,
            textvariable=self.ubicacion_var,
            font=("Arial", 10),
            width=40
        ).grid(row=row, column=1, sticky='ew', pady=5, padx=(10, 0))

        # Responsable
        row += 1
        tk.Label(
            info_frame,
            text="Responsable:",
            font=("Arial", 10),
            bg='white'
        ).grid(row=row, column=0, sticky='w', pady=5)

        self.responsable_var = tk.StringVar()
        tk.Entry(
            info_frame,
            textvariable=self.responsable_var,
            font=("Arial", 10),
            width=40
        ).grid(row=row, column=1, sticky='ew', pady=5, padx=(10, 0))

        # Estado
        row += 1
        tk.Label(
            info_frame,
            text="Estado:",
            font=("Arial", 10),
            bg='white'
        ).grid(row=row, column=0, sticky='w', pady=5)

        self.estado_var = tk.StringVar(value='en_planificacion')
        estados_combo = ttk.Combobox(
            info_frame,
            textvariable=self.estado_var,
            values=['en_planificacion', 'en_curso', 'pausado', 'completado', 'cancelado'],
            font=("Arial", 10),
            width=38,
            state='readonly'
        )
        estados_combo.grid(row=row, column=1, sticky='ew', pady=5, padx=(10, 0))

        info_frame.columnconfigure(1, weight=1)

        # === FECHAS ===
        fechas_frame = tk.LabelFrame(
            content_frame,
            text="Fechas",
            font=("Arial", 11, "bold"),
            bg='white',
            padx=15,
            pady=15
        )
        fechas_frame.pack(fill=tk.X, pady=(0, 15))

        # Fecha de inicio
        row = 0
        tk.Label(
            fechas_frame,
            text="Fecha de Inicio:",
            font=("Arial", 10),
            bg='white'
        ).grid(row=row, column=0, sticky='w', pady=5)

        self.fecha_inicio_var = tk.StringVar()
        fecha_inicio_entry = DateEntry(
            fechas_frame,
            textvariable=self.fecha_inicio_var,
            font=("Arial", 10),
            width=38,
            background='#2563eb',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd'
        )
        fecha_inicio_entry.grid(row=row, column=1, sticky='ew', pady=5, padx=(10, 0))

        # Fecha fin estimada
        row += 1
        tk.Label(
            fechas_frame,
            text="Fecha Fin Estimada:",
            font=("Arial", 10),
            bg='white'
        ).grid(row=row, column=0, sticky='w', pady=5)

        self.fecha_fin_var = tk.StringVar()
        fecha_fin_entry = DateEntry(
            fechas_frame,
            textvariable=self.fecha_fin_var,
            font=("Arial", 10),
            width=38,
            background='#2563eb',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd'
        )
        fecha_fin_entry.grid(row=row, column=1, sticky='ew', pady=5, padx=(10, 0))

        fechas_frame.columnconfigure(1, weight=1)

        # === DESCRIPCIÓN Y NOTAS ===
        desc_frame = tk.LabelFrame(
            content_frame,
            text="Descripción y Notas",
            font=("Arial", 11, "bold"),
            bg='white',
            padx=15,
            pady=15
        )
        desc_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        tk.Label(
            desc_frame,
            text="Descripción del Proyecto:",
            font=("Arial", 10),
            bg='white'
        ).pack(anchor='w', pady=(0, 5))

        self.descripcion_text = tk.Text(
            desc_frame,
            font=("Arial", 10),
            width=60,
            height=4,
            wrap=tk.WORD
        )
        self.descripcion_text.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            desc_frame,
            text="Notas Adicionales:",
            font=("Arial", 10),
            bg='white'
        ).pack(anchor='w', pady=(10, 5))

        self.notas_text = tk.Text(
            desc_frame,
            font=("Arial", 10),
            width=60,
            height=3,
            wrap=tk.WORD
        )
        self.notas_text.pack(fill=tk.BOTH, expand=True)

        # === BOTONES ===
        btn_frame = tk.Frame(self.dialog, bg='white')
        btn_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        tk.Button(
            btn_frame,
            text="✅ Crear Proyecto",
            font=("Arial", 11, "bold"),
            bg='#10b981',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=30,
            pady=10,
            command=self.guardar_proyecto
        ).pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(
            btn_frame,
            text="❌ Cancelar",
            font=("Arial", 11),
            bg='#6b7280',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=30,
            pady=10,
            command=self.dialog.destroy
        ).pack(side=tk.LEFT)

    def generar_numero_proyecto(self):
        """Genera el siguiente número de proyecto disponible"""
        cursor = self.db.ejecutar_query(
            'SELECT numero_proyecto FROM proyectos ORDER BY id_proyecto DESC LIMIT 1'
        )
        resultado = cursor.fetchone()

        if resultado:
            ultimo_numero = resultado[0]
            # Extraer número (formato: PROY-2025-001)
            partes = ultimo_numero.split('-')
            if len(partes) == 3:
                año = datetime.now().year
                if int(partes[1]) == año:
                    siguiente = int(partes[2]) + 1
                    return f"PROY-{año}-{siguiente:03d}"

        # Si no hay proyectos o es nuevo año
        año = datetime.now().year
        return f"PROY-{año}-001"

    def cargar_clientes(self):
        """Carga los clientes en el combo"""
        cursor = self.db.ejecutar_query(
            'SELECT id_cliente, nombre_empresa FROM clientes WHERE activo = 1 ORDER BY nombre_empresa'
        )
        clientes = cursor.fetchall()

        self.clientes_dict = {f"{nombre} (ID: {id_c})": id_c for id_c, nombre in clientes}
        self.cliente_combo['values'] = list(self.clientes_dict.keys())

        if self.clientes_dict:
            self.cliente_combo.current(0)

    def guardar_proyecto(self):
        """Guarda el nuevo proyecto"""
        # Validar campos requeridos
        if not self.nombre_var.get().strip():
            messagebox.showerror("Error", "El nombre del proyecto es obligatorio")
            return

        if not self.cliente_var.get():
            messagebox.showerror("Error", "Debes seleccionar un cliente")
            return

        # Obtener datos
        numero = self.numero_var.get()
        nombre = self.nombre_var.get().strip()
        id_cliente = self.clientes_dict[self.cliente_var.get()]
        ubicacion = self.ubicacion_var.get().strip()
        responsable = self.responsable_var.get().strip()
        estado = self.estado_var.get()
        fecha_inicio = self.fecha_inicio_var.get()
        fecha_fin = self.fecha_fin_var.get()
        descripcion = self.descripcion_text.get('1.0', tk.END).strip()
        notas = self.notas_text.get('1.0', tk.END).strip()

        try:
            # Insertar proyecto
            self.db.ejecutar_query('''
                INSERT INTO proyectos (
                    numero_proyecto, nombre_proyecto, id_cliente,
                    ubicacion, responsable, estado,
                    fecha_inicio, fecha_fin_estimada,
                    descripcion, notas
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                numero, nombre, id_cliente,
                ubicacion if ubicacion else None,
                responsable if responsable else None,
                estado,
                fecha_inicio, fecha_fin,
                descripcion if descripcion else None,
                notas if notas else None
            ))

            messagebox.showinfo(
                "Éxito",
                f"Proyecto {numero} creado correctamente.\n\n"
                "Ahora puedes agregar niveles y items al proyecto."
            )
            self.dialog.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Error al crear proyecto:\n{e}")
