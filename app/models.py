from app import db

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=True)
    code = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    def __repr__(self):
        return f"<User {self.username}>"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    role = db.relationship('Role', backref='users')
    
    def __repr__(self):
        return f"<User {self.username}>"

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __repr__(self):
        return f"<Contact {self.name} {self.lastname}>"

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    direction = db.Column(db.String(50), nullable=False)  # Ej: 'inbound' o 'outbound'
    content = db.Column(db.Text, nullable=False)
    sent_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Puede ser nulo si es enviado por un bot
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    is_read = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<Message {self.id}>"

class MessageStatus(db.Model):
    __tablename__ = 'message_status'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)  # 'Pending', 'Read', 'Answered'
    code = db.Column(db.String(20), unique=True, nullable=False)  # 'pending', 'read', 'answered'

    def __repr__(self):
        return f"<MessageStatus {self.status_name}>"
    
class Queue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<Queue {self.name}>"


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Event {self.title}>'

class WhatsAppMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.String(100), unique=True)  # ID único del mensaje
    content = db.Column(db.Text, nullable=True)
    sender = db.Column(db.String(100), nullable=False)  # Número del remitente
    is_media = db.Column(db.Boolean, default=False)
    media_url = db.Column(db.String(200), nullable=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=True)  # Asociar con un ticket
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<WhatsAppMessage {self.message_id}>'

    
class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False)
    queue_id = db.Column(db.Integer, db.ForeignKey('queue.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    ticket_status_id = db.Column(db.Integer, db.ForeignKey('ticket_status.id'), nullable=False)
    priority_id = db.Column(db.Integer, db.ForeignKey('priority.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __repr__(self):
        return f"<Ticket {self.name}>"

class TicketStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<TicketStatus {self.name}>"

class Priority(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<Priority {self.name}>"
    
class ChatbotControl(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    is_handled_by_bot = db.Column(db.Boolean, default=False)
    transferred_to_agent = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<ChatbotControl {self.ticket_id}>"