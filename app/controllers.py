from flask import request, jsonify,session
from app.models import User, Role, Contact, Message, Priority, Queue, TicketStatus
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, bcrypt
from flask_jwt_extended import create_access_token
from app.models import User, Message, Ticket, Queue, Event, WhatsAppMessage, TicketStatus, ChatbotControl
from app.schemas import message_schema, messages_schema, ticket_schema, tickets_schema, queue_schema, queues_schema, event_schema, events_schema
from app.services.whatsapp_service import WhatsAppService
from app.whatsapp_service1 import WhatsAppService1
from sqlalchemy.exc import IntegrityError
#from flask_jwt_extended import jwt_required, get_jwt_identity
# from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
import logging

from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, create_refresh_token, verify_jwt_in_request

whatsapp_service = WhatsAppService()
whatsapp_service1 = WhatsAppService1()

logging.basicConfig(level=logging.DEBUG)



def register_user():
    try:
        print("Inicio del controlador register_user")  # Depuración

        # Obtener los datos enviados
        data = request.get_json()
        print(f"Datos recibidos: {data}")  # Depuración

        # Validar que los datos requeridos estén presentes
        if not data or not data.get("username") or not data.get("password"):
            print("Faltan datos requeridos")  # Depuración
            return {"error": "Los campos 'username' y 'password' son obligatorios"}, 400

        # Crear un nuevo usuario
        username = data["username"]
        password = data["password"]
        role_id = data.get("role_id")  # Asumiendo que el role_id es opcional
        name = data["name"]
        lastname = data["lastname"]
        email = data["email"]
        #print(f"Creando usuario: {username}, role_id: {role_id}, name: {name}, lastname: {lastname}, email: {email}")  # Depuración

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        #print(f"Contraseña encriptada: {hashed_password}")

        if not role_id:
            default_role = Role.query.filter_by(name="User").first()
            if not default_role:
                return {"error": "Role 'User' does not exist"}, 400
            role_id = default_role.id

        # Crear instancia del usuario con la contraseña encriptada
        new_user = User(
            name=name,
            lastname=lastname,
            email=email,
            username=username,
            password=hashed_password,
            role_id=role_id
        )
        db.session.add(new_user)
        db.session.commit()

        print("Usuario creado exitosamente")  # Depuración
        return {"message": "Usuario creado exitosamente"}, 201

    except IntegrityError:
        db.session.rollback()
        print("El usuario ya existe")  # Depuración
        # Devuelve un mensaje de error en formato JSON
        return {"error": "El usuario ya existe"}, 400

    except Exception as e:
        print(f"Error interno: {str(e)}")  # Depuración
        # Devuelve un mensaje de error genérico en formato JSON
        return {"error": f"Error interno del servidor: {str(e)}"}, 500



# def refresh_token():
#     current_user = get_jwt_identity()
#     new_token = create_access_token(identity=current_user)
#     return {"token": new_token}, 200


def refresh_token():
    current_user = get_jwt_identity()  # Extract user identity
    new_token = create_access_token(identity=current_user)  # Create new access token
    return {"access_token": new_token}, 200  # Use correct key


# from flask import jsonify
# from flask_jwt_extended import jwt_required, get_jwt_identity


def get_user():
    user_identity = get_jwt_identity()
    user_id = user_identity.get('username') if isinstance(user_identity, dict) else user_identity  # Ensure correct format
    return jsonify({"userId": user_id})





def login_user():
    data = request.get_json()
    #logging.debug(f"Login data: {data}")
    user = User.query.filter_by(username=data['username']).first()
    #logging.debug(f"User found: {user}")
    if not user:
        logging.error("User not found")
        return {"error": "Credenciales inválidas"}, 401

    if not bcrypt.check_password_hash(user.password, data['password']):
        logging.error("Password mismatch")
        return {"error": "Credenciales inválidas"}, 401

    if not user.role:
        return {"error": "Usuario sin rol asignado"}, 400
    #logging.debug(f"User logging in: {user.username}, Role: {user.role.name}, ID: {user.id}")
    session['user_id'] = user.id  # Store user ID in session
    session['username'] = user.username  # Optional: Store username
    session['role'] = user.role.name  # Optional: Store role

    access_token = create_access_token(identity={"username": user.username, "role": user.role.name, "user_id": user.id})
    refresh_token = create_refresh_token(identity={"username": user.username, "role": user.role.name, "user_id": user.id})
    ##logging.debug((f"Referesh created: {refresh_token}"))
    #logging.debug((f"Token created: {access_token}"))
    return {"token": access_token, "refresh_token": refresh_token}, 200


# Crear un mensaje
def create_message():
    data = request.get_json()
    new_message = Message(
        content=data['content'],
        status=data.get('status', 'pending'),
        user_id=data['user_id']
    )
    db.session.add(new_message)
    db.session.commit()
    return message_schema.jsonify(new_message), 201

# Obtener todos los mensajes
def get_messages():
    messages = Message.query.all()
    return messages_schema.jsonify(messages), 200

