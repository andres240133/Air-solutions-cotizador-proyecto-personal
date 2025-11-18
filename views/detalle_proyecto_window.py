"""
detalle_proyecto_window.py - Ventana de Detalle de Proyecto

Permite ver y editar todos los detalles de un proyecto:
- Información general
- Niveles (S100, N1, N2, etc.)
- Items por nivel con costos
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class DetalleProyectoWindow:
    """Ventana de detalle de proyecto"""

    def __init__(self, parent, db, id_proyecto):
        """
        Inicializa la ventana de detalle

        Args:
            parent: Ventana padre
            db: Instancia de DatabaseManager
            id_proyecto: ID del proyecto a mostrar
        """
        self.db = db
        self.id_proyecto = id_proyecto

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Detalle de Proyecto")
        self.dialog.geometry("1400x800")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Centrar ventana
        self.centrar_ventana()

        # Cargar datos del proyecto
        self.cargar_proyecto()

        # Crear interfaz
        self.crear_interfaz()

    def centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        self.dialog.update_idletasks()
        width = 1400
        height = 800
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')

    def cargar_proyecto(self):
        """Carga los datos del proyecto"""
        cursor = self.db.ejecutar_query('''
            SELECT
                p.numero_proyecto, p.nombre_proyecto,
                c.nombre_empresa, p.ubicacion, p.responsable,
                p.estado, p.fecha_inicio, p.descripcion,
                p.subtotal_equipos, p.subtotal_materiales,
                p.subtotal_mano_obra, p.total_proyecto
            FROM proyectos p
            LEFT JOIN clientes c ON p.id_cliente = c.id_cliente
            WHERE p.id_proyecto = ?
        ''', (self.id_proyecto,))

        self.proyecto = cursor.fetchone()

        if not self.proyecto:
            messagebox.showerror("Error", "Proyecto no encontrado")
            self.dialog.destroy()
            return

    def crear_interfaz(self):
        """Crea la interfaz de la ventana"""
        # Header con información del proyecto
        header = tk.Frame(self.dialog, bg='#1e293b')
        header.pack(fill=tk.X)

        info_frame = tk.Frame(header, bg='#1e293b')
        info_frame.pack(fill=tk.X, padx=20, pady=15)

        # Título
        tk.Label(
            info_frame,
            text=f"{self.proyecto[0]} - {self.proyecto[1]}",
            font=("Arial", 16, "bold"),
            bg='#1e293b',
            fg='white'
        ).pack(anchor='w')

        # Info secundaria
        info_text = f"Cliente: {self.proyecto[2] or 'N/A'}"
        if self.proyecto[3]:
            info_text += f"  |  Ubicación: {self.proyecto[3]}"
        if self.proyecto[4]:
            info_text += f"  |  Responsable: {self.proyecto[4]}"

        tk.Label(
            info_frame,
            text=info_text,
            font=("Arial", 10),
            bg='#1e293b',
            fg='#cbd5e1'
        ).pack(anchor='w', pady=(5, 0))

        # Botones de acción
        btn_frame = tk.Frame(header, bg='#1e293b')
        btn_frame.pack(fill=tk.X, padx=20, pady=(0, 15))

        tk.Button(
            btn_frame,
            text="➕ Nuevo Nivel",
            font=("Arial", 10),
            bg='#10b981',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=self.nuevo_nivel
        ).pack(side=tk.LEFT, padx=(0, 5))

        tk.Button(
            btn_frame,
            text="➕ Nuevo Item",
            font=("Arial", 10),
            bg='#3b82f6',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=self.nuevo_item
        ).pack(side=tk.LEFT, padx=(0, 5))

        tk.Button(
            btn_frame,
            text="🔄 Actualizar",
            font=("Arial", 10),
            bg='#6b7280',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=self.actualizar_datos
        ).pack(side=tk.LEFT, padx=(0, 5))

        tk.Button(
            btn_frame,
            text="📊 Exportar Excel",
            font=("Arial", 10),
            bg='#f59e0b',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=self.exportar_excel
        ).pack(side=tk.LEFT)

        # Total del proyecto
        total_frame = tk.Frame(btn_frame, bg='#10b981', relief=tk.RAISED, bd=2)
        total_frame.pack(side=tk.RIGHT)

        tk.Label(
            total_frame,
            text=f"TOTAL PROYECTO: ${self.proyecto[11]:,.2f}" if self.proyecto[11] else "TOTAL PROYECTO: $0.00",
            font=("Arial", 12, "bold"),
            bg='#10b981',
            fg='white',
            padx=20,
            pady=5
        ).pack()

        # Contenedor principal con pestañas
        main_container = tk.Frame(self.dialog, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True)

        # Notebook (pestañas)
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Pestaña 1: Niveles e Items
        tab_niveles = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab_niveles, text='  📋 Niveles e Items  ')
        self.crear_tab_niveles(tab_niveles)

        # Pestaña 2: Cotizaciones
        tab_cotizaciones = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab_cotizaciones, text='  💼 Cotizaciones del Proyecto  ')
        self.crear_tab_cotizaciones(tab_cotizaciones)

    def crear_tab_niveles(self, parent):
        """Crea la pestaña de niveles e items"""
        # Panel izquierdo - Niveles
        left_panel = tk.Frame(parent, bg='white', width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(10, 5), pady=10)
        left_panel.pack_propagate(False)

        tk.Label(
            left_panel,
            text="Niveles/Áreas",
            font=("Arial", 12, "bold"),
            bg='white'
        ).pack(anchor='w', pady=(0, 10))

        # Lista de niveles
        niveles_frame = tk.Frame(left_panel, bg='white')
        niveles_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar_niveles = ttk.Scrollbar(niveles_frame)
        scrollbar_niveles.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_niveles = ttk.Treeview(
            niveles_frame,
            columns=('Código', 'Nombre', 'Total'),
            show='headings',
            yscrollcommand=scrollbar_niveles.set,
            selectmode='browse'
        )

        self.tree_niveles.heading('Código', text='Código')
        self.tree_niveles.heading('Nombre', text='Nombre')
        self.tree_niveles.heading('Total', text='Total')

        self.tree_niveles.column('Código', width=80)
        self.tree_niveles.column('Nombre', width=130)
        self.tree_niveles.column('Total', width=90)

        self.tree_niveles.pack(fill=tk.BOTH, expand=True)
        scrollbar_niveles.config(command=self.tree_niveles.yview)

        # Evento de selección
        self.tree_niveles.bind('<<TreeviewSelect>>', self.on_nivel_seleccionado)
        self.tree_niveles.bind('<Button-3>', self.menu_nivel)

        # Panel derecho - Items
        right_panel = tk.Frame(parent, bg='white')
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 10), pady=10)

        tk.Label(
            right_panel,
            text="Items del Nivel",
            font=("Arial", 12, "bold"),
            bg='white'
        ).pack(anchor='w', pady=(0, 10))

        # Tabla de items
        items_frame = tk.Frame(right_panel, bg='white')
        items_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar_items = ttk.Scrollbar(items_frame)
        scrollbar_items.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_items = ttk.Treeview(
            items_frame,
            columns=('Espec', 'Descripción', 'Cant', 'Unidad', 'C.Equipo', 'C.Materiales', 'C.ManoObra', 'Total'),
            show='headings',
            yscrollcommand=scrollbar_items.set
        )

        self.tree_items.heading('Espec', text='Especificación')
        self.tree_items.heading('Descripción', text='Descripción')
        self.tree_items.heading('Cant', text='Cant.')
        self.tree_items.heading('Unidad', text='Unidad')
        self.tree_items.heading('C.Equipo', text='Costo Equipo')
        self.tree_items.heading('C.Materiales', text='Costo Materiales')
        self.tree_items.heading('C.ManoObra', text='Costo Mano Obra')
        self.tree_items.heading('Total', text='Total')

        self.tree_items.column('Espec', width=120)
        self.tree_items.column('Descripción', width=200)
        self.tree_items.column('Cant', width=60)
        self.tree_items.column('Unidad', width=80)
        self.tree_items.column('C.Equipo', width=100)
        self.tree_items.column('C.Materiales', width=120)
        self.tree_items.column('C.ManoObra', width=120)
        self.tree_items.column('Total', width=100)

        self.tree_items.pack(fill=tk.BOTH, expand=True)
        scrollbar_items.config(command=self.tree_items.yview)

        # Evento doble clic para editar
        self.tree_items.bind('<Double-1>', self.editar_item)
        self.tree_items.bind('<Button-3>', self.menu_item)

        # Cargar datos
        self.cargar_niveles()

    def crear_tab_cotizaciones(self, parent):
        """Crea la pestaña de cotizaciones del proyecto"""
        # Header
        header_frame = tk.Frame(parent, bg='white')
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))

        tk.Label(
            header_frame,
            text="Cotizaciones del Proyecto",
            font=("Arial", 14, "bold"),
            bg='white'
        ).pack(side=tk.LEFT)

        tk.Button(
            header_frame,
            text="➕ Nueva Cotización",
            font=("Arial", 10),
            bg='#10b981',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=self.nueva_cotizacion
        ).pack(side=tk.RIGHT, padx=(5, 0))

        tk.Button(
            header_frame,
            text="🔄 Actualizar",
            font=("Arial", 10),
            bg='#6b7280',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=self.cargar_cotizaciones_proyecto
        ).pack(side=tk.RIGHT)

        # Info
        info_label = tk.Label(
            parent,
            text="Aquí puedes crear cotizaciones específicas para este proyecto (rutas eléctricas, instalaciones específicas, etc.)",
            font=("Arial", 9),
            bg='#f3f4f6',
            fg='#6b7280',
            wraplength=1300,
            justify=tk.LEFT,
            padx=15,
            pady=10
        )
        info_label.pack(fill=tk.X, padx=20, pady=(0, 15))

        # Tabla de cotizaciones
        table_frame = tk.Frame(parent, bg='white')
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_cotizaciones = ttk.Treeview(
            table_frame,
            columns=('Número', 'Tipo', 'Fecha', 'Estado', 'Subtotal', 'IVA', 'Total'),
            show='headings',
            yscrollcommand=scrollbar.set
        )

        self.tree_cotizaciones.heading('Número', text='Número')
        self.tree_cotizaciones.heading('Tipo', text='Tipo de Servicio')
        self.tree_cotizaciones.heading('Fecha', text='Fecha Emisión')
        self.tree_cotizaciones.heading('Estado', text='Estado')
        self.tree_cotizaciones.heading('Subtotal', text='Subtotal')
        self.tree_cotizaciones.heading('IVA', text='IVA')
        self.tree_cotizaciones.heading('Total', text='Total')

        self.tree_cotizaciones.column('Número', width=120)
        self.tree_cotizaciones.column('Tipo', width=250)
        self.tree_cotizaciones.column('Fecha', width=120)
        self.tree_cotizaciones.column('Estado', width=120)
        self.tree_cotizaciones.column('Subtotal', width=120)
        self.tree_cotizaciones.column('IVA', width=100)
        self.tree_cotizaciones.column('Total', width=120)

        self.tree_cotizaciones.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree_cotizaciones.yview)

        # Eventos
        self.tree_cotizaciones.bind('<Double-1>', self.ver_cotizacion)
        self.tree_cotizaciones.bind('<Button-3>', self.menu_cotizacion_proyecto)

        # Cargar cotizaciones
        self.cargar_cotizaciones_proyecto()

    def cargar_niveles(self):
        """Carga los niveles del proyecto"""
        # Limpiar tabla
        for item in self.tree_niveles.get_children():
            self.tree_niveles.delete(item)

        # Cargar niveles
        cursor = self.db.ejecutar_query('''
            SELECT id_nivel, codigo_nivel, nombre_nivel, total_nivel
            FROM proyecto_niveles
            WHERE id_proyecto = ?
            ORDER BY orden, codigo_nivel
        ''', (self.id_proyecto,))

        niveles = cursor.fetchall()

        for nivel in niveles:
            id_nivel, codigo, nombre, total = nivel
            total_str = f'${total:,.2f}' if total else '$0.00'

            self.tree_niveles.insert('', 'end', values=(
                codigo, nombre, total_str
            ), tags=(id_nivel,))

    def on_nivel_seleccionado(self, event):
        """Evento cuando se selecciona un nivel"""
        selection = self.tree_niveles.selection()
        if not selection:
            return

        item = self.tree_niveles.item(selection[0])
        id_nivel = item['tags'][0]

        self.cargar_items(id_nivel)

    def cargar_items(self, id_nivel):
        """Carga los items de un nivel"""
        # Limpiar tabla
        for item in self.tree_items.get_children():
            self.tree_items.delete(item)

        # Cargar items
        cursor = self.db.ejecutar_query('''
            SELECT
                id_item, especificacion, descripcion, cantidad,
                unidad, costo_equipo, costo_materiales,
                costo_mano_obra, total_item
            FROM proyecto_items
            WHERE id_nivel = ?
            ORDER BY orden, especificacion
        ''', (id_nivel,))

        items = cursor.fetchall()

        for item in items:
            (id_item, espec, desc, cant, unidad, c_equipo,
             c_materiales, c_mano_obra, total) = item

            self.tree_items.insert('', 'end', values=(
                espec,
                desc or '-',
                cant,
                unidad,
                f'${c_equipo:,.2f}',
                f'${c_materiales:,.2f}',
                f'${c_mano_obra:,.2f}',
                f'${total:,.2f}' if total else '$0.00'
            ), tags=(id_item,))

    def nuevo_nivel(self):
        """Abre ventana para crear nuevo nivel"""
        from views.nuevo_nivel_window import NuevoNivelWindow
        ventana = NuevoNivelWindow(self.dialog, self.db, self.id_proyecto)
        self.dialog.wait_window(ventana.dialog)
        self.actualizar_datos()

    def nuevo_item(self):
        """Abre ventana para crear nuevo item"""
        # Verificar que haya un nivel seleccionado
        selection = self.tree_niveles.selection()
        if not selection:
            messagebox.showwarning(
                "Nivel Requerido",
                "Primero selecciona un nivel donde agregar el item"
            )
            return

        item = self.tree_niveles.item(selection[0])
        id_nivel = item['tags'][0]

        from views.nuevo_item_window import NuevoItemWindow
        ventana = NuevoItemWindow(self.dialog, self.db, id_nivel)
        self.dialog.wait_window(ventana.dialog)
        self.actualizar_datos()

    def editar_item(self, event):
        """Edita un item"""
        selection = self.tree_items.selection()
        if not selection:
            return

        item = self.tree_items.item(selection[0])
        id_item = item['tags'][0]

        from views.editar_item_window import EditarItemWindow
        ventana = EditarItemWindow(self.dialog, self.db, id_item)
        self.dialog.wait_window(ventana.dialog)
        self.actualizar_datos()

    def menu_nivel(self, event):
        """Menú contextual para niveles"""
        selection = self.tree_niveles.selection()
        if not selection:
            return

        menu = tk.Menu(self.dialog, tearoff=0)
        menu.add_command(label="✏️ Editar Nivel", command=self.editar_nivel)
        menu.add_separator()
        menu.add_command(label="🗑️ Eliminar Nivel", command=self.eliminar_nivel)

        menu.post(event.x_root, event.y_root)

    def menu_item(self, event):
        """Menú contextual para items"""
        selection = self.tree_items.selection()
        if not selection:
            return

        menu = tk.Menu(self.dialog, tearoff=0)
        menu.add_command(label="✏️ Editar Item", command=lambda: self.editar_item(None))
        menu.add_separator()
        menu.add_command(label="🗑️ Eliminar Item", command=self.eliminar_item)

        menu.post(event.x_root, event.y_root)

    def editar_nivel(self):
        """Edita un nivel"""
        selection = self.tree_niveles.selection()
        if not selection:
            return

        item = self.tree_niveles.item(selection[0])
        id_nivel = item['tags'][0]

        from views.editar_nivel_window import EditarNivelWindow
        ventana = EditarNivelWindow(self.dialog, self.db, id_nivel)
        self.dialog.wait_window(ventana.dialog)
        self.actualizar_datos()

    def eliminar_nivel(self):
        """Elimina un nivel"""
        selection = self.tree_niveles.selection()
        if not selection:
            return

        item = self.tree_niveles.item(selection[0])
        codigo_nivel = item['values'][0]
        id_nivel = item['tags'][0]

        if messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Eliminar el nivel {codigo_nivel}?\n\n"
            "Se eliminarán también todos los items del nivel.\n"
            "Esta acción no se puede deshacer."
        ):
            try:
                self.db.ejecutar_query(
                    'DELETE FROM proyecto_niveles WHERE id_nivel = ?',
                    (id_nivel,)
                )
                self.actualizar_datos()
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar nivel:\n{e}")

    def eliminar_item(self):
        """Elimina un item"""
        selection = self.tree_items.selection()
        if not selection:
            return

        item = self.tree_items.item(selection[0])
        especificacion = item['values'][0]
        id_item = item['tags'][0]

        if messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Eliminar el item {especificacion}?\n\n"
            "Esta acción no se puede deshacer."
        ):
            try:
                self.db.ejecutar_query(
                    'DELETE FROM proyecto_items WHERE id_item = ?',
                    (id_item,)
                )
                self.actualizar_datos()
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar item:\n{e}")

    def actualizar_datos(self):
        """Actualiza todos los datos de la ventana"""
        # Recalcular totales
        self.recalcular_totales()

        # Recargar datos del proyecto
        self.cargar_proyecto()

        # Recargar niveles
        self.cargar_niveles()

        # Si hay un nivel seleccionado, recargar sus items
        selection = self.tree_niveles.selection()
        if selection:
            item = self.tree_niveles.item(selection[0])
            id_nivel = item['tags'][0]
            self.cargar_items(id_nivel)

        # Actualizar total en header
        for widget in self.dialog.winfo_children():
            if isinstance(widget, tk.Frame) and widget.cget('bg') == '#1e293b':
                # Es el header, actualizar el total
                break

    def recalcular_totales(self):
        """Recalcula todos los totales del proyecto"""
        # Recalcular totales de items en cada nivel
        self.db.ejecutar_query('''
            UPDATE proyecto_items
            SET total_item = (costo_equipo + costo_materiales + costo_mano_obra) * cantidad
            WHERE id_item IN (
                SELECT id_item FROM proyecto_items pi
                JOIN proyecto_niveles pn ON pi.id_nivel = pn.id_nivel
                WHERE pn.id_proyecto = ?
            )
        ''', (self.id_proyecto,))

        # Recalcular totales de niveles
        self.db.ejecutar_query('''
            UPDATE proyecto_niveles
            SET
                subtotal_equipos = (
                    SELECT COALESCE(SUM(costo_equipo * cantidad), 0)
                    FROM proyecto_items
                    WHERE id_nivel = proyecto_niveles.id_nivel
                ),
                subtotal_materiales = (
                    SELECT COALESCE(SUM(costo_materiales * cantidad), 0)
                    FROM proyecto_items
                    WHERE id_nivel = proyecto_niveles.id_nivel
                ),
                subtotal_mano_obra = (
                    SELECT COALESCE(SUM(costo_mano_obra * cantidad), 0)
                    FROM proyecto_items
                    WHERE id_nivel = proyecto_niveles.id_nivel
                ),
                total_nivel = (
                    SELECT COALESCE(SUM(total_item), 0)
                    FROM proyecto_items
                    WHERE id_nivel = proyecto_niveles.id_nivel
                )
            WHERE id_proyecto = ?
        ''', (self.id_proyecto,))

        # Recalcular total del proyecto
        self.db.ejecutar_query('''
            UPDATE proyectos
            SET
                subtotal_equipos = (
                    SELECT COALESCE(SUM(subtotal_equipos), 0)
                    FROM proyecto_niveles
                    WHERE id_proyecto = proyectos.id_proyecto
                ),
                subtotal_materiales = (
                    SELECT COALESCE(SUM(subtotal_materiales), 0)
                    FROM proyecto_niveles
                    WHERE id_proyecto = proyectos.id_proyecto
                ),
                subtotal_mano_obra = (
                    SELECT COALESCE(SUM(subtotal_mano_obra), 0)
                    FROM proyecto_niveles
                    WHERE id_proyecto = proyectos.id_proyecto
                ),
                total_proyecto = (
                    SELECT COALESCE(SUM(total_nivel), 0)
                    FROM proyecto_niveles
                    WHERE id_proyecto = proyectos.id_proyecto
                )
            WHERE id_proyecto = ?
        ''', (self.id_proyecto,))

    def exportar_excel(self):
        """Exporta el proyecto a Excel"""
        try:
            from utils.excel_manager import ExcelManager
            excel_manager = ExcelManager(self.db)

            ruta = excel_manager.exportar_proyecto(self.id_proyecto)

            if ruta:
                if messagebox.askyesno(
                    "Exportación Exitosa",
                    f"Proyecto exportado a:\n{ruta}\n\n¿Abrir el archivo?"
                ):
                    os.startfile(ruta)
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar:\n{e}")

    # ===== MÉTODOS PARA COTIZACIONES =====

    def cargar_cotizaciones_proyecto(self):
        """Carga las cotizaciones del proyecto"""
        # Limpiar tabla
        for item in self.tree_cotizaciones.get_children():
            self.tree_cotizaciones.delete(item)

        # Cargar cotizaciones vinculadas a este proyecto
        cursor = self.db.ejecutar_query('''
            SELECT
                id_cotizacion, numero_cotizacion, tipo_servicio,
                fecha_emision, estado, subtotal, total_iva, total
            FROM cotizaciones
            WHERE id_proyecto = ?
            ORDER BY fecha_creacion DESC
        ''', (self.id_proyecto,))

        cotizaciones = cursor.fetchall()

        for cot in cotizaciones:
            (id_cot, numero, tipo, fecha, estado, subtotal,
             iva, total) = cot

            # Formatear valores
            tipo_str = tipo or 'Sin especificar'
            fecha_str = fecha or '-'

            # Traducir estado
            estados_traduccion = {
                'pendiente': 'Pendiente',
                'aprobada': 'Aprobada',
                'rechazada': 'Rechazada',
                'facturada': 'Facturada'
            }
            estado_str = estados_traduccion.get(estado, estado)

            subtotal_str = f'${subtotal:,.2f}' if subtotal else '$0.00'
            iva_str = f'${iva:,.2f}' if iva else '$0.00'
            total_str = f'${total:,.2f}' if total else '$0.00'

            self.tree_cotizaciones.insert('', 'end', values=(
                numero, tipo_str, fecha_str, estado_str,
                subtotal_str, iva_str, total_str
            ), tags=(id_cot,))

    def nueva_cotizacion(self):
        """Crea una nueva cotización para este proyecto"""
        # Obtener información del proyecto para prellenar
        cursor = self.db.ejecutar_query('''
            SELECT id_cliente, numero_proyecto
            FROM proyectos
            WHERE id_proyecto = ?
        ''', (self.id_proyecto,))

        proyecto_info = cursor.fetchone()
        if not proyecto_info:
            messagebox.showerror("Error", "No se pudo obtener información del proyecto")
            return

        id_cliente, numero_proyecto = proyecto_info

        # Importar y abrir ventana de nueva cotización
        from views.nueva_cotizacion_window import NuevaCotizacionWindow
        ventana = NuevaCotizacionWindow(
            self.dialog,
            self.db,
            id_cliente_preseleccionado=id_cliente,
            id_proyecto=self.id_proyecto,
            descripcion_proyecto=f"Proyecto: {numero_proyecto}"
        )
        self.dialog.wait_window(ventana.dialog)

        # Recargar cotizaciones
        self.cargar_cotizaciones_proyecto()

    def ver_cotizacion(self, event):
        """Ver detalle de una cotización"""
        selection = self.tree_cotizaciones.selection()
        if not selection:
            return

        item = self.tree_cotizaciones.item(selection[0])
        id_cotizacion = item['tags'][0]

        # Abrir ventana de detalle
        from views.detalle_cotizacion_window import DetalleCotizacionWindow
        ventana = DetalleCotizacionWindow(self.dialog, self.db, id_cotizacion)
        self.dialog.wait_window(ventana.dialog)

        # Recargar cotizaciones
        self.cargar_cotizaciones_proyecto()

    def menu_cotizacion_proyecto(self, event):
        """Menú contextual para cotizaciones"""
        selection = self.tree_cotizaciones.selection()
        if not selection:
            return

        menu = tk.Menu(self.dialog, tearoff=0)
        menu.add_command(label="📄 Ver Detalle", command=lambda: self.ver_cotizacion(None))
        menu.add_separator()
        menu.add_command(label="🗑️ Eliminar Cotización", command=self.eliminar_cotizacion_proyecto)

        menu.post(event.x_root, event.y_root)

    def eliminar_cotizacion_proyecto(self):
        """Elimina una cotización del proyecto"""
        selection = self.tree_cotizaciones.selection()
        if not selection:
            messagebox.showwarning("Selección Requerida", "Selecciona una cotización para eliminar")
            return

        item = self.tree_cotizaciones.item(selection[0])
        numero = item['values'][0]
        id_cotizacion = item['tags'][0]

        if messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Estás seguro de eliminar la cotización {numero}?\n\n"
            "Esta acción no se puede deshacer."
        ):
            try:
                self.db.ejecutar_query(
                    'DELETE FROM cotizaciones WHERE id_cotizacion = ?',
                    (id_cotizacion,)
                )
                messagebox.showinfo("Éxito", "Cotización eliminada correctamente")
                self.cargar_cotizaciones_proyecto()
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar cotización:\n{e}")
