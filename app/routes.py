from flask import Blueprint, render_template, request, jsonify, send_from_directory, session
from flask_restful import Api, Resource
from app.controllers import (
    register_user, login_user,
    create_message, get_messages, update_message_status,
    create_ticket, get_tickets, update_ticket_status, close_ticket,
    create_queue, get_queues, update_queue_priority, reassign_message,
    create_event, get_events, update_event, delete_event, refresh_token,
    start_whatsapp, send_whatsapp_message, get_messages_by_ticket, get_unlinked_messages,
    send_chatbot_response, assign_agent, resolve_ticket, receive_message
)
import requests
import os
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, verify_jwt_in_request
import logging

logging.basicConfig(level=logging.DEBUG)


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

class GetUser(Resource):
    @jwt_required()
    def get(self):
        return get_user()


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


class RecieveMessage(Resource):
    @jwt_required()
    def post(self):
        return receive_message()

class SendChatbotResponse(Resource):
    @jwt_required()
    def post(self, ticket_id):
        return send_chatbot_response(ticket_id)

class AssignAgent(Resource):
    @jwt_required()
    def post(self, ticket_id):
        return assign_agent(ticket_id)

class ResolveTicket(Resource):
    @jwt_required()
    def post(self, ticket_id):
        return resolve_ticket(ticket_id)

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
api.add_resource(RecieveMessage, '/receive-message')
api.add_resource(SendChatbotResponse, '/send-chatbot-response/<int:ticket_id>')
api.add_resource(AssignAgent, '/assign-agent/<int:ticket_id>')
api.add_resource(ResolveTicket, '/resolve-ticket/<int:ticket_id>')
api.add_resource(GetUser, '/get-user')



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

    # @app.route('/chats')
    # #@jwt_required()
    # def chats():
    #     user_id = "abulyaqs"  # Puedes obtenerlo de la sesión o una variable dinámica.
    #     #verify_jwt_in_request()  # Manually verify the JWT token
    #     #print('JWT Identity:', get_jwt_identity())  # Debug: Print the JWT identity
    #     #logging.debug(f"JWT Identity:', {get_jwt_identity()}")
    #     #user_id = get_jwt_identity().get('username') 
    #     response = requests.get(f'http://localhost:3000/get-chats?userId={user_id}')
    #     chats_data = response.json()
    #     return render_template('chats.html', chats=chats_data)

 

    @app.route('/chats')
    def chats():
        #user_id = request.args.get('userId')  #Get userId dynamically from query params
        user_id = session.get('username')
        to = session.get('to')
        chatId= to[1:] + "@c.us"
        logging.debug(f"userid: {user_id}") 
        if not user_id:
            return jsonify({"error": "Missing userId"}), 400  # Ensure userId is provided

        try:
            response = requests.get(f'http://localhost:3000/get-chats?userId={user_id}')

            if response.status_code != 200:
                return jsonify({"error": "Failed to fetch chats", "status_code": response.status_code, "text": response.text}), response.status_code

            # Log and return response JSON
            chats_data = response.json()
            print("Chats fetched:", chats_data)  # Debug log
            logging.debug(f"chats ftech: {chats_data}")
            return render_template('chats.html', chats=chats_data, to=to, chatId=chatId, user_id=user_id)

        except Exception as e:
            logging.error(f"🔥 Error fetching chats: {e}")
            return jsonify({"error": "Internal server error"}), 500

    # @app.route('/messages')
    # def messages():
    #     user_id = session.get('username')
    #     to = session.get('to')
    #     logging.debug(f"useriddd: {user_id}")
    #     logging.debug(f"too: {to}") 
    #     chatId= to[1:] + "@c.us"
    #     if not user_id and not to:
    #         return jsonify({"error": "Missing userId and contact"}), 400  # Ensure userId is provided
    #     response = requests.get(f'http://localhost:3000/get-messages?userId={user_id}&chatId={chatId}')

    #     if response.status_code != 200:
    #         return jsonify({"error": "Failed to fetch messages"}), response.status_code

    #     messages_data = response.json()
    #     return render_template('chats.html', messages=messages_data)
        


