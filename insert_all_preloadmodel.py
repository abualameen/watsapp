from app import db, create_app
from app.models import Role, MessageStatus, TicketStatus, Priority, Queue, User



def insert_message_statuses():
    statuses = [
        {'name': 'Pending', 'code': 'pending'},
        {'name': 'Read', 'code': 'read'},
        {'name': 'Answered', 'code': 'answered'}
    ]
    for status in statuses:
        existing_status = MessageStatus.query.filter_by(code=status['code']).first()
        if not existing_status:
            new_status = MessageStatus(**status)
            db.session.add(new_status)
    db.session.commit()

def insert_ticket_statuses():
    statuses = [
        {'name': 'Open', 'code': 'open', 'description': 'Ticket is open and awaiting action'},
        {'name': 'In Progress', 'code': 'in_progress', 'description': 'Ticket is being worked on'},
        {'name': 'Closed', 'code': 'closed', 'description': 'Ticket is resolved and closed'}
    ]
    for status in statuses:
        existing_status = TicketStatus.query.filter_by(code=status['code']).first()
        if not existing_status:
            new_status = TicketStatus(**status)
            db.session.add(new_status)
    db.session.commit()

def insert_priorities():
    priorities = [
        {'name': 'Low', 'description': 'Low priority issue'},
        {'name': 'Medium', 'description': 'Medium priority issue'},
        {'name': 'High', 'description': 'High priority issue'}
    ]
    for priority in priorities:
        existing_priority = Priority.query.filter_by(name=priority['name']).first()
        if not existing_priority:
            new_priority = Priority(**priority)
            db.session.add(new_priority)
    db.session.commit()

def insert_queues():
    queues = [
        {'name': 'Support', 'description': 'General support queue'},
        {'name': 'Sales', 'description': 'Sales-related inquiries'},
        {'name': 'Billing', 'description': 'Billing and payments'}
    ]
    for queue in queues:
        existing_queue = Queue.query.filter_by(name=queue['name']).first()
        if not existing_queue:
            new_queue = Queue(**queue)
            db.session.add(new_queue)
    db.session.commit()



def prepopulate_data():
    insert_message_statuses()
    insert_ticket_statuses()
    insert_priorities()
    insert_queues()
    print("Pre-population completed successfully!")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        prepopulate_data()
