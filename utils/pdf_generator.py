"""
pdf_generator.py - Generador de PDFs Profesionales para Cotizaciones

Genera ofertas formales de mantenimiento con formato profesional
similar a las cotizaciones oficiales de AirSolutions
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY


class PDFCotizacionProfesional:
    """Generador de PDFs con formato profesional"""

    def __init__(self, data):
        """
        Inicializa el generador de PDF

        Args:
            data: Diccionario con los datos de la cotización
        """
        self.data = data
        self.styles = getSampleStyleSheet()
        self._crear_estilos_personalizados()

        # Rutas de logos
        self.logo_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'resources', 'images', 'logo.jpg'
        )

    def _crear_estilos_personalizados(self):
        """Crea estilos personalizados para el documento"""

        # Título principal
        self.styles.add(ParagraphStyle(
            name='TituloPrincipal',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Subtítulo
        self.styles.add(ParagraphStyle(
            name='Subtitulo',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2563eb'),
            spaceAfter=10,
            fontName='Helvetica-Bold'
        ))

        # Texto normal
        self.styles.add(ParagraphStyle(
            name='TextoNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=6
        ))

        # Texto pequeño
        self.styles.add(ParagraphStyle(
            name='TextoPequeño',
            parent=self.styles['Normal'],
            fontSize=9,
            alignment=TA_LEFT
        ))

    def generar(self, output_path):
        """
        Genera el PDF completo

        Args:
            output_path: Ruta donde guardar el PDF

        Returns:
            bool: True si se generó correctamente
        """
        try:
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Crear documento
            doc = SimpleDocTemplate(
                output_path,
                pagesize=letter,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=0.5*inch,
                bottomMargin=0.5*inch
            )

            # Construir contenido
            story = []

            # Página 1: Portada con descripción del servicio
            story.extend(self._crear_portada())
            story.append(PageBreak())

            # Páginas 2-3: Detalle técnico del mantenimiento
            story.extend(self._crear_detalle_tecnico())
            story.append(PageBreak())

            # Página 4: Propuesta económica
            story.extend(self._crear_propuesta_economica())
            story.append(PageBreak())

            # Página 5: Notas y firma
            story.extend(self._crear_notas_firma())

            # Generar PDF
            doc.build(story, onFirstPage=self._agregar_encabezado_pie,
                     onLaterPages=self._agregar_encabezado_pie)

            print(f"[OK] PDF generado: {output_path}")
            return True

        except Exception as e:
            print(f"Error al generar PDF: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _agregar_encabezado_pie(self, canvas, doc):
        """Agrega encabezado y pie de página a cada página"""
        canvas.saveState()

        # Encabezado con logo
        if os.path.exists(self.logo_path):
            try:
                canvas.drawImage(self.logo_path, 0.75*inch, letter[1] - 1*inch,
                               width=1.2*inch, height=0.8*inch, preserveAspectRatio=True)
            except:
                pass

        # Texto del encabezado
        canvas.setFont('Helvetica-Bold', 14)
        canvas.setFillColor(colors.HexColor('#1e40af'))
        canvas.drawString(2.2*inch, letter[1] - 0.7*inch, "AIR SOLUTIONS")

        # Pie de página con línea azul
        canvas.setStrokeColor(colors.HexColor('#2563eb'))
        canvas.setLineWidth(3)
        canvas.line(0.75*inch, 0.6*inch, letter[0] - 0.75*inch, 0.6*inch)

        # Información del pie
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#666666'))
        canvas.drawCentredString(letter[0]/2, 0.4*inch, "WWW.AIRSOLUTIONSCR.COM")
        canvas.drawCentredString(letter[0]/2, 0.25*inch, "Escazú, San José, Costa Rica | INFO@AIRSOLUTIONSCR.COM")

        canvas.restoreState()

    def _crear_portada(self):
        """Crea la portada con información del servicio"""
        elementos = []

        # Espacio después del logo
        elementos.append(Spacer(1, 0.5*inch))

        # Número de cotización
        elementos.append(Paragraph(
            f"<b>{self.data['numero_cotizacion']}</b>",
            self.styles['TituloPrincipal']
        ))

        # Título del servicio
        titulo_servicio = f"{self.data.get('tipo_servicio', 'Mantenimiento Preventivo')}"
        elementos.append(Paragraph(
            f"<b>{titulo_servicio}</b>",
            self.styles['Subtitulo']
        ))

        elementos.append(Spacer(1, 0.3*inch))

        # Información del cliente y fecha
        info_text = f"""
        <b>{self.data.get('direccion_cliente', 'Dirección del cliente')}</b><br/>
        {datetime.now().strftime('%d de %B de %Y')}
        """
        elementos.append(Paragraph(info_text, self.styles['TextoNormal']))

        elementos.append(Spacer(1, 0.2*inch))

        # Saludo
        elementos.append(Paragraph(
            f"<b>Atención {self.data['cliente']}</b>",
            self.styles['TextoNormal']
        ))

        elementos.append(Spacer(1, 0.2*inch))

        # Descripción del servicio
        descripcion = f"""
        Por medio del presente documento Air Solutions se complace en presentar la oferta por
        el servicio de mantenimiento preventivo del Chiller y dos bombas ubicados en {self.data['cliente']},
        a continuación, el detalle de los equipos:
        """
        elementos.append(Paragraph(descripcion, self.styles['TextoNormal']))

        elementos.append(Spacer(1, 0.2*inch))

        # Lista de equipos
        equipos_text = self._generar_lista_equipos()
        elementos.append(Paragraph(equipos_text, self.styles['TextoNormal']))

        elementos.append(Spacer(1, 0.2*inch))

        # El mantenimiento incluye
        elementos.append(Paragraph(
            "<b>El mantenimiento incluye:</b>",
            self.styles['Subtitulo']
        ))

        return elementos

    def _generar_lista_equipos(self):
        """Genera la lista de equipos incluidos en la cotización"""
        equipos = self.data.get('equipos', [])

        if not equipos:
            return "• <b>Equipos a cotizar</b>"

        lista_html = ""
        for equipo in equipos:
            nombre = equipo[0] if len(equipo) > 0 else "Equipo"
            cantidad = equipo[1] if len(equipo) > 1 else 1
            lista_html += f"• <b>{cantidad} {nombre.upper()}</b><br/>"

        return lista_html

    def _crear_detalle_tecnico(self):
        """Crea las páginas con el detalle técnico del mantenimiento"""
        elementos = []

        elementos.append(Paragraph("<b>Evaporador</b>", self.styles['Subtitulo']))
        elementos.append(Paragraph("<u>Procedimientos Misceláneos:</u>", self.styles['TextoNormal']))

        procedimientos_evaporador = [
            "Limpieza de filtro de retorno de aire.",
            "Limpieza de bandeja de recolección de condensados.",
            "Limpieza de drenajes de condensación mediante soplado de aire o agua o desbloqueo con sonda.",
            "Verificación de sifón de drenaje, revisar que esté bien figurado.",
            "Limpieza de consola de la unidad, en su defecto limpieza de difusores y rejillas de retorno.",
            "Limpieza de serpentín: Soplado, lavado o aplicación de químico en bases alcalinas biodegradable. " +
            "En algunos casos el bloqueo o incrustación del serpentín por suciedad se debe considerar como " +
            "procedimiento de reparación y no de mantenimiento.",
            "Limpieza y/o lavado de turbinas o \"Blower\" de evaporador.",
            "Cambio o reposición de tornillos deteriorados en gabinetes de equipos.",
            "Verificación de temperatura del suministro de caudal de aire."
        ]

        for proc in procedimientos_evaporador:
            elementos.append(Paragraph(f"➤ {proc}", self.styles['TextoPequeño']))
            elementos.append(Spacer(1, 4))

        elementos.append(Spacer(1, 0.2*inch))

        # Verificación de condiciones de serpentín
        elementos.append(Paragraph(
            "<u>Verificación de condiciones de serpentín de evaporación:</u>",
            self.styles['TextoNormal']
        ))

        verificaciones = [
            "Verificación y diagnóstico de presencia de escarcha o congelamiento en líneas de refrigerante.",
            "Verificación y diagnóstico de presencia de escarcha o congelamiento en serpentín de evaporación.",
            "Verificación de uniformidad de llenado del serpentín.",
            "Verificación de nivel de abolladuras, ruptura o deterioro por aplicación de ácido a las " +
            "aletas de aluminio del serpentín."
        ]

        for verif in verificaciones:
            elementos.append(Paragraph(f"➤ {verif}", self.styles['TextoPequeño']))
            elementos.append(Spacer(1, 4))

        return elementos

    def _crear_propuesta_economica(self):
        """Crea la página con la propuesta económica"""
        elementos = []

        elementos.append(Spacer(1, 0.3*inch))

        elementos.append(Paragraph("<b>Propuesta económica:</b>", self.styles['Subtitulo']))

        elementos.append(Spacer(1, 0.2*inch))

        # Tabla de presupuesto
        tabla_presupuesto = self._crear_tabla_presupuesto()
        elementos.append(tabla_presupuesto)

        return elementos

    def _crear_tabla_presupuesto(self):
        """Crea la tabla de presupuesto profesional"""

        # Datos de la tabla
        data = []

        # Encabezado con logo y datos de versión
        header_row = [
            ['', f"{self.data['numero_cotizacion']}\n{datetime.now().strftime('%d/%m/%Y')}\nVERSION: 2 / ULTIMA REVISION: 10-12-19"]
        ]

        # Información del cliente
        info_row = [
            [f"CLIENTE:\nCONTACTO:", f"{self.data['cliente']}\n{self.data.get('contacto', 'N/A')}",
             f"TELEFONO:\nEMAIL:", f"N/A\nN/A"]
        ]

        # Encabezado de la tabla principal
        header_presupuesto = [
            ['PRESUPUESTO MANTENIMIENTO PREVENTIVO', '', '', '', '']
        ]

        columnas_tabla = [
            ['DETALLE', 'CANTIDAD DE\nEQUIPOS', 'VALOR POR\nUNITARIO', 'VALOR POR\nVISITA', 'CANTIDAD DE VISITAS\nAL AÑO', 'PRECIO TOTAL\nANUAL']
        ]

        # Obtener equipos y calcular totales
        equipos = self.data.get('equipos', [])
        subtotal = 0

        for equipo in equipos:
            nombre = equipo[0] if len(equipo) > 0 else "Equipo"
            cantidad = equipo[1] if len(equipo) > 1 else 1
            subtotal_equipo = equipo[3] if len(equipo) > 3 else 0
            subtotal += subtotal_equipo

            precio_unitario = subtotal_equipo / cantidad if cantidad > 0 else 0
            visitas = self.data.get('visitas_anuales', 1)
            total_anual = subtotal_equipo * visitas

            fila_equipo = [
                nombre.upper(),
                str(int(cantidad)),
                f"${precio_unitario:,.2f}",
                f"${subtotal_equipo:,.2f}",
                str(int(visitas)),
                f"${total_anual:,.2f}"
            ]
            columnas_tabla.append(fila_equipo)

        # Fila de subtotales
        visitas = self.data.get('visitas_anuales', 1)
        subtotal_anual = subtotal * visitas

        columnas_tabla.append([
            'SUB - TOTALES', '', 'VISITA', f"${subtotal:,.2f}", 'ANUAL', f"${subtotal_anual:,.2f}"
        ])

        # Calcular IVA y total
        iva_porcentaje = self.data.get('iva_porcentaje', 13.0)
        iva = subtotal_anual * (iva_porcentaje / 100)
        total = subtotal_anual + iva

        # Filas de IVA y total
        columnas_tabla.append([
            f'I.V.A. {iva_porcentaje}%', '', '', f"${iva:,.2f}", '', f"${iva:,.2f}"
        ])

        columnas_tabla.append([
            'MONTO TOTAL OFERTA', '', '', f"${total:,.2f}", '', f"${total:,.2f}"
        ])

        # Combinar todas las filas
        data.extend(header_row)
        data.extend(info_row)
        data.extend(header_presupuesto)
        data.extend(columnas_tabla)

        # Crear tabla
        tabla = Table(data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch, 1.2*inch, 1*inch])

        # Estilos de la tabla
        tabla.setStyle(TableStyle([
            # Fila del header con logo
            ('SPAN', (0, 0), (1, 0)),
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#e3f2fd')),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (1, 0), 9),

            # Fila de información del cliente
            ('BACKGROUND', (0, 1), (-1, 1), colors.white),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, 1), 9),
            ('ALIGN', (0, 1), (-1, 1), 'LEFT'),

            # Encabezado "PRESUPUESTO MANTENIMIENTO PREVENTIVO"
            ('SPAN', (0, 2), (-1, 2)),
            ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 2), (-1, 2), colors.white),
            ('ALIGN', (0, 2), (-1, 2), 'CENTER'),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 2), (-1, 2), 11),

            # Encabezado de columnas
            ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#64748b')),
            ('TEXTCOLOR', (0, 3), (-1, 3), colors.white),
            ('ALIGN', (0, 3), (-1, 3), 'CENTER'),
            ('FONTNAME', (0, 3), (-1, 3), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 3), (-1, 3), 8),

            # Filas de equipos
            ('ALIGN', (1, 4), (-1, -4), 'CENTER'),
            ('FONTSIZE', (0, 4), (-1, -4), 9),

            # Fila de subtotales
            ('BACKGROUND', (0, -3), (-1, -3), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, -3), (-1, -3), colors.white),
            ('FONTNAME', (0, -3), (-1, -3), 'Helvetica-Bold'),
            ('ALIGN', (0, -3), (-1, -3), 'CENTER'),

            # Fila de IVA
            ('BACKGROUND', (0, -2), (-1, -2), colors.HexColor('#e3f2fd')),
            ('FONTNAME', (0, -2), (-1, -2), 'Helvetica-Bold'),
            ('ALIGN', (0, -2), (-1, -2), 'CENTER'),

            # Fila de total
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 11),
            ('ALIGN', (0, -1), (-1, -1), 'CENTER'),

            # Bordes
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        return tabla

    def _crear_notas_firma(self):
        """Crea la página de notas y firma"""
        elementos = []

        elementos.append(Spacer(1, 0.3*inch))

        elementos.append(Paragraph("<b>Notas:</b>", self.styles['Subtitulo']))

        notas = [
            "Oferta válida por 30 días naturales.",
            "El precio es firme y definitivo según los requerimientos especificados en sitio.",
            "El pago será conforme se acuerda con el cliente.",
            "Sobre la garantía del servicio es de 90 días naturales."
        ]

        for nota in notas:
            elementos.append(Paragraph(f"- {nota}", self.styles['TextoNormal']))
            elementos.append(Spacer(1, 6))

        elementos.append(Spacer(1, 0.5*inch))

        # Información de contacto
        contacto_data = [
            ['', ''],
            ['', ''],
            ['<b>Mauricio Cordero T.</b>', 'WWW.AIRSOLUTIONSCR.COM'],
            ['<b>Gerente General</b>', 'Escazú, San José, Costa Rica'],
            ['', '+506 4419-5148 / +506 7294-2347'],
            ['', 'MCORDERO@AIRSOLUTIONSCR.COM']
        ]

        contacto_tabla = Table(contacto_data, colWidths=[3*inch, 3*inch])
        contacto_tabla.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 2), (0, 3), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 2), (0, 3), 12),
            ('FONTSIZE', (1, 2), (1, -1), 10),
            ('TEXTCOLOR', (1, 2), (1, 2), colors.HexColor('#2563eb')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        elementos.append(contacto_tabla)

        return elementos


def generar_pdf_cotizacion(numero_cotizacion, db):
    """
    Función principal para generar PDF de cotización profesional

    Args:
        numero_cotizacion: Número de la cotización
        db: Instancia de DatabaseManager

    Returns:
        Path del archivo PDF generado o None si hay error
    """
    try:
        # Obtener datos de la cotización
        query = """
            SELECT c.*, cl.nombre_empresa, cl.contacto_nombre, cl.direccion
            FROM cotizaciones c
            LEFT JOIN clientes cl ON c.id_cliente = cl.id_cliente
            WHERE c.numero_cotizacion = ?
        """
        result = db.ejecutar_query(query, (numero_cotizacion,))
        cotizacion = result.fetchone()

        if not cotizacion:
            print("Cotización no encontrada")
            return None

        id_cotizacion = cotizacion[0]

        # Preparar datos
        data = {
            'numero_cotizacion': numero_cotizacion,
            'cliente': cotizacion[26] or 'Cliente',
            'contacto': cotizacion[27] or 'N/A',
            'direccion_cliente': cotizacion[28] or 'Dirección del cliente',
            'fecha': cotizacion[3],
            'tipo_servicio': cotizacion[5] or 'Mantenimiento Preventivo',
            'visitas_anuales': cotizacion[6] or 1,
            'subtotal': cotizacion[10] or 0,
            'ins_ccss': cotizacion[19] or 0,
            'iva': cotizacion[14] or 0,
            'total': cotizacion[15] or 0,
            'tipo_cambio': cotizacion[9] or 515,
            'iva_porcentaje': cotizacion[24] if len(cotizacion) > 24 and cotizacion[24] else 13.0,
            'mostrar_colones': cotizacion[25] if len(cotizacion) > 25 else 0
        }

        # Cargar equipos
        data['equipos'] = db.ejecutar_query("""
            SELECT pe.tipo_equipo, dc.cantidad, dc.horas_por_equipo, dc.subtotal
            FROM detalle_cotizacion dc
            LEFT JOIN productos_equipos pe ON dc.id_equipo = pe.id_equipo
            WHERE dc.id_cotizacion = ?
        """, (id_cotizacion,)).fetchall()

        # Generar PDF
        pdf_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'cotizaciones'
        )
        pdf_filename = f"COT_{numero_cotizacion}_{datetime.now().strftime('%Y%m%d')}.pdf"
        pdf_path = os.path.join(pdf_dir, pdf_filename)

        generador = PDFCotizacionProfesional(data)

        if generador.generar(pdf_path):
            return pdf_path
        else:
            return None

    except Exception as e:
        print(f"Error generando PDF: {e}")
        import traceback
        traceback.print_exc()
        return None
