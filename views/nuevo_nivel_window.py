"""
nuevo_nivel_window.py - Ventana para Crear Nuevo Nivel

Permite crear un nuevo nivel/área en un proyecto (S100, N1, N2, etc.)
"""

import tkinter as tk
from tkinter import ttk, messagebox


class NuevoNivelWindow:
    """Ventana para crear un nuevo nivel"""

    def __init__(self, parent, db, id_proyecto):
        """
        Inicializa la ventana de nuevo nivel

        Args:
            parent: Ventana padre
            db: Instancia de DatabaseManager
            id_proyecto: ID del proyecto
        """
        self.db = db
        self.id_proyecto = id_proyecto

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Nuevo Nivel/Área")
        self.dialog.geometry("550x450")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Centrar ventana
        self.centrar_ventana()

        # Crear interfaz
        self.crear_interfaz()

    def centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        self.dialog.update_idletasks()
        width = 550
        height = 450
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
            text="Crear Nuevo Nivel/Área",
            font=("Arial", 14, "bold"),
            bg='#1e293b',
            fg='white'
        ).pack(pady=15)

        # Contenedor principal
        main_frame = tk.Frame(self.dialog, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        # Código del nivel
        row = 0
        tk.Label(
            main_frame,
            text="Código del Nivel: *",
            font=("Arial", 10),
            bg='white'
        ).grid(row=row, column=0, sticky='w', pady=10)

        codigo_frame = tk.Frame(main_frame, bg='white')
        codigo_frame.grid(row=row, column=1, sticky='ew', pady=10, padx=(10, 0))

        self.codigo_var = tk.StringVar()
        tk.Entry(
            codigo_frame,
            textvariable=self.codigo_var,
            font=("Arial", 10),
            width=15
        ).pack(side=tk.LEFT)

        # Botones de sugerencias
        sugerencias_frame = tk.Frame(codigo_frame, bg='white')
        sugerencias_frame.pack(side=tk.LEFT, padx=(10, 0))

        tk.Button(
            sugerencias_frame,
            text="S100",
            font=("Arial", 8),
            bg='#e5e7eb',
            relief=tk.FLAT,
            cursor='hand2',
            command=lambda: self.codigo_var.set('S100')
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            sugerencias_frame,
            text="N1",
            font=("Arial", 8),
            bg='#e5e7eb',
            relief=tk.FLAT,
            cursor='hand2',
            command=lambda: self.codigo_var.set('N1')
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            sugerencias_frame,
            text="N2",
            font=("Arial", 8),
            bg='#e5e7eb',
            relief=tk.FLAT,
            cursor='hand2',
            command=lambda: self.codigo_var.set('N2')
        ).pack(side=tk.LEFT, padx=2)

        # Ayuda
        row += 1
        tk.Label(
            main_frame,
            text="Ejemplos: S100 (Sótano 1), N1 (Nivel 1), N2 (Nivel 2)",
            font=("Arial", 8),
            bg='white',
            fg='#6b7280'
        ).grid(row=row, column=0, columnspan=2, sticky='w', pady=(0, 15))

        # Nombre del nivel
        row += 1
        tk.Label(
            main_frame,
            text="Nombre del Nivel: *",
            font=("Arial", 10),
            bg='white'
        ).grid(row=row, column=0, sticky='w', pady=10)

        self.nombre_var = tk.StringVar()
        tk.Entry(
            main_frame,
            textvariable=self.nombre_var,
            font=("Arial", 10),
            width=30
        ).grid(row=row, column=1, sticky='ew', pady=10, padx=(10, 0))

        # Orden
        row += 1
        tk.Label(
            main_frame,
            text="Orden de visualización:",
            font=("Arial", 10),
            bg='white'
        ).grid(row=row, column=0, sticky='w', pady=10)

        self.orden_var = tk.StringVar()
        orden_spin = tk.Spinbox(
            main_frame,
            from_=0,
            to=100,
            textvariable=self.orden_var,
            font=("Arial", 10),
            width=10
        )
        orden_spin.grid(row=row, column=1, sticky='w', pady=10, padx=(10, 0))
        self.orden_var.set(self.obtener_siguiente_orden())

        # Notas
        row += 1
        tk.Label(
            main_frame,
            text="Notas:",
            font=("Arial", 10),
            bg='white'
        ).grid(row=row, column=0, sticky='nw', pady=10)

        self.notas_text = tk.Text(
            main_frame,
            font=("Arial", 10),
            width=35,
            height=3,
            wrap=tk.WORD
        )
        self.notas_text.grid(row=row, column=1, sticky='ew', pady=10, padx=(10, 0))

        main_frame.columnconfigure(1, weight=1)

        # Botones
        btn_frame = tk.Frame(self.dialog, bg='white')
        btn_frame.pack(fill=tk.X, padx=30, pady=(0, 20))

        tk.Button(
            btn_frame,
            text="✅ Crear Nivel",
            font=("Arial", 10, "bold"),
            bg='#10b981',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            command=self.guardar_nivel
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

    def obtener_siguiente_orden(self):
        """Obtiene el siguiente orden disponible"""
        cursor = self.db.ejecutar_query(
            'SELECT MAX(orden) FROM proyecto_niveles WHERE id_proyecto = ?',
            (self.id_proyecto,)
        )
        resultado = cursor.fetchone()

        if resultado and resultado[0] is not None:
            return resultado[0] + 1
        return 0

    def guardar_nivel(self):
        """Guarda el nuevo nivel"""
        # Validar campos requeridos
        codigo = self.codigo_var.get().strip()
        nombre = self.nombre_var.get().strip()

        if not codigo:
            messagebox.showerror("Error", "El código del nivel es obligatorio")
            return

        if not nombre:
            messagebox.showerror("Error", "El nombre del nivel es obligatorio")
            return

        # Verificar que no exista el código
        cursor = self.db.ejecutar_query(
            'SELECT id_nivel FROM proyecto_niveles WHERE id_proyecto = ? AND codigo_nivel = ?',
            (self.id_proyecto, codigo)
        )

        if cursor.fetchone():
            messagebox.showerror(
                "Error",
                f"Ya existe un nivel con el código '{codigo}' en este proyecto"
            )
            return

        # Obtener datos
        orden = int(self.orden_var.get())
        notas = self.notas_text.get('1.0', tk.END).strip()

        try:
            # Insertar nivel
            self.db.ejecutar_query('''
                INSERT INTO proyecto_niveles (
                    id_proyecto, codigo_nivel, nombre_nivel,
                    orden, notas
                )
                VALUES (?, ?, ?, ?, ?)
            ''', (
                self.id_proyecto, codigo, nombre, orden,
                notas if notas else None
            ))

            messagebox.showinfo(
                "Éxito",
                f"Nivel {codigo} creado correctamente.\n\n"
                "Ahora puedes agregar items a este nivel."
            )
            self.dialog.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Error al crear nivel:\n{e}")
