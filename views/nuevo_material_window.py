"""
nuevo_material_window.py - Ventana para agregar nuevo material/repuesto

Permite agregar materiales y repuestos al catálogo:
- Nombre del material
- Precio unitario
- Unidad de medida
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.database import DatabaseManager


class NuevoMaterialWindow:
    """Ventana modal para agregar nuevo material"""

    def __init__(self, parent):
        """
        Inicializa la ventana de nuevo material

        Args:
            parent: Ventana principal que llama a esta ventana
        """
        self.parent = parent
        self.window = tk.Toplevel()
        self.window.title("Nuevo Material/Repuesto")
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
        self.nombre_material_var = tk.StringVar()
        self.precio_unitario_var = tk.StringVar(value="0")
        self.unidad_medida_var = tk.StringVar()

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
        header = tk.Frame(self.window, bg='#10b981', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Nuevo Material/Repuesto",
            font=("Arial", 16, "bold"),
            bg='#10b981',
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
        """Crea el formulario de datos del material"""
        form_frame = tk.Frame(parent, bg='white')
        form_frame.pack(fill=tk.BOTH, expand=True)

        # Nombre del material (obligatorio)
        tk.Label(
            form_frame,
            text="Nombre del Material *",
            font=("Arial", 10, "bold"),
            bg='white',
            fg='#666'
        ).grid(row=0, column=0, sticky=tk.W, pady=(10, 5))

        tk.Label(
            form_frame,
            text="Ejemplo: Refrigerante R410A, Aceite POE, Limpiador Coil, etc.",
            font=("Arial", 9),
            bg='white',
            fg='#999'
        ).grid(row=1, column=0, sticky=tk.W, pady=(0, 5))

        nombre_entry = tk.Entry(
            form_frame,
            textvariable=self.nombre_material_var,
            font=("Arial", 11),
            width=50,
            relief=tk.SOLID,
            bd=1
        )
        nombre_entry.grid(row=2, column=0, sticky=tk.W, pady=(0, 15), ipady=5)
        nombre_entry.focus()

        # Unidad de medida (opcional)
        tk.Label(
            form_frame,
            text="Unidad de Medida",
            font=("Arial", 10, "bold"),
            bg='white',
            fg='#666'
        ).grid(row=3, column=0, sticky=tk.W, pady=(10, 5))

        unidades = [
            'Unidad',
            'Litro',
            'Kilogramo',
            'Galon',
            'Libra',
            'Metro',
            'Paquete',
            'Caja',
            'Botella'
        ]

        unidad_combo = ttk.Combobox(
            form_frame,
            textvariable=self.unidad_medida_var,
            values=unidades,
            font=("Arial", 10),
            width=48,
            state='readonly'
        )
        unidad_combo.grid(row=4, column=0, sticky=tk.W, pady=(0, 15), ipady=3)
        unidad_combo.current(0)

        # Precio unitario (obligatorio)
        tk.Label(
            form_frame,
            text="Precio Unitario *",
            font=("Arial", 10, "bold"),
            bg='white',
            fg='#666'
        ).grid(row=5, column=0, sticky=tk.W, pady=(10, 5))

        tk.Label(
            form_frame,
            text="Precio por unidad/litro/kilogramo (según la unidad de medida)",
            font=("Arial", 9),
            bg='white',
            fg='#999'
        ).grid(row=6, column=0, sticky=tk.W, pady=(0, 5))

        precio_frame = tk.Frame(form_frame, bg='white')
        precio_frame.grid(row=7, column=0, sticky=tk.W, pady=(0, 15))

        tk.Label(
            precio_frame,
            text="$",
            font=("Arial", 11, "bold"),
            bg='white',
            fg='#666'
        ).pack(side=tk.LEFT, padx=(0, 5))

        tk.Entry(
            precio_frame,
            textvariable=self.precio_unitario_var,
            font=("Arial", 11),
            width=15,
            relief=tk.SOLID,
            bd=1
        ).pack(side=tk.LEFT, ipady=5)

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
            text="Guardar Material",
            font=("Arial", 11, "bold"),
            bg='#10b981',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=30,
            pady=10,
            command=self.guardar_material
        ).pack(side=tk.RIGHT)

    def guardar_material(self):
        """Guarda el material en la base de datos"""
        # Validar campos obligatorios
        nombre_material = self.nombre_material_var.get().strip()
        precio_str = self.precio_unitario_var.get().strip()

        if not nombre_material:
            messagebox.showwarning(
                "Campos Incompletos",
                "El nombre del material es obligatorio"
            )
            return

        # Validar precio
        try:
            precio = float(precio_str)
            if precio < 0:
                raise ValueError()
        except:
            messagebox.showwarning(
                "Valor Inválido",
                "El precio unitario debe ser un número válido"
            )
            return

        unidad_medida = self.unidad_medida_var.get()

        try:
            # Verificar si ya existe un material con ese nombre
            cursor = self.db.cursor.execute(
                "SELECT COUNT(*) FROM materiales_repuestos WHERE nombre_material = ?",
                (nombre_material,)
            )
            if cursor.fetchone()[0] > 0:
                messagebox.showwarning(
                    "Material Existente",
                    f"Ya existe un material con el nombre '{nombre_material}'"
                )
                return

            # Insertar material
            self.db.cursor.execute('''
                INSERT INTO materiales_repuestos (
                    nombre_material, precio_unitario, unidad_medida, activo
                ) VALUES (?, ?, ?, 1)
            ''', (nombre_material, precio, unidad_medida))

            self.db.conn.commit()

            messagebox.showinfo(
                "Exito",
                f"Material '{nombre_material}' guardado correctamente"
            )

            print(f"Material guardado: {nombre_material} - ${precio}")

            # Actualizar lista en ventana principal si existe el método
            if hasattr(self.parent, 'cargar_materiales'):
                self.parent.cargar_materiales()

            # Cerrar ventana
            self.cerrar()

        except Exception as e:
            print(f"Error al guardar material: {e}")
            messagebox.showerror(
                "Error",
                f"No se pudo guardar el material:\n{e}"
            )

    def cancelar(self):
        """Cancela y cierra la ventana"""
        # Verificar si hay datos ingresados
        if self.nombre_material_var.get().strip():
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
