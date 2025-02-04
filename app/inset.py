from app import db, Role

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
    insert_roles()