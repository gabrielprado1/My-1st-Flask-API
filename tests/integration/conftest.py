import pytest
from src.app import create_app, db, User, Role
from werkzeug.security import generate_password_hash
from http import HTTPStatus

@pytest.fixture
def app():
    app = create_app(
        {
            "SECRET_KEY": 'test',
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "JWT_SECRET_KEY": 'test',
        }
    )
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def access_token(client):
    role = Role(name='admin')
    db.session.add(role)
    db.session.commit()

    hashed_password = generate_password_hash("test")
    user = User(username="aaron-summers", password=hashed_password, role_id= role.id)
    db.session.add(user)
    db.session.commit()

    response = client.post('/auth/login', json={'username': user.username, "password": "test"})
    
    assert response.status_code == HTTPStatus.OK, f"Login falhou no fixture: {response.json}"

    return response.json['access_token']

    
   