# Actualizar el estado de un mensaje
def update_message_status(message_id):
    data = request.get_json()
    message = Message.query.get(message_id)
    if not message:
        return {"error": "Mensaje no encontrado"}, 404

    message.status = data['status']
    db.session.commit()
    return message_schema.jsonify(message), 200

# Crear un ticket
def create_ticket():
    data = request.get_json()
    new_ticket = Ticket(
        title=data['title'],
        description=data['description'],
        status=data.get('status', 'pending'),
        user_id=data['user_id']
    )
    db.session.add(new_ticket)
    db.session.commit()
    return ticket_schema.jsonify(new_ticket), 201

# Obtener todos los tickets
def get_tickets():
    tickets = Ticket.query.all()
    return tickets_schema.jsonify(tickets), 200

# Actualizar el estado de un ticket
def update_ticket_status(ticket_id):
    data = request.get_json()
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return {"error": "Ticket no encontrado"}, 404

    ticket.status = data['status']
    db.session.commit()
    return ticket_schema.jsonify(ticket), 200

# Crear una cola para un mensaje
def create_queue():
    data = request.get_json()
    message = Message.query.get(data['message_id'])
    if not message:
        return {"error": "Mensaje no encontrado"}, 404

    new_queue = Queue(
        priority=data.get('priority', 'medium'),
        message_id=message.id,
        agent_id=data.get('agent_id')  # Opcional
    )
    db.session.add(new_queue)
    db.session.commit()
    return queue_schema.jsonify(new_queue), 201

# Obtener todas las colas
def get_queues():
    queues = Queue.query.all()
    return queues_schema.jsonify(queues), 200

# Actualizar la prioridad de un mensaje en la cola
def update_queue_priority(queue_id):
    data = request.get_json()
    queue = Queue.query.get(queue_id)
    if not queue:
        return {"error": "Cola no encontrada"}, 404

    queue.priority = data['priority']
    db.session.commit()
    return queue_schema.jsonify(queue), 200

# Reasignar un mensaje a otro agente
def reassign_message(queue_id):
    data = request.get_json()
    queue = Queue.query.get(queue_id)
    if not queue:
        return {"error": "Cola no encontrada"}, 404

    agent = User.query.get(data['agent_id'])
    if not agent or agent.role != 'agent':
        return {"error": "Agente no válido"}, 400

    queue.agent_id = agent.id
    db.session.commit()
    return queue_schema.jsonify(queue), 200

# Crear un evento
def create_event():
    data = request.get_json()
    new_event = Event(
        title=data['title'],
        description=data.get('description'),
        date=data['date'],
        user_id=data['user_id']
    )
    db.session.add(new_event)
    db.session.commit()
    return event_schema.jsonify(new_event), 201

# Obtener todos los eventos
def get_events():
    events = Event.query.all()
    return events_schema.jsonify(events), 200

# Actualizar un evento
def update_event(event_id):
    data = request.get_json()
    event = Event.query.get(event_id)
    if not event:
        return {"error": "Evento no encontrado"}, 404

    event.title = data.get('title', event.title)
    event.description = data.get('description', event.description)
    event.date = data.get('date', event.date)
    db.session.commit()
    return event_schema.jsonify(event), 200

# Eliminar un evento
def delete_event(event_id):
    event = Event.query.get(event_id)
    if not event:
        return {"error": "Evento no encontrado"}, 404

    db.session.delete(event)
    db.session.commit()
    return {"message": "Evento eliminado exitosamente"}, 200

def start_whatsapp():
    try:
        whatsapp_service.start()
        return {"message": "Servicio de WhatsApp iniciado. Escanea el código QR para continuar."}, 200
    except Exception as e:
        return {"error": str(e)}, 500


