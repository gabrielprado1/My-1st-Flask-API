from flask import Blueprint, request
from models import User, Post, db
from http import HTTPStatus
from sqlalchemy import inspect
from flask_jwt_extended import jwt_required, get_jwt_identity


app = Blueprint("post", __name__, url_prefix="/posts")

def _create_post():
    data = request.json
    current_user_id = get_jwt_identity()

    post = Post(
                author_id=current_user_id,
                title=data["title"],
                body=data["body"],
                )
    db.session.add(post)
    db.session.commit()

def _list_posts():
    query = db.select(Post)
    posts = db.session.execute(query).scalars()
    return [
        {
            "author_id": post.author_id,
            "id": post.id,
            "title": post.title,
            "body": post.body,
            "created": post.created.isoformat(),
        }
        for post in posts
    ]

@app.route("/", methods=["GET", "POST"])
@jwt_required()
def list_or_create_posts():
    if request.method == "POST":
        _create_post()
        return {"message": "Post created!"}, HTTPStatus.CREATED
    else:
        return {"Posts": _list_posts()}
    
@app.route("/<int:post_id>", methods=["GET", "PATCH", "DELETE"])
@jwt_required() 
def post_detail_view(post_id):
    post = db.get_or_404(Post, post_id)

    if request.method == "GET":
        return {
            "author_id": post.author_id,
            "id": post.id,
            "title": post.title,
            "body": post.body,
            "created": post.created.isoformat(),
        }

    current_user_id_str = get_jwt_identity() 
    current_user_id = int(current_user_id_str)
    is_owner = (current_user_id == post.author_id)
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
        if "title" in data:
            post.title = data["title"]
        if "body" in data:
            post.body = data["body"]
        
        db.session.commit()
        
        return {
            "author_id": post.author_id,
            "id": post.id,
            "title": post.title,
            "body": post.body,
            "created": post.created.isoformat(),
        }

    if request.method == "DELETE":
        db.session.delete(post)
        db.session.commit()
        return {"message": "Post successfully deleted."}, HTTPStatus.NO_CONTENT
    