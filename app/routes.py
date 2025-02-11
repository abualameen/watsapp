from flask import Blueprint, render_template, request, jsonify, send_from_directory
from flask_restful import Api, Resource
from app.controllers import (
    register_user, login_user,
    create_message, get_messages, update_message_status,
    create_ticket, get_tickets, update_ticket_status, close_ticket,
    create_queue, get_queues, update_queue_priority, reassign_message,
    create_event, get_events, update_event, delete_event, refresh_token,
    start_whatsapp, send_whatsapp_message,
    get_messages_by_ticket, get_unlinked_messages
)
import requests
import os
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity

# Create a Blueprint
bp = Blueprint('api', __name__, url_prefix='/api')
api = Api(bp)

# User routes
class Register(Resource):
    def post(self):
        return register_user()

class Login(Resource):
    def post(self):
        return login_user()

class RefreshToken(Resource):
    @jwt_required(refresh=True)
    def post(self):
        return refresh_token()

# Message routes
class Messages(Resource):
    def get(self):
        return get_messages()

    def post(self):
        return create_message()

class MessageStatus(Resource):
    def patch(self, message_id):
        return update_message_status(message_id)

# Ticket routes
class Tickets(Resource):
    def get(self):
        return get_tickets()

    def post(self):
        return create_ticket()

class TicketStatus(Resource):
    def patch(self, ticket_id):
        return update_ticket_status(ticket_id)

class CloseTicket(Resource):
    def patch(self, ticket_id):
        return close_ticket(ticket_id)

class MessagesByTicket(Resource):
    def get(self, ticket_id):
        return get_messages_by_ticket(ticket_id)

class UnlinkedMessages(Resource):
    def get(self):
        return get_unlinked_messages()

# Queue routes
class Queues(Resource):
    def get(self):
        return get_queues()

    def post(self):
        return create_queue()

class QueuePriority(Resource):
    def patch(self, queue_id):
        return update_queue_priority(queue_id)

class ReassignMessage(Resource):
    def patch(self, queue_id):
        return reassign_message(queue_id)

# Event routes
class Events(Resource):
    def get(self):
        return get_events()

    def post(self):
        return create_event()

class EventDetail(Resource):
    def patch(self, event_id):
        return update_event(event_id)

    def delete(self, event_id):
        return delete_event(event_id)

# WhatsApp routes
class StartWhatsApp(Resource):
    def get(self):
        return start_whatsapp()

class SendMessage(Resource):
    @jwt_required()
    def post(self):
        return send_whatsapp_message()

# Register API resources
api.add_resource(Register, '/register')
api.add_resource(Login, '/login')
api.add_resource(RefreshToken, '/refresh-token')
api.add_resource(Messages, '/messages')
api.add_resource(MessageStatus, '/messages/<int:message_id>/status')
api.add_resource(Tickets, '/tickets')
api.add_resource(TicketStatus, '/tickets/<int:ticket_id>/status')
api.add_resource(CloseTicket, '/tickets/<int:ticket_id>/close')
api.add_resource(MessagesByTicket, '/tickets/<int:ticket_id>/messages')
api.add_resource(UnlinkedMessages, '/messages/unlinked')
api.add_resource(Queues, '/queues')
api.add_resource(QueuePriority, '/queues/<int:queue_id>/priority')
api.add_resource(ReassignMessage, '/queues/<int:queue_id>/reassign')
api.add_resource(Events, '/events')
api.add_resource(EventDetail, '/events/<int:event_id>')
api.add_resource(StartWhatsApp, '/start-whatsapp')
api.add_resource(SendMessage, '/send-whatsapp-message')

# Register Blueprint with the application
def init_app(app):
    app.register_blueprint(bp)

    @app.route('/')
    def dashboard():
        return render_template('dashboard.html')

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

    @app.route('/start-session', methods=['POST'])
    def start_session():
        user_id = request.json.get('userId')
        response = requests.post('http://localhost:3000/start-session', json={"userId": user_id})
        return jsonify(response.json())

    @app.route('/chats')
    def chats():
        user_id = "diegotest5"  # Puedes obtenerlo de la sesión o una variable dinámica.
        response = requests.get(f'http://localhost:3000/get-chats?userId={user_id}')
        chats_data = response.json()
        return render_template('chats.html', chats=chats_data)