from flask import request, jsonify
from app.models import User, Role
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, bcrypt
from flask_jwt_extended import create_access_token
from app.models import User, Message, Ticket, Queue, Event, WhatsAppMessage, TicketStatus, ChatbotControl
from app.schemas import message_schema, messages_schema, ticket_schema, tickets_schema, queue_schema, queues_schema, event_schema, events_schema
from app.services.whatsapp_service import WhatsAppService
from sqlalchemy.exc import IntegrityError

whatsapp_service = WhatsAppService()

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
        print(f"Creando usuario: {username}, role_id: {role_id}, name: {name}, lastname: {lastname}, email: {email}")  # Depuración

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        print(f"Contraseña encriptada: {hashed_password}")

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

def login_user():
    data = request.get_json()
    print(data)
    user = User.query.filter_by(username=data['username']).first()
    print(f"User found: {user}")

    if not user:
        print("Usuario no encontrado")  # Depuración
        return {"error": "Credenciales inválidas"}, 401

    if not bcrypt.check_password_hash(user.password, data['password']):
        print("Contraseña incorrecta")  # Depuración
        return {"error": "Credenciales inválidas"}, 401

    # Ensure the user has a valid role
    if not user.role:
        return {"error": "Usuario sin rol asignado"}, 400

    token = create_access_token(identity={"username": user.username, "role": user.role.name})
    print(f"Token created: {token}")  # Depuración
    return {"token": token}, 200

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
    data = request.get_json()
    try:
        whatsapp_service.send_message(data['contact'], data['message'])
        return {"message": "Mensaje enviado exitosamente"}, 200
    except Exception as e:
        return {"error": str(e)}, 500

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


