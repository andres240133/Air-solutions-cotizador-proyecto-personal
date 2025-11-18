"""
editar_nivel_window.py - Ventana para Editar Nivel

Permite editar un nivel/área existente
"""

import tkinter as tk
from tkinter import ttk, messagebox


class EditarNivelWindow:
    """Ventana para editar un nivel"""

    def __init__(self, parent, db, id_nivel):
        """
        Inicializa la ventana de edición

        Args:
            parent: Ventana padre
            db: Instancia de DatabaseManager
            id_nivel: ID del nivel a editar
        """
        self.db = db
        self.id_nivel = id_nivel

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Editar Nivel/Área")
        self.dialog.geometry("500x350")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Centrar ventana
        self.centrar_ventana()

        # Cargar datos del nivel
        self.cargar_nivel()

        # Crear interfaz
        self.crear_interfaz()

    def centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        self.dialog.update_idletasks()
        width = 500
        height = 350
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')

    def cargar_nivel(self):
        """Carga los datos del nivel"""
        cursor = self.db.ejecutar_query('''
            SELECT codigo_nivel, nombre_nivel, orden, notas
            FROM proyecto_niveles
            WHERE id_nivel = ?
        ''', (self.id_nivel,))

        self.nivel = cursor.fetchone()

        if not self.nivel:
            messagebox.showerror("Error", "Nivel no encontrado")
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
            text="Editar Nivel/Área",
            font=("Arial", 14, "bold"),
            bg='#1e293b',
            fg='white'
        ).pack(pady=15)

        # Contenedor principal
        main_frame = tk.Frame(self.dialog, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        # Código del nivel (readonly)
        row = 0
        tk.Label(
            main_frame,
            text="Código del Nivel:",
            font=("Arial", 10),
            bg='white'
        ).grid(row=row, column=0, sticky='w', pady=10)

        self.codigo_var = tk.StringVar(value=self.nivel[0])
        tk.Entry(
            main_frame,
            textvariable=self.codigo_var,
            font=("Arial", 10),
            width=30,
            state='readonly',
            bg='#f3f4f6'
        ).grid(row=row, column=1, sticky='ew', pady=10, padx=(10, 0))

        # Nombre del nivel
        row += 1
        tk.Label(
            main_frame,
            text="Nombre del Nivel: *",
            font=("Arial", 10),
            bg='white'
        ).grid(row=row, column=0, sticky='w', pady=10)

        self.nombre_var = tk.StringVar(value=self.nivel[1])
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

        self.orden_var = tk.StringVar(value=str(self.nivel[2]))
        tk.Spinbox(
            main_frame,
            from_=0,
            to=100,
            textvariable=self.orden_var,
            font=("Arial", 10),
            width=10
        ).grid(row=row, column=1, sticky='w', pady=10, padx=(10, 0))

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
            width=30,
            height=4,
            wrap=tk.WORD
        )
        self.notas_text.grid(row=row, column=1, sticky='ew', pady=10, padx=(10, 0))

        if self.nivel[3]:
            self.notas_text.insert('1.0', self.nivel[3])

        main_frame.columnconfigure(1, weight=1)

        # Botones
        btn_frame = tk.Frame(self.dialog, bg='white')
        btn_frame.pack(fill=tk.X, padx=30, pady=(0, 20))

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

    def guardar_cambios(self):
        """Guarda los cambios del nivel"""
        # Validar campos requeridos
        nombre = self.nombre_var.get().strip()

        if not nombre:
            messagebox.showerror("Error", "El nombre del nivel es obligatorio")
            return

        # Obtener datos
        orden = int(self.orden_var.get())
        notas = self.notas_text.get('1.0', tk.END).strip()

        try:
            # Actualizar nivel
            self.db.ejecutar_query('''
                UPDATE proyecto_niveles
                SET nombre_nivel = ?, orden = ?, notas = ?
                WHERE id_nivel = ?
            ''', (nombre, orden, notas if notas else None, self.id_nivel))

            messagebox.showinfo("Éxito", "Nivel actualizado correctamente")
            self.dialog.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar nivel:\n{e}")
