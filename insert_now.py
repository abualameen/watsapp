from app import db, create_app
from app.models import Role

def insert_roles():
    roles = [
        {'name': 'Admin', 'code': 'admin', 'description': 'Administrative user'},
        {'name': 'Agent', 'code': 'agent', 'description': 'Support agent'},
        {'name': 'User', 'code': 'user', 'description': 'Regular user'}
    ]
    for role in roles:
        existing_role = Role.query.filter_by(code=role['code']).first()
        if not existing_role:
            new_role = Role(**role)
            db.session.add(new_role)
    db.session.commit()

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        insert_roles()