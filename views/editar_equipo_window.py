"""
editar_equipo_window.py - Ventana para editar equipo HVAC existente

Permite editar equipos de aire acondicionado:
- Tipo de equipo (nombre/modelo)
- Horas de mantenimiento
- Categoría
- Activar/desactivar
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.database import DatabaseManager


class EditarEquipoWindow:
    """Ventana modal para editar equipo"""

    def __init__(self, parent, id_equipo):
        """
        Inicializa la ventana de edición

        Args:
            parent: Ventana principal
            id_equipo: ID del equipo a editar
        """
        self.parent = parent
        self.id_equipo = id_equipo
        self.window = tk.Toplevel()
        self.window.title("Editar Equipo HVAC")
        self.window.geometry("600x500")
        self.window.resizable(False, False)

        # Hacer ventana modal
        self.window.transient(parent.root if hasattr(parent, 'root') else parent)
        self.window.grab_set()

        # Centrar ventana
        self.centrar_ventana()

        # Conectar a base de datos
        self.db = DatabaseManager()
        self.db.conectar()

        # Cargar datos del equipo
        self.cargar_equipo()

        # Variables del formulario
        self.tipo_equipo_var = tk.StringVar(value=self.equipo[1])
        self.horas_mantenimiento_var = tk.StringVar(value=str(self.equipo[4]))
        self.categoria_var = tk.StringVar(value=self.equipo[2] or '')
        self.activo_var = tk.BooleanVar(value=bool(self.equipo[6]))

        # Crear interfaz
        self.crear_interfaz()

    def centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        self.window.update_idletasks()
        width = 600
        height = 500
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def cargar_equipo(self):
        """Carga los datos del equipo desde la base de datos"""
        try:
            query = "SELECT * FROM productos_equipos WHERE id_equipo = ?"
            result = self.db.ejecutar_query(query, (self.id_equipo,))
            self.equipo = result.fetchone()

            if not self.equipo:
                messagebox.showerror("Error", "No se encontró el equipo")
                self.window.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar equipo:\n{e}")
            self.window.destroy()

    def crear_interfaz(self):
        """Crea la interfaz de la ventana"""
        # Header
        header = tk.Frame(self.window, bg='#2563eb', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Editar Equipo HVAC",
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

        # ID (solo lectura)
        tk.Label(
            form_frame,
            text=f"ID: {self.id_equipo}",
            font=("Arial", 9),
            bg='white',
            fg='#999'
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))

        # Tipo de equipo (obligatorio)
        tk.Label(
            form_frame,
            text="Tipo de Equipo / Modelo *",
            font=("Arial", 10, "bold"),
            bg='white',
            fg='#666'
        ).grid(row=1, column=0, sticky=tk.W, pady=(10, 5))

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

        # Categoría
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

        # Horas de mantenimiento
        tk.Label(
            form_frame,
            text="Horas de Mantenimiento *",
            font=("Arial", 10, "bold"),
            bg='white',
            fg='#666'
        ).grid(row=5, column=0, sticky=tk.W, pady=(10, 5))

        horas_frame = tk.Frame(form_frame, bg='white')
        horas_frame.grid(row=6, column=0, sticky=tk.W, pady=(0, 15))

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

        # Estado (activo/inactivo)
        tk.Label(
            form_frame,
            text="Estado",
            font=("Arial", 10, "bold"),
            bg='white',
            fg='#666'
        ).grid(row=7, column=0, sticky=tk.W, pady=(10, 5))

        tk.Checkbutton(
            form_frame,
            text="Equipo activo (disponible para cotizaciones)",
            variable=self.activo_var,
            font=("Arial", 10),
            bg='white'
        ).grid(row=8, column=0, sticky=tk.W, pady=(0, 15))

        # Nota
        tk.Label(
            form_frame,
            text="* Campos obligatorios",
            font=("Arial", 9),
            bg='white',
            fg='#999'
        ).grid(row=9, column=0, sticky=tk.W, pady=(15, 0))

    def crear_botones(self, parent):
        """Crea los botones de acción"""
        btn_frame = tk.Frame(parent, bg='white')
        btn_frame.pack(fill=tk.X, pady=(20, 0))

        # Botón Eliminar
        tk.Button(
            btn_frame,
            text="Desactivar",
            font=("Arial", 11),
            bg='#ef4444',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            command=self.desactivar_equipo
        ).pack(side=tk.LEFT)

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
            command=self.cerrar
        ).pack(side=tk.RIGHT, padx=(10, 0))

        # Botón Guardar
        tk.Button(
            btn_frame,
            text="Guardar Cambios",
            font=("Arial", 11, "bold"),
            bg='#2563eb',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=30,
            pady=10,
            command=self.guardar_cambios
        ).pack(side=tk.RIGHT)

    def guardar_cambios(self):
        """Guarda los cambios del equipo"""
        tipo_equipo = self.tipo_equipo_var.get().strip()
        horas_str = self.horas_mantenimiento_var.get().strip()

        if not tipo_equipo:
            messagebox.showwarning("Campo Requerido", "El tipo de equipo es obligatorio")
            return

        try:
            horas = float(horas_str)
            if horas < 0:
                raise ValueError()
        except:
            messagebox.showwarning("Valor Inválido", "Las horas deben ser un número válido")
            return

        categoria = self.categoria_var.get()
        activo = 1 if self.activo_var.get() else 0

        try:
            # Actualizar equipo
            self.db.cursor.execute('''
                UPDATE productos_equipos
                SET tipo_equipo = ?, categoria = ?, horas_mantenimiento = ?, activo = ?
                WHERE id_equipo = ?
            ''', (tipo_equipo, categoria, horas, activo, self.id_equipo))

            self.db.conn.commit()

            messagebox.showinfo("Éxito", "Equipo actualizado correctamente")

            # Actualizar tabla en ventana principal
            if hasattr(self.parent, 'cargar_equipos'):
                self.parent.cargar_equipos()

            self.cerrar()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el equipo:\n{e}")

    def desactivar_equipo(self):
        """Desactiva el equipo"""
        if messagebox.askyesno(
            "Confirmar",
            "¿Desactivar este equipo? No aparecerá en las cotizaciones"
        ):
            try:
                self.db.cursor.execute(
                    "UPDATE productos_equipos SET activo = 0 WHERE id_equipo = ?",
                    (self.id_equipo,)
                )
                self.db.conn.commit()

                messagebox.showinfo("Éxito", "Equipo desactivado")

                if hasattr(self.parent, 'cargar_equipos'):
                    self.parent.cargar_equipos()

                self.cerrar()

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo desactivar:\n{e}")

    def cerrar(self):
        """Cierra la ventana"""
        self.db.desconectar()
        self.window.destroy()
