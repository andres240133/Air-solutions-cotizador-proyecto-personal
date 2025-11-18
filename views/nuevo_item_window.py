"""
nuevo_item_window.py - Ventana para Crear Nuevo Item

Permite crear un nuevo item en un nivel con costos desglosados:
- Costo Equipo
- Costo Materiales
- Costo Mano de Obra
"""

import tkinter as tk
from tkinter import ttk, messagebox


class NuevoItemWindow:
    """Ventana para crear un nuevo item"""

    def __init__(self, parent, db, id_nivel):
        """
        Inicializa la ventana de nuevo item

        Args:
            parent: Ventana padre
            db: Instancia de DatabaseManager
            id_nivel: ID del nivel donde se agregará el item
        """
        self.db = db
        self.id_nivel = id_nivel

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Nuevo Item")
        self.dialog.geometry("600x550")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Centrar ventana
        self.centrar_ventana()

        # Cargar catálogo
        self.cargar_catalogo()

        # Crear interfaz
        self.crear_interfaz()

    def centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        self.dialog.update_idletasks()
        width = 600
        height = 550
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')

    def cargar_catalogo(self):
        """Carga el catálogo de componentes HVAC"""
        cursor = self.db.ejecutar_query('''
            SELECT
                id_componente, codigo, descripcion,
                costo_equipo_base, costo_material_base,
                costo_mano_obra_base, unidad_medida
            FROM catalogo_hvac
            WHERE activo = 1
            ORDER BY codigo
        ''')

        self.catalogo = {}
        self.catalogo_list = []

        for row in cursor.fetchall():
            (id_comp, codigo, desc, c_equipo, c_material,
             c_mano_obra, unidad) = row

            display = f"{codigo} - {desc}"
            self.catalogo_list.append(display)
            self.catalogo[display] = {
                'id': id_comp,
                'codigo': codigo,
                'descripcion': desc,
                'costo_equipo': c_equipo,
                'costo_material': c_material,
                'costo_mano_obra': c_mano_obra,
                'unidad': unidad
            }

    def crear_interfaz(self):
        """Crea la interfaz de la ventana"""
        # Header
        header = tk.Frame(self.dialog, bg='#1e293b', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Crear Nuevo Item",
            font=("Arial", 14, "bold"),
            bg='#1e293b',
            fg='white'
        ).pack(pady=15)

        # Contenedor principal con scroll
        main_frame = tk.Frame(self.dialog, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # === SELECCIÓN DE CATÁLOGO (OPCIONAL) ===
        catalogo_frame = tk.LabelFrame(
            main_frame,
            text="Usar componente del catálogo (opcional)",
            font=("Arial", 10, "bold"),
            bg='white',
            padx=10,
            pady=10
        )
        catalogo_frame.pack(fill=tk.X, pady=(0, 15))

        self.catalogo_var = tk.StringVar()
        catalogo_combo = ttk.Combobox(
            catalogo_frame,
            textvariable=self.catalogo_var,
            values=self.catalogo_list,
            font=("Arial", 9),
            width=50,
            state='readonly'
        )
        catalogo_combo.pack(fill=tk.X)
        catalogo_combo.bind('<<ComboboxSelected>>', self.on_catalogo_seleccionado)

        # === INFORMACIÓN DEL ITEM ===
        info_frame = tk.LabelFrame(
            main_frame,
            text="Información del Item",
            font=("Arial", 10, "bold"),
            bg='white',
            padx=10,
            pady=10
        )
        info_frame.pack(fill=tk.X, pady=(0, 15))

        # Especificación
        row = 0
        tk.Label(
            info_frame,
            text="Especificación: *",
            font=("Arial", 10),
            bg='white'
        ).grid(row=row, column=0, sticky='w', pady=5)

        self.especificacion_var = tk.StringVar()
        tk.Entry(
            info_frame,
            textvariable=self.especificacion_var,
            font=("Arial", 10),
            width=40
        ).grid(row=row, column=1, sticky='ew', pady=5, padx=(10, 0))

        # Descripción
        row += 1
        tk.Label(
            info_frame,
            text="Descripción:",
            font=("Arial", 10),
            bg='white'
        ).grid(row=row, column=0, sticky='w', pady=5)

        self.descripcion_var = tk.StringVar()
        tk.Entry(
            info_frame,
            textvariable=self.descripcion_var,
            font=("Arial", 10),
            width=40
        ).grid(row=row, column=1, sticky='ew', pady=5, padx=(10, 0))

        # Cantidad
        row += 1
        tk.Label(
            info_frame,
            text="Cantidad: *",
            font=("Arial", 10),
            bg='white'
        ).grid(row=row, column=0, sticky='w', pady=5)

        cantidad_frame = tk.Frame(info_frame, bg='white')
        cantidad_frame.grid(row=row, column=1, sticky='ew', pady=5, padx=(10, 0))

        self.cantidad_var = tk.StringVar(value='1')
        tk.Entry(
            cantidad_frame,
            textvariable=self.cantidad_var,
            font=("Arial", 10),
            width=15
        ).pack(side=tk.LEFT)

        tk.Label(
            cantidad_frame,
            text="Unidad:",
            font=("Arial", 10),
            bg='white'
        ).pack(side=tk.LEFT, padx=(15, 5))

        self.unidad_var = tk.StringVar(value='unidad')
        unidad_combo = ttk.Combobox(
            cantidad_frame,
            textvariable=self.unidad_var,
            values=['unidad', 'ml', 'm²', 'm³', 'kg', 'lb', 'global'],
            font=("Arial", 10),
            width=10,
            state='readonly'
        )
        unidad_combo.pack(side=tk.LEFT)

        info_frame.columnconfigure(1, weight=1)

        # === COSTOS ===
        costos_frame = tk.LabelFrame(
            main_frame,
            text="Costos por Unidad (USD)",
            font=("Arial", 10, "bold"),
            bg='white',
            padx=10,
            pady=10
        )
        costos_frame.pack(fill=tk.X, pady=(0, 15))

        # Costo Equipo
        row = 0
        tk.Label(
            costos_frame,
            text="Costo Equipo:",
            font=("Arial", 10),
            bg='white'
        ).grid(row=row, column=0, sticky='w', pady=5)

        self.costo_equipo_var = tk.StringVar(value='0.00')
        self.costo_equipo_var.trace('w', self.calcular_total)
        tk.Entry(
            costos_frame,
            textvariable=self.costo_equipo_var,
            font=("Arial", 10),
            width=20
        ).grid(row=row, column=1, sticky='w', pady=5, padx=(10, 0))

        # Costo Materiales
        row += 1
        tk.Label(
            costos_frame,
            text="Costo Materiales:",
            font=("Arial", 10),
            bg='white'
        ).grid(row=row, column=0, sticky='w', pady=5)

        self.costo_materiales_var = tk.StringVar(value='0.00')
        self.costo_materiales_var.trace('w', self.calcular_total)
        tk.Entry(
            costos_frame,
            textvariable=self.costo_materiales_var,
            font=("Arial", 10),
            width=20
        ).grid(row=row, column=1, sticky='w', pady=5, padx=(10, 0))

        # Costo Mano de Obra
        row += 1
        tk.Label(
            costos_frame,
            text="Costo Mano de Obra:",
            font=("Arial", 10),
            bg='white'
        ).grid(row=row, column=0, sticky='w', pady=5)

        self.costo_mano_obra_var = tk.StringVar(value='0.00')
        self.costo_mano_obra_var.trace('w', self.calcular_total)
        tk.Entry(
            costos_frame,
            textvariable=self.costo_mano_obra_var,
            font=("Arial", 10),
            width=20
        ).grid(row=row, column=1, sticky='w', pady=5, padx=(10, 0))

        # Total
        row += 1
        tk.Label(
            costos_frame,
            text="Total por Unidad:",
            font=("Arial", 10, "bold"),
            bg='white'
        ).grid(row=row, column=0, sticky='w', pady=(10, 5))

        self.total_label = tk.Label(
            costos_frame,
            text="$0.00",
            font=("Arial", 11, "bold"),
            bg='white',
            fg='#10b981'
        )
        self.total_label.grid(row=row, column=1, sticky='w', pady=(10, 5), padx=(10, 0))

        # Botones
        btn_frame = tk.Frame(self.dialog, bg='white')
        btn_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        tk.Button(
            btn_frame,
            text="✅ Crear Item",
            font=("Arial", 10, "bold"),
            bg='#10b981',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            command=self.guardar_item
        ).pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(
            btn_frame,
            text="❌ Cancelar",
            font=("Arial", 10),
            bg='#6b7280',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            command=self.dialog.destroy
        ).pack(side=tk.LEFT)

    def on_catalogo_seleccionado(self, event):
        """Evento cuando se selecciona un componente del catálogo"""
        seleccion = self.catalogo_var.get()
        if not seleccion or seleccion not in self.catalogo:
            return

        comp = self.catalogo[seleccion]

        # Rellenar campos
        self.especificacion_var.set(comp['codigo'])
        self.descripcion_var.set(comp['descripcion'])
        self.unidad_var.set(comp['unidad'])
        self.costo_equipo_var.set(f"{comp['costo_equipo']:.2f}")
        self.costo_materiales_var.set(f"{comp['costo_material']:.2f}")
        self.costo_mano_obra_var.set(f"{comp['costo_mano_obra']:.2f}")

    def calcular_total(self, *args):
        """Calcula el total automáticamente"""
        try:
            costo_equipo = float(self.costo_equipo_var.get() or 0)
            costo_materiales = float(self.costo_materiales_var.get() or 0)
            costo_mano_obra = float(self.costo_mano_obra_var.get() or 0)

            total = costo_equipo + costo_materiales + costo_mano_obra
            self.total_label.config(text=f'${total:,.2f}')
        except ValueError:
            self.total_label.config(text='$0.00')

    def guardar_item(self):
        """Guarda el nuevo item"""
        # Validar campos requeridos
        especificacion = self.especificacion_var.get().strip()

        if not especificacion:
            messagebox.showerror("Error", "La especificación es obligatoria")
            return

        try:
            cantidad = float(self.cantidad_var.get())
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número mayor a 0")
            return

        try:
            costo_equipo = float(self.costo_equipo_var.get() or 0)
            costo_materiales = float(self.costo_materiales_var.get() or 0)
            costo_mano_obra = float(self.costo_mano_obra_var.get() or 0)
        except ValueError:
            messagebox.showerror("Error", "Los costos deben ser números válidos")
            return

        # Obtener datos
        descripcion = self.descripcion_var.get().strip()
        unidad = self.unidad_var.get()

        # Calcular total
        total_unitario = costo_equipo + costo_materiales + costo_mano_obra
        total_item = total_unitario * cantidad

        # Obtener orden
        cursor = self.db.ejecutar_query(
            'SELECT MAX(orden) FROM proyecto_items WHERE id_nivel = ?',
            (self.id_nivel,)
        )
        resultado = cursor.fetchone()
        orden = (resultado[0] + 1) if (resultado and resultado[0] is not None) else 0

        try:
            # Insertar item
            self.db.ejecutar_query('''
                INSERT INTO proyecto_items (
                    id_nivel, especificacion, descripcion,
                    cantidad, unidad,
                    costo_equipo, costo_materiales, costo_mano_obra,
                    total_item, orden
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.id_nivel, especificacion,
                descripcion if descripcion else None,
                cantidad, unidad,
                costo_equipo, costo_materiales, costo_mano_obra,
                total_item, orden
            ))

            messagebox.showinfo("Éxito", f"Item '{especificacion}' creado correctamente")
            self.dialog.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Error al crear item:\n{e}")
