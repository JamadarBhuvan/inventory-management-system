from app import app, db, User

with app.app_context():
    u = User(username='staff1', role='staff')
    u.set_password('staffpass123')
    db.session.add(u)
    db.session.commit()
    print("User created")
