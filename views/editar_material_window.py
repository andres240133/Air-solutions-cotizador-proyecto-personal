"""
editar_material_window.py - Ventana para editar material/repuesto existente

Permite editar materiales y repuestos:
- Nombre del material
- Precio unitario
- Unidad de medida
- Activar/desactivar
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.database import DatabaseManager


class EditarMaterialWindow:
    """Ventana modal para editar material"""

    def __init__(self, parent, id_material):
        """
        Inicializa la ventana de edición

        Args:
            parent: Ventana principal
            id_material: ID del material a editar
        """
        self.parent = parent
        self.id_material = id_material
        self.window = tk.Toplevel()
        self.window.title("Editar Material/Repuesto")
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

        # Cargar datos del material
        self.cargar_material()

        # Variables del formulario
        self.nombre_material_var = tk.StringVar(value=self.material[1])
        self.precio_unitario_var = tk.StringVar(value=str(self.material[2]))
        self.unidad_medida_var = tk.StringVar(value=self.material[3] or 'Unidad')
        self.activo_var = tk.BooleanVar(value=bool(self.material[4]))

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

    def cargar_material(self):
        """Carga los datos del material desde la base de datos"""
        try:
            query = "SELECT * FROM materiales_repuestos WHERE id_material = ?"
            result = self.db.ejecutar_query(query, (self.id_material,))
            self.material = result.fetchone()

            if not self.material:
                messagebox.showerror("Error", "No se encontró el material")
                self.window.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar material:\n{e}")
            self.window.destroy()

    def crear_interfaz(self):
        """Crea la interfaz de la ventana"""
        # Header
        header = tk.Frame(self.window, bg='#10b981', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Editar Material/Repuesto",
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

        # ID (solo lectura)
        tk.Label(
            form_frame,
            text=f"ID: {self.id_material}",
            font=("Arial", 9),
            bg='white',
            fg='#999'
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))

        # Nombre del material
        tk.Label(
            form_frame,
            text="Nombre del Material *",
            font=("Arial", 10, "bold"),
            bg='white',
            fg='#666'
        ).grid(row=1, column=0, sticky=tk.W, pady=(10, 5))

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

        # Unidad de medida
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

        # Precio unitario
        tk.Label(
            form_frame,
            text="Precio Unitario *",
            font=("Arial", 10, "bold"),
            bg='white',
            fg='#666'
        ).grid(row=5, column=0, sticky=tk.W, pady=(10, 5))

        precio_frame = tk.Frame(form_frame, bg='white')
        precio_frame.grid(row=6, column=0, sticky=tk.W, pady=(0, 15))

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
            text="Material activo (disponible para cotizaciones)",
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

        # Botón Desactivar
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
            command=self.desactivar_material
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
            bg='#10b981',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=30,
            pady=10,
            command=self.guardar_cambios
        ).pack(side=tk.RIGHT)

    def guardar_cambios(self):
        """Guarda los cambios del material"""
        nombre_material = self.nombre_material_var.get().strip()
        precio_str = self.precio_unitario_var.get().strip()

        if not nombre_material:
            messagebox.showwarning("Campo Requerido", "El nombre del material es obligatorio")
            return

        try:
            precio = float(precio_str)
            if precio < 0:
                raise ValueError()
        except:
            messagebox.showwarning("Valor Inválido", "El precio debe ser un número válido")
            return

        unidad_medida = self.unidad_medida_var.get()
        activo = 1 if self.activo_var.get() else 0

        try:
            # Actualizar material
            self.db.cursor.execute('''
                UPDATE materiales_repuestos
                SET nombre_material = ?, precio_unitario = ?, unidad_medida = ?, activo = ?
                WHERE id_material = ?
            ''', (nombre_material, precio, unidad_medida, activo, self.id_material))

            self.db.conn.commit()

            messagebox.showinfo("Éxito", "Material actualizado correctamente")

            # Actualizar tabla en ventana principal
            if hasattr(self.parent, 'cargar_materiales'):
                self.parent.cargar_materiales()

            self.cerrar()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el material:\n{e}")

    def desactivar_material(self):
        """Desactiva el material"""
        if messagebox.askyesno(
            "Confirmar",
            "¿Desactivar este material? No aparecerá en las cotizaciones"
        ):
            try:
                self.db.cursor.execute(
                    "UPDATE materiales_repuestos SET activo = 0 WHERE id_material = ?",
                    (self.id_material,)
                )
                self.db.conn.commit()

                messagebox.showinfo("Éxito", "Material desactivado")

                if hasattr(self.parent, 'cargar_materiales'):
                    self.parent.cargar_materiales()

                self.cerrar()

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo desactivar:\n{e}")

    def cerrar(self):
        """Cierra la ventana"""
        self.db.desconectar()
        self.window.destroy()
