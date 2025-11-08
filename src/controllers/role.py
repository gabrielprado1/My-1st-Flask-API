from flask import Blueprint, request
from src.models.role import Role
from src.models.base import db
from http import HTTPStatus
from flask_jwt_extended import jwt_required
from src.utils import requires_role

app = Blueprint("role", __name__, url_prefix="/roles")

@app.route("/", methods=["POST"])
@requires_role("admin")
@jwt_required
def create_role():
    data = request.json
    role = Role(name=data["name"])
    db.session.add(role)
    db.session.commit()
    return {"message": "Role created!"}, HTTPStatus.CREATED
