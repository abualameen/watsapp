from app import ma

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'lastname', 'email', 'username', 'role_id', 'created_at')

user_schema = UserSchema()
users_schema = UserSchema(many=True)

class MessageSchema(ma.Schema):
    class Meta:
        fields = ('id', 'content', 'status', 'user_id')

message_schema = MessageSchema()
messages_schema = MessageSchema(many=True)

class TicketSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'description', 'status', 'user_id')

ticket_schema = TicketSchema()
tickets_schema = TicketSchema(many=True)

class QueueSchema(ma.Schema):
    class Meta:
        fields = ('id', 'priority', 'message_id', 'agent_id')

queue_schema = QueueSchema()
queues_schema = QueueSchema(many=True)

class EventSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'description', 'date', 'user_id')

event_schema = EventSchema()
events_schema = EventSchema(many=True)