def send_whatsapp_message():
    try:
        logging.debug('Entering send_whatsapp_message function')
        verify_jwt_in_request()  # Manually verify the JWT token
        logging.debug(f"JWT Identity: {get_jwt_identity()}")
        data = request.get_json()
        logging.debug(f"data_msg: {data}")
        session['to'] = data['to']

        user_name = get_jwt_identity().get('username')  # Retrieve user ID from the JWT token
        logging.debug(f"use_id: {user_name}")

        if not user_name:
            logging.debug(f"use_id: {user_name}")
            return jsonify({'error': 'User not logged in'}), 401

        user = User.query.filter_by(username=user_name).first()
        logging.debug(f"user: {user}")
        if not user:
            logging.debug(f"user: {user}")
            return jsonify({'error': 'User not found'})
            
        # Check if this is the first message from the contact
        existing_contact = Contact.query.filter_by(phone_number=data['to']).first()
        if not existing_contact:
            existing_contact = Contact(name=user.name, lastname=user.lastname, phone_number=data['to'], email=user.email)
            db.session.add(existing_contact)
            db.session.commit()

        # Check if this is the first message from the contact
        if not Message.query.filter_by(contact_id=existing_contact.id).first():
            support_queue = Queue.query.filter_by(name='Support').first()
            default_status = TicketStatus.query.filter_by(name='Open').first()
            default_priority = Priority.query.filter_by(name='Medium').first()

            new_ticket = Ticket(
                contact_id=existing_contact.id,
                queue_id=support_queue.id,
                assigned_to=None,  # Initially unassigned
                ticket_status_id=default_status.id,
                priority_id=default_priority.id,
                name=existing_contact.name,  # You might want to handle this differently
                description=data['message']
            )
            db.session.add(new_ticket)
            db.session.commit()

            # Create a chatbot control entry for the new ticket
            chatbot_control = ChatbotControl(
                ticket_id=new_ticket.id,
                is_handled_by_bot=True,
                transferred_to_agent=False
            )
            db.session.add(chatbot_control)
            db.session.commit()

            # Set the ticket_id for the new message
            new_message = Message(
                contact_id=existing_contact.id,
                ticket_id=new_ticket.id,  # Assign the ticket_id here
                direction='inbound',
                content=data['message'],
                sent_by=None,
                is_read=False
            )
        else:
            # If it's not the first message, create the message without a ticket_id
            new_message = Message(
                contact_id=existing_contact.id,
                ticket_id=None,  # This will still cause an error if ticket_id is NOT NULL
                direction='inbound',
                content=data['message'],
                sent_by=None,
                is_read=False
            )

        db.session.add(new_message)
        db.session.commit()

        try:
            response = whatsapp_service1.send_message(user_name, data['to'], data['message'])
            
            # Ensure the response is JSON serializable
            if hasattr(response, 'json'):  # Check if the response has a .json() method
                response_data = response.json()
            else:
                response_data = str(response)  # Fallback to string representation
            
            logging.debug(f"response_data: {response_data}")
            return {"message": "Mensaje enviado exitosamente", "response": response_data}, 200
        except Exception as e:
            logging.error(f"Error in send_message: {str(e)}")
            return {"error": str(e)}, 500
    except Exception as e:
        logging.error('Error: %s', str(e))
        return jsonify({'error': str(e)}), 500


def send_chatbot_response(ticket_id):
    try:
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404

        # Generate a chatbot response
        chatbot_message = "Thank you for your message. We will get back to you shortly."
        new_message = Message(
            contact_id=ticket.contact_id,
            ticket_id=ticket.id,
            direction='outbound',
            content=chatbot_message,
            sent_by=None,  # Chatbot response
            is_read=False
        )
        db.session.add(new_message)
        db.session.commit()

        # Send the chatbot response using the WhatsApp service
        response = whatsapp_service1.send_message(ticket.user_id, ticket.contact.phone_number, chatbot_message)
        logging.debug('res: %s', response)

        if 'error' in response:
            return jsonify(response), 500

        return jsonify({'message': 'Chatbot response sent successfully'}), 200
    except Exception as e:
        logging.error('Error: %s', str(e))
        return jsonify({'error': str(e)}), 500


def assign_agent(ticket_id):
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')

        if not agent_id:
            return jsonify({'error': 'Agent ID is required'}), 400

        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404

        ticket.assigned_to = agent_id
        db.session.commit()

        return jsonify({'message': 'Ticket assigned to agent successfully'}), 200
    except Exception as e:
        logging.error('Error: %s', str(e))
        return jsonify({'error': str(e)}), 500



def resolve_ticket(ticket_id):
    try:
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404

        closed_status = TicketStatus.query.filter_by(name='Closed').first()
        if not closed_status:
            closed_status = TicketStatus(name='Closed', code='closed', description='Ticket is closed')
            db.session.add(closed_status)
            db.session.commit()

        ticket.ticket_status_id = closed_status.id
        db.session.commit()

        return jsonify({'message': 'Ticket resolved successfully'}), 200
    except Exception as e:
        logging.error('Error: %s', str(e))
        return jsonify({'error': str(e)}), 500



def get_messages_by_ticket(ticket_id):
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return {"error": "Ticket no encontrado"}, 404

    messages = WhatsAppMessage.query.filter_by(ticket_id=ticket_id).all()
    return {
        "ticket": {
            "id": ticket.id,
            "contact": ticket.contact,
            "status": ticket.status,
            "description": ticket.description,
        },
        "messages": [
            {
                "id": message.id,
                "content": message.content,
                "sender": message.sender,
                "is_media": message.is_media,
                "media_url": message.media_url,
                "created_at": message.created_at
            } for message in messages
        ]
    }, 200

def get_unlinked_messages():
    messages = WhatsAppMessage.query.filter_by(ticket_id=None).all()
    return {
        "unlinked_messages": [
            {
                "id": message.id,
                "content": message.content,
                "sender": message.sender,
                "is_media": message.is_media,
                "media_url": message.media_url,
                "created_at": message.created_at
            } for message in messages
        ]
    }, 200

def update_ticket_status(ticket_id):
    data = request.get_json()
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return {"error": "Ticket no encontrado"}, 404

    new_status = data.get("status")
    if new_status not in ["open", "in-progress", "closed"]:
        return {"error": "Estado no válido"}, 400

    ticket.status = new_status
    db.session.commit()
    return {"message": f"Estado del ticket actualizado a '{new_status}'."}, 200

def close_ticket(ticket_id):
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return {"error": "Ticket no encontrado"}, 404

    ticket.status = "closed"
    db.session.commit()
    return {"message": "Ticket cerrado exitosamente."}, 200


