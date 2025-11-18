"""
email_manager.py - Sistema de Envío de Emails

Permite:
- Configurar servidor SMTP
- Enviar cotizaciones por email con PDF adjunto
- Plantillas de email personalizables
- Registro de emails enviados
"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime


class EmailManager:
    """Gestor de envío de emails"""

    def __init__(self, db_manager=None):
        """
        Inicializa el gestor de emails

        Args:
            db_manager: Gestor de base de datos (opcional)
        """
        self.db = db_manager
        self.config = self._cargar_configuracion()

    def _cargar_configuracion(self):
        """Carga la configuración de email desde la base de datos"""
        config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'email_remitente': '',
            'email_password': '',
            'email_nombre': 'AirSolutions'
        }

        if self.db:
            try:
                # Intentar cargar desde configuración
                result = self.db.ejecutar_query(
                    "SELECT clave, valor FROM configuracion WHERE clave LIKE 'email_%'"
                )
                for clave, valor in result.fetchall():
                    if clave in config:
                        config[clave] = valor
            except Exception as e:
                print(f"Error cargando configuración de email: {e}")

        return config

    def configurar_smtp(self, smtp_server, smtp_port, email_remitente, email_password, email_nombre):
        """
        Configura los parámetros SMTP

        Args:
            smtp_server: Servidor SMTP (ej: smtp.gmail.com)
            smtp_port: Puerto SMTP (ej: 587)
            email_remitente: Email del remitente
            email_password: Contraseña o app password
            email_nombre: Nombre del remitente

        Returns:
            tuple: (éxito, mensaje)
        """
        self.config['smtp_server'] = smtp_server
        self.config['smtp_port'] = smtp_port
        self.config['email_remitente'] = email_remitente
        self.config['email_password'] = email_password
        self.config['email_nombre'] = email_nombre

        # Guardar en base de datos si está disponible
        if self.db:
            try:
                for clave, valor in self.config.items():
                    # Verificar si existe
                    result = self.db.ejecutar_query(
                        "SELECT COUNT(*) FROM configuracion WHERE clave = ?",
                        (clave,)
                    )
                    if result.fetchone()[0] > 0:
                        # Actualizar
                        self.db.cursor.execute(
                            "UPDATE configuracion SET valor = ? WHERE clave = ?",
                            (valor, clave)
                        )
                    else:
                        # Insertar
                        self.db.cursor.execute(
                            "INSERT INTO configuracion (clave, valor) VALUES (?, ?)",
                            (clave, valor)
                        )
                self.db.conn.commit()
                return True, "Configuración guardada correctamente"
            except Exception as e:
                return False, f"Error guardando configuración: {str(e)}"

        return True, "Configuración actualizada (no guardada en BD)"

    def probar_conexion(self):
        """
        Prueba la conexión SMTP

        Returns:
            tuple: (éxito, mensaje)
        """
        try:
            server = smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port'])
            server.starttls()
            server.login(self.config['email_remitente'], self.config['email_password'])
            server.quit()
            return True, "Conexión exitosa con el servidor SMTP"
        except smtplib.SMTPAuthenticationError:
            return False, "Error de autenticación. Verifica tu email y contraseña."
        except Exception as e:
            return False, f"Error de conexión: {str(e)}"

    def enviar_cotizacion(self, email_destino, nombre_cliente, numero_cotizacion,
                          pdf_path, mensaje_personalizado=""):
        """
        Envía una cotización por email

        Args:
            email_destino: Email del destinatario
            nombre_cliente: Nombre del cliente
            numero_cotizacion: Número de cotización
            pdf_path: Ruta al archivo PDF
            mensaje_personalizado: Mensaje adicional (opcional)

        Returns:
            tuple: (éxito, mensaje)
        """
        try:
            # Verificar que existe el PDF
            if not os.path.exists(pdf_path):
                return False, "El archivo PDF no existe"

            # Verificar configuración
            if not self.config['email_remitente'] or not self.config['email_password']:
                return False, "Configuración de email incompleta"

            # Crear mensaje
            msg = MIMEMultipart()
            msg['From'] = f"{self.config['email_nombre']} <{self.config['email_remitente']}>"
            msg['To'] = email_destino
            msg['Subject'] = f"Cotización {numero_cotizacion} - {self.config['email_nombre']}"

            # Cuerpo del email
            cuerpo = self._generar_cuerpo_email(
                nombre_cliente,
                numero_cotizacion,
                mensaje_personalizado
            )

            msg.attach(MIMEText(cuerpo, 'html'))

            # Adjuntar PDF
            with open(pdf_path, 'rb') as archivo:
                parte = MIMEBase('application', 'octet-stream')
                parte.set_payload(archivo.read())

            encoders.encode_base64(parte)
            nombre_archivo = os.path.basename(pdf_path)
            parte.add_header('Content-Disposition', f'attachment; filename= {nombre_archivo}')
            msg.attach(parte)

            # Enviar email
            server = smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port'])
            server.starttls()
            server.login(self.config['email_remitente'], self.config['email_password'])
            texto = msg.as_string()
            server.sendmail(self.config['email_remitente'], email_destino, texto)
            server.quit()

            # Registrar envío
            self._registrar_envio(email_destino, numero_cotizacion)

            return True, f"Email enviado correctamente a {email_destino}"

        except smtplib.SMTPAuthenticationError:
            return False, "Error de autenticación. Verifica tu email y contraseña."
        except Exception as e:
            return False, f"Error enviando email: {str(e)}"

    def _generar_cuerpo_email(self, nombre_cliente, numero_cotizacion, mensaje_personalizado):
        """
        Genera el cuerpo HTML del email

        Args:
            nombre_cliente: Nombre del cliente
            numero_cotizacion: Número de cotización
            mensaje_personalizado: Mensaje personalizado

        Returns:
            str: HTML del cuerpo del email
        """
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #2563eb;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background-color: #f9fafb;
                    padding: 30px;
                    border: 1px solid #e5e7eb;
                }}
                .footer {{
                    background-color: #f3f4f6;
                    padding: 15px;
                    text-align: center;
                    font-size: 12px;
                    color: #6b7280;
                    border-radius: 0 0 5px 5px;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 24px;
                    background-color: #10b981;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .mensaje-personalizado {{
                    background-color: #fef3c7;
                    border-left: 4px solid #f59e0b;
                    padding: 15px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{self.config['email_nombre']}</h1>
                    <p>Soluciones en Aires Acondicionados</p>
                </div>

                <div class="content">
                    <h2>Estimado/a {nombre_cliente},</h2>

                    <p>Es un placer saludarle y hacerle llegar la cotización <strong>{numero_cotizacion}</strong>
                    que hemos preparado especialmente para usted.</p>

                    {"<div class='mensaje-personalizado'>" + mensaje_personalizado + "</div>" if mensaje_personalizado else ""}

                    <p>Adjunto a este correo encontrará el documento PDF con todos los detalles de la cotización,
                    incluyendo:</p>

                    <ul>
                        <li>Equipos y materiales cotizados</li>
                        <li>Precios detallados</li>
                        <li>Condiciones comerciales</li>
                        <li>Información de contacto</li>
                    </ul>

                    <p>Quedamos atentos a cualquier consulta o aclaración que pueda tener.
                    Estamos comprometidos en brindarle el mejor servicio.</p>

                    <p>Saludos cordiales,<br>
                    <strong>{self.config['email_nombre']}</strong></p>
                </div>

                <div class="footer">
                    <p>Este es un correo automático, por favor no responder a esta dirección.</p>
                    <p>Para consultas, contáctenos directamente.</p>
                    <p>&copy; {datetime.now().year} {self.config['email_nombre']}. Todos los derechos reservados.</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html

    def _registrar_envio(self, email_destino, numero_cotizacion):
        """
        Registra el envío de email en la base de datos

        Args:
            email_destino: Email del destinatario
            numero_cotizacion: Número de cotización
        """
        if self.db:
            try:
                # Crear tabla de registro si no existe
                self.db.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS envios_email (
                        id_envio INTEGER PRIMARY KEY AUTOINCREMENT,
                        numero_cotizacion TEXT,
                        email_destino TEXT,
                        fecha_envio TEXT,
                        estado TEXT DEFAULT 'Enviado'
                    )
                ''')

                # Insertar registro
                self.db.cursor.execute('''
                    INSERT INTO envios_email (numero_cotizacion, email_destino, fecha_envio)
                    VALUES (?, ?, ?)
                ''', (numero_cotizacion, email_destino, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

                self.db.conn.commit()

            except Exception as e:
                print(f"Error registrando envío: {e}")

    def obtener_historial_envios(self, limite=50):
        """
        Obtiene el historial de emails enviados

        Args:
            limite: Número máximo de registros a retornar

        Returns:
            list: Lista de envíos
        """
        if not self.db:
            return []

        try:
            result = self.db.ejecutar_query('''
                SELECT numero_cotizacion, email_destino, fecha_envio, estado
                FROM envios_email
                ORDER BY fecha_envio DESC
                LIMIT ?
            ''', (limite,))

            return result.fetchall()

        except Exception as e:
            print(f"Error obteniendo historial: {e}")
            return []
