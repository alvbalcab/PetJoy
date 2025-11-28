import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings
import threading

def enviar_email_dinamico(destinatario, template_id, datos_dinamicos):
    """
    Función que se ejecuta en un hilo para enviar correos a través de SendGrid.
    Retorna True si la solicitud a SendGrid fue exitosa.
    """
    remitente = settings.EMAIL_SENDER 
    
    try:
        # Se obtiene la API Key de las variables de entorno de Django/Render
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        
        message = Mail(
            from_email=remitente,
            to_emails=destinatario
        )
        
        message.template_id = template_id
        message.dynamic_template_data = datos_dinamicos

        response = sg.send(message)
        
        # El código 202 significa Aceptado para procesamiento por SendGrid
        if response.status_code == 202:
            return True
        else:
            # Puedes loguear el error si lo necesitas
            print(f"Error SendGrid. Status: {response.status_code}, Body: {response.body}")
            return False

    except Exception as e:
        print(f"Error al enviar email a {destinatario} via SendGrid: {e}")
        return False

def enviar_email_async(destinatario, template_id, datos_dinamicos):
    """Lanza la función de envío en un hilo."""
    email_thread = threading.Thread(
        target=enviar_email_dinamico,
        args=[destinatario, template_id, datos_dinamicos]
    )
    email_thread.start()