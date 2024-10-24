from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    new_user = User(username="testuser", email="testuser@example.com")
    new_user.set_password("password123")

    db.session.add(new_user)
    db.session.commit()
