from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
from app.models import WhatsAppMessage, Ticket
from app import db

class WhatsAppService:
    def __init__(self):
        self.driver = None

    def start(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')  # Abrir el navegador maximizado
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        # Abre WhatsApp Web
        self.driver.get("https://web.whatsapp.com/")
        print("Escanea el código QR en el navegador para iniciar sesión.")
        time.sleep(20)  # Tiempo para escanear el QR

    def listen_for_messages(self):
        print("Escuchando mensajes entrantes...")
        while True:
            try:
                # Captura los mensajes nuevos
                messages = self.driver.find_elements(By.XPATH, '//div[contains(@class,"message-in")]')
                for message in messages:
                    content = message.text
                    sender = message.find_element(By.XPATH, '..//span[@class="copyable-text"]').get_attribute("title")

                    # Verificar si ya existe el mensaje
                    existing_message = WhatsAppMessage.query.filter_by(content=content, sender=sender).first()
                    if not existing_message:
                        # Crear un nuevo mensaje en la base de datos
                        new_message = WhatsAppMessage(content=content, sender=sender)
                        db.session.add(new_message)
                        db.session.commit()

                        # Asociar el mensaje a un ticket
                        self.associate_with_ticket(sender, content)

                        print(f"Nuevo mensaje recibido de {sender}: {content}")
            except Exception as e:
                print(f"Error al procesar mensajes: {str(e)}")
                time.sleep(5)  # Esperar un tiempo antes de intentar de nuevo

    def associate_with_ticket(self, sender, content):
        # Verificar si el remitente ya tiene un ticket abierto
        ticket = Ticket.query.filter_by(contact=sender, status="open").first()
        if not ticket:
            # Crear un nuevo ticket
            ticket = Ticket(contact=sender, status="open", description=f"Nuevo mensaje: {content}")
            db.session.add(ticket)
            db.session.commit()
            print(f"Nuevo ticket creado para {sender}.")
        else:
            # Actualizar el ticket existente
            ticket.description = f"{ticket.description}\n{content}"
            db.session.commit()
            print(f"Ticket actualizado para {sender}.")
