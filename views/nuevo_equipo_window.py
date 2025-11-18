"""
nuevo_equipo_window.py - Ventana para agregar nuevo equipo HVAC

Permite agregar equipos de aire acondicionado al catálogo:
- Tipo de equipo (nombre/modelo)
- Horas de mantenimiento
- Categoría
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.database import DatabaseManager


class NuevoEquipoWindow:
    """Ventana modal para agregar nuevo equipo"""

    def __init__(self, parent):
        """
        Inicializa la ventana de nuevo equipo

        Args:
            parent: Ventana principal que llama a esta ventana
        """
        self.parent = parent
        self.window = tk.Toplevel()
        self.window.title("Nuevo Equipo HVAC")
        self.window.geometry("600x450")
        self.window.resizable(False, False)

        # Hacer ventana modal
        self.window.transient(parent.root if hasattr(parent, 'root') else parent)
        self.window.grab_set()

        # Centrar ventana
        self.centrar_ventana()

        # Conectar a base de datos
        self.db = DatabaseManager()
        self.db.conectar()

        # Variables del formulario
        self.tipo_equipo_var = tk.StringVar()
        self.horas_mantenimiento_var = tk.StringVar(value="0")
        self.categoria_var = tk.StringVar()

        # Crear interfaz
        self.crear_interfaz()

    def centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        self.window.update_idletasks()
        width = 600
        height = 450
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def crear_interfaz(self):
        """Crea la interfaz de la ventana"""
        # Header
        header = tk.Frame(self.window, bg='#2563eb', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Nuevo Equipo HVAC",
            font=("Arial", 16, "bold"),
            bg='#2563eb',
            fg='white'
        ).pack(side=tk.LEFT, padx=20, pady=15)

        # Contenedor principal
        main_container = tk.Frame(self.window, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Formulario
        self.crear_formulario(main_container)

        # Botones
        self.crear_botones(main_container)

    def crear_formulario(self, parent):
        """Crea el formulario de datos del equipo"""
        form_frame = tk.Frame(parent, bg='white')
        form_frame.pack(fill=tk.BOTH, expand=True)

        # Tipo de equipo (obligatorio)
        tk.Label(
            form_frame,
            text="Tipo de Equipo / Modelo *",
            font=("Arial", 10, "bold"),
            bg='white',
            fg='#666'
        ).grid(row=0, column=0, sticky=tk.W, pady=(10, 5))

        tk.Label(
            form_frame,
            text="Ejemplo: Split Pared 12000 BTU, Cassette 24000 BTU, etc.",
            font=("Arial", 9),
            bg='white',
            fg='#999'
        ).grid(row=1, column=0, sticky=tk.W, pady=(0, 5))

        tipo_entry = tk.Entry(
            form_frame,
            textvariable=self.tipo_equipo_var,
            font=("Arial", 11),
            width=50,
            relief=tk.SOLID,
            bd=1
        )
        tipo_entry.grid(row=2, column=0, sticky=tk.W, pady=(0, 15), ipady=5)
        tipo_entry.focus()

        # Categoría (opcional)
        tk.Label(
            form_frame,
            text="Categoría",
            font=("Arial", 10, "bold"),
            bg='white',
            fg='#666'
        ).grid(row=3, column=0, sticky=tk.W, pady=(10, 5))

        categorias = [
            'Split Pared',
            'Split Piso-Techo',
            'Cassette',
            'Fancoil',
            'VRV/VRF',
            'Chiller',
            'Sistema Precision',
            'Estacionario',
            'Otro'
        ]

        categoria_combo = ttk.Combobox(
            form_frame,
            textvariable=self.categoria_var,
            values=categorias,
            font=("Arial", 10),
            width=48,
            state='readonly'
        )
        categoria_combo.grid(row=4, column=0, sticky=tk.W, pady=(0, 15), ipady=3)
        categoria_combo.current(0)

        # Horas de mantenimiento (obligatorio)
        tk.Label(
            form_frame,
            text="Horas de Mantenimiento *",
            font=("Arial", 10, "bold"),
            bg='white',
            fg='#666'
        ).grid(row=5, column=0, sticky=tk.W, pady=(10, 5))

        tk.Label(
            form_frame,
            text="Horas estimadas para el mantenimiento de este equipo",
            font=("Arial", 9),
            bg='white',
            fg='#999'
        ).grid(row=6, column=0, sticky=tk.W, pady=(0, 5))

        horas_frame = tk.Frame(form_frame, bg='white')
        horas_frame.grid(row=7, column=0, sticky=tk.W, pady=(0, 15))

        tk.Entry(
            horas_frame,
            textvariable=self.horas_mantenimiento_var,
            font=("Arial", 11),
            width=15,
            relief=tk.SOLID,
            bd=1
        ).pack(side=tk.LEFT, ipady=5)

        tk.Label(
            horas_frame,
            text="horas",
            font=("Arial", 10),
            bg='white',
            fg='#666'
        ).pack(side=tk.LEFT, padx=(10, 0))

        # Nota sobre campos obligatorios
        tk.Label(
            form_frame,
            text="* Campos obligatorios",
            font=("Arial", 9),
            bg='white',
            fg='#999'
        ).grid(row=8, column=0, sticky=tk.W, pady=(15, 0))

    def crear_botones(self, parent):
        """Crea los botones de acción"""
        btn_frame = tk.Frame(parent, bg='white')
        btn_frame.pack(fill=tk.X, pady=(20, 0))

        # Botón Cancelar
        tk.Button(
            btn_frame,
            text="Cancelar",
            font=("Arial", 11),
            bg='#6b7280',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=30,
            pady=10,
            command=self.cancelar
        ).pack(side=tk.RIGHT, padx=(10, 0))

        # Botón Guardar
        tk.Button(
            btn_frame,
            text="Guardar Equipo",
            font=("Arial", 11, "bold"),
            bg='#2563eb',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=30,
            pady=10,
            command=self.guardar_equipo
        ).pack(side=tk.RIGHT)

    def guardar_equipo(self):
        """Guarda el equipo en la base de datos"""
        # Validar campos obligatorios
        tipo_equipo = self.tipo_equipo_var.get().strip()
        horas_str = self.horas_mantenimiento_var.get().strip()

        if not tipo_equipo:
            messagebox.showwarning(
                "Campos Incompletos",
                "El tipo de equipo es obligatorio"
            )
            return

        # Validar horas
        try:
            horas = float(horas_str)
            if horas < 0:
                raise ValueError()
        except:
            messagebox.showwarning(
                "Valor Inválido",
                "Las horas de mantenimiento deben ser un número válido"
            )
            return

        categoria = self.categoria_var.get()

        try:
            # Verificar si ya existe un equipo con ese nombre
            cursor = self.db.cursor.execute(
                "SELECT COUNT(*) FROM productos_equipos WHERE tipo_equipo = ?",
                (tipo_equipo,)
            )
            if cursor.fetchone()[0] > 0:
                messagebox.showwarning(
                    "Equipo Existente",
                    f"Ya existe un equipo con el nombre '{tipo_equipo}'"
                )
                return

            # Insertar equipo
            self.db.cursor.execute('''
                INSERT INTO productos_equipos (
                    tipo_equipo, horas_mantenimiento, categoria, activo
                ) VALUES (?, ?, ?, 1)
            ''', (tipo_equipo, horas, categoria))

            self.db.conn.commit()

            messagebox.showinfo(
                "Exito",
                f"Equipo '{tipo_equipo}' guardado correctamente"
            )

            print(f"Equipo guardado: {tipo_equipo} - {horas}h")

            # Actualizar lista en ventana principal si existe el método
            if hasattr(self.parent, 'cargar_equipos'):
                self.parent.cargar_equipos()

            # Cerrar ventana
            self.cerrar()

        except Exception as e:
            print(f"Error al guardar equipo: {e}")
            messagebox.showerror(
                "Error",
                f"No se pudo guardar el equipo:\n{e}"
            )

    def cancelar(self):
        """Cancela y cierra la ventana"""
        # Verificar si hay datos ingresados
        if self.tipo_equipo_var.get().strip():
            if messagebox.askyesno(
                "Confirmar",
                "Hay datos sin guardar. Deseas salir de todos modos?"
            ):
                self.cerrar()
        else:
            self.cerrar()

    def cerrar(self):
        """Cierra la ventana"""
        self.db.desconectar()
        self.window.destroy()
