from flask import Blueprint, request
from src.app import Post, db
from http import HTTPStatus
from sqlalchemy import inspect

app = Blueprint("post", __name__, url_prefix="/posts")

def _create_post():
    data = request.json
    post = Post(
                author_id=data["author_id"],
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
def list_or_create_posts():
    if request.method == "POST":
        _create_post()
        return {"message": "Post created!"}, HTTPStatus.CREATED
    else:
        return {"Posts": _list_posts()}
    
@app.route("/<int:post_id>")
def get_post(post_id):
    post = db.get_or_404(Post, post_id)
    return {
        "author_id": post.author_id,
        "id": post.id,
        "title": post.title,
        "body": post.body,
        "created": post.created.isoformat(),
        }

@app.route("/<int:post_id>", methods=['PATCH'])
def update_post(post_id):
    post = db.get_or_404(Post, post_id)
    data = request.json

    mapper = inspect(Post)
    for column in mapper.attrs:
        if column.key in data:
            setattr(post, column.key, data[column.key])
    db.session.commit()
    

    return {
        "author_id": post.author_id,
        "id": post.id,
        "title": post.title,
        "body": post.body,
        "created": post.created.isoformat(),
    }

@app.route("/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    post = db.get_or_404(Post, post_id)
    db.session.delete(post)
    db.session.commit()

    return {"message": "Post successfully deleted."}