from flask import Blueprint, request
from src.models.user import User
from src.models.base import db
from http import HTTPStatus
from sqlalchemy import inspect
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.utils import requires_role
from werkzeug.security import generate_password_hash

app = Blueprint("user", __name__, url_prefix="/users")

def _create_user():
    data = request.json

    username = data.get("username")
    password = data.get("password")
    role_id = data.get("role_id")

    if not username or not password or not role_id:
        return {"error": "Missing data"}, HTTPStatus.BAD_REQUEST
    
    hashed_password = generate_password_hash(data["password"])

    user = User(
        username=data["username"],
        password=hashed_password, 
        role_id=data["role_id"],
        )
    db.session.add(user)
    db.session.commit()

    return {
        "id": user.id,
        "username": user.username,
        "role_id": user.role_id
    }, HTTPStatus.CREATED

def _list_users():
    query = db.select(User)
    users = db.session.execute(query).scalars()
    return [
        {
            "id": user.id,
            "username": user.username,
            "role": {"id": user.role.id, "name": user.role.name} if user.role else None
        }
        for user in users
    ]

@app.route("/", methods=["GET", "POST"])
@jwt_required()
@requires_role("admin")
def list_or_create_user():
    if request.method == "POST":
        response, status_code = _create_user()
        return response, status_code
    else:
        return {"Users": _list_users()}
    
@app.route("/<int:user_id>", methods=["GET", "PATCH", "DELETE"])
@jwt_required() 
def user_detail_view(user_id):
    user = db.get_or_404(User, user_id)

    if request.method == "GET":
        return {
            "id": user.id,
            "username": user.username,
            "role_id": user.role_id
        }

    current_user_id_str = get_jwt_identity() 
    current_user_id = int(current_user_id_str)
    is_owner = (current_user_id == user.id)
    is_admin = False

    if not is_owner:
        current_user_db = db.session.execute(
            db.select(User).where(User.id == current_user_id)
        ).scalar()
        if current_user_db and current_user_db.role.name == "admin":
            is_admin = True
    
    if not is_owner and not is_admin:
        return {"error": "Forbidden: You do not have permission to perform this action."}, HTTPStatus.FORBIDDEN
    
    if request.method == "PATCH":
        data = request.json
        if "username" in data:
            user.username = data["username"]
        if "password" in data:
            user.password = generate_password_hash(data["password"])
        
        db.session.commit()
        
        return {
            "id": user.id,
            "username": user.username,
        }

    if request.method == "DELETE":
        db.session.delete(user)
        db.session.commit()
        return {"message": "User successfully deleted."}, HTTPStatus.NO_CONTENT