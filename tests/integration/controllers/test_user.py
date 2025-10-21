from http import HTTPStatus
from src.app import User, Role, db
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash

def test_get_user_success(client):
    # Given
    role = Role(name='admin')
    db.session.add(role)
    db.session.commit()
    
    hashed_password = generate_password_hash("test")
    user = User(username="aaron-summers", password=hashed_password, role_id=role.id)
    db.session.add(user)
    db.session.commit()

    login_resp = client.post('/auth/login', json={
        'username': "aaron-summers", 
        "password": "test"
    })
    assert login_resp.status_code == HTTPStatus.OK
    
    access_token = login_resp.json['access_token']

    # When 
    response = client.get(
        f'/users/{user.id}', 
        headers={'Authorization': f'Bearer {access_token}'}
    )

    # Then
    assert response.status_code == HTTPStatus.OK
    assert response.json == {
        "id": user.id, 
        "username": user.username,
        "role_id": user.role_id
    }


def test_get_user_not_found(client):
    # Given
    role = Role(name='admin')
    db.session.add(role)
    db.session.commit()

    hashed_password = generate_password_hash("test")
    user = User(username="test_user", password=hashed_password, role_id=role.id)
    db.session.add(user)
    db.session.commit()

    login_resp = client.post('/auth/login', json={'username': "test_user", "password": "test"})
    assert login_resp.status_code == HTTPStatus.OK
    
    access_token = login_resp.json['access_token']
    user_id = 999

    # When 
    response = client.get(
        f'/users/{user_id}',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    # Then
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_create_user(client, access_token):
    # Given
    role_id = db.session.execute(db.select(Role.id).where(Role.name == "admin")).scalar()
    payload = {"username": "user2", "password": "user2", "role_id": role_id}

    # When
    response = client.post("/users/", json=payload, headers={'Authorization': f'Bearer {access_token}'})
    
    # Then
    assert response.status_code == HTTPStatus.CREATED

    new_user = db.session.execute(db.select(User).where(User.username == "user2")).scalar()

    assert new_user is not None
    assert response.json == {
        "id": new_user.id, 
        "username": "user2", 
        "role_id": role_id
    }
    assert db.session.execute(db.select(func.count(User.id))).scalar() == 2

    assert new_user.password != "user2"
    assert check_password_hash(new_user.password, "user2")


def test_list_users(client, access_token):
    # Given
    role = db.session.execute(db.select(Role).where(Role.name == "admin")).scalar()
    hashed_password = generate_password_hash("test2")

    user2 = User(username="another-user", password=hashed_password, role_id=role.id)
    db.session.add(user2)
    db.session.commit()

    # When 
    response = client.get("/users/", headers={'Authorization': f'Bearer {access_token}'})

    # Then
    assert response.status_code == HTTPStatus.OK
    assert "Users" in response.json


    assert len(response.json["Users"]) == 2
    assert response.json["Users"][0]["username"] is not None
    assert "role" in response.json["Users"][0]

