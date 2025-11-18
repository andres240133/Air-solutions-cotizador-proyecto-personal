"""
editar_item_window.py - Ventana para Editar Item

Permite editar un item existente con sus costos
"""

import tkinter as tk
from tkinter import ttk, messagebox


class EditarItemWindow:
    """Ventana para editar un item"""

    def __init__(self, parent, db, id_item):
        """
        Inicializa la ventana de edición

        Args:
            parent: Ventana padre
            db: Instancia de DatabaseManager
            id_item: ID del item a editar
        """
        self.db = db
        self.id_item = id_item

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Editar Item")
        self.dialog.geometry("600x500")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Centrar ventana
        self.centrar_ventana()

        # Cargar datos del item
        self.cargar_item()

        # Crear interfaz
        self.crear_interfaz()

    def centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        self.dialog.update_idletasks()
        width = 600
        height = 500
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')

    def cargar_item(self):
        """Carga los datos del item"""
        cursor = self.db.ejecutar_query('''
            SELECT
                especificacion, descripcion, cantidad, unidad,
                costo_equipo, costo_materiales, costo_mano_obra
            FROM proyecto_items
            WHERE id_item = ?
        ''', (self.id_item,))

        self.item = cursor.fetchone()

        if not self.item:
            messagebox.showerror("Error", "Item no encontrado")
            self.dialog.destroy()
            return

    def crear_interfaz(self):
        """Crea la interfaz de la ventana"""
        # Header
        header = tk.Frame(self.dialog, bg='#1e293b', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Editar Item",
            font=("Arial", 14, "bold"),
            bg='#1e293b',
            fg='white'
        ).pack(pady=15)

        # Contenedor principal
        main_frame = tk.Frame(self.dialog, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

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

        self.especificacion_var = tk.StringVar(value=self.item[0])
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

        self.descripcion_var = tk.StringVar(value=self.item[1] or '')
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

        self.cantidad_var = tk.StringVar(value=str(self.item[2]))
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

        self.unidad_var = tk.StringVar(value=self.item[3])
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

        self.costo_equipo_var = tk.StringVar(value=f'{self.item[4]:.2f}')
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

        self.costo_materiales_var = tk.StringVar(value=f'{self.item[5]:.2f}')
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

        self.costo_mano_obra_var = tk.StringVar(value=f'{self.item[6]:.2f}')
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

        # Calcular total inicial
        self.calcular_total()

        # Botones
        btn_frame = tk.Frame(self.dialog, bg='white')
        btn_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        tk.Button(
            btn_frame,
            text="💾 Guardar Cambios",
            font=("Arial", 10, "bold"),
            bg='#10b981',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            command=self.guardar_cambios
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

    def guardar_cambios(self):
        """Guarda los cambios del item"""
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

        try:
            # Actualizar item
            self.db.ejecutar_query('''
                UPDATE proyecto_items
                SET especificacion = ?, descripcion = ?,
                    cantidad = ?, unidad = ?,
                    costo_equipo = ?, costo_materiales = ?, costo_mano_obra = ?,
                    total_item = ?
                WHERE id_item = ?
            ''', (
                especificacion,
                descripcion if descripcion else None,
                cantidad, unidad,
                costo_equipo, costo_materiales, costo_mano_obra,
                total_item, self.id_item
            ))

            messagebox.showinfo("Éxito", "Item actualizado correctamente")
            self.dialog.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar item:\n{e}")
