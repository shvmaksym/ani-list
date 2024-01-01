import threading
import time

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    jsonify,
    url_for,
)
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from api_helpers import login_required, get_data_from_api_and_process, apology

app = Flask(__name__)

db = SQL("sqlite:///anime_db.db")

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

last_update_time = None

UPDATE_INTERVAL = 3600


@app.route("/anime/<int:anime_id>", methods=["GET", "POST"])
def add_comments(anime_id):
    if request.method == "POST":
        user_id = session.get("user_id")
        comment = request.form.get("comment")
        db.execute(
            "INSERT INTO comments (anime_id, user_id, comment) VALUES (:anime_id, :user_id, :comment)",
            anime_id=anime_id,
            user_id=user_id,
            comment=comment,
        )

    anime_data = get_anime_data_by_id(anime_id)
    comments = db.execute(
        "SELECT  comments.anime_id, comments.id, comments.comment, comments.timestamp, users.username FROM comments JOIN users ON comments.user_id = users.id WHERE comments.anime_id = :anime_id",
        anime_id=anime_id,
    )

    return render_template("comments.html", comments=comments)


@app.route("/delete_comment/<int:comment_id>", methods=["POST"])
def delete_comment(comment_id):
    user_id = session.get("user_id")
    result = db.execute(
        "SELECT user_id FROM comments WHERE id = :comment_id", comment_id=comment_id
    )
    if result and result[0]["user_id"] == user_id:
        db.execute("DELETE FROM comments WHERE id = :comment_id", comment_id=comment_id)
        return jsonify({"success": True}), 200
    else:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Comment does not belong to the current user.",
                }
            ),
            403,
        )


@app.route("/favorites/<int:userId>", methods=["GET"])
@login_required
def favorites(userId):
    user_id_from_session = session.get("user_id")
    if userId != user_id_from_session:
        flash("You are not authorized to view this page.")
        return redirect(url_for("home"))

    favorite_anime = db.execute(
        "SELECT anime.id, anime.title, anime.image FROM anime JOIN favorite_anime ON anime.id = favorite_anime.anime_id WHERE favorite_anime.user_id = :user_id",
        user_id=session.get("user_id"),
    )
    return render_template(
        "favorites.html", favorite_anime=favorite_anime, current_page="favorites"
    )


def get_anime_data_by_id(anime_id):
    anime_data = db.execute(
        "SELECT * FROM anime WHERE id = :anime_id", anime_id=anime_id
    )
    if not anime_data:
        return None
    return anime_data[0]


@app.route("/add_to_favorites/<int:animeId>/<int:userId>", methods=["POST"])
def add_to_favorites(animeId, userId):
    try:
        existing_favorite = db.execute(
            "SELECT * FROM favorite_anime WHERE user_id = :user_id AND anime_id = :anime_id",
            user_id=userId,
            anime_id=animeId,
        )
        if existing_favorite:
            db.execute(
                "DELETE FROM favorite_anime WHERE user_id = :user_id AND anime_id = :anime_id",
                user_id=userId,
                anime_id=animeId,
            )
            is_favorite = False
        else:
            db.execute(
                "INSERT INTO favorite_anime (user_id, anime_id) VALUES (:user_id, :anime_id)",
                user_id=userId,
                anime_id=animeId,
            )
            is_favorite = True

        image_url = (
            "/static/heart_favor.png" if is_favorite else "/static/white-heart.png"
        )

        return (
            jsonify(
                {
                    "message": "Anime added to favorites successfully",
                    "is_favorite": is_favorite,
                    "image_url": image_url,
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/show_info/<int:anime_id>", methods=["GET", "POST"])
@login_required
def show_info(anime_id):
    anime_data = get_anime_data_by_id(anime_id)
    comments = db.execute(
        "SELECT comments.id,comments.comment, comments.timestamp, users.username FROM comments JOIN users ON comments.user_id = users.id WHERE comments.anime_id = :anime_id",
        anime_id=anime_id,
    )

    if request.method == "POST":
        user_id = session.get("user_id")
        comment = request.form.get("comment")

        db.execute(
            "INSERT INTO comments (anime_id, user_id, comment) VALUES (:anime_id, :user_id, :comment)",
            anime_id=anime_id,
            user_id=user_id,
            comment=comment,
        )

        comments = db.execute(
            "SELECT comments.id, comments.comment, comments.timestamp, users.username FROM comments JOIN users ON comments.user_id = users.id WHERE comments.anime_id = :anime_id",
            anime_id=anime_id,
        )

        return render_template(
            "info.html",
            anime_data=anime_data,
            comments=comments,
            current_page="show_info",
            anime_id=anime_id,
            update_comments=True,
        )

    return render_template(
        "info.html",
        anime_data=anime_data,
        comments=comments,
        current_page="show_info",
        anime_id=anime_id,
        update_comments=False,
    )


@app.route("/")
@login_required
def index():
    user_id = session.get("user_id")
    anime_data = db.execute(
        "SELECT anime.id, anime.title, anime.image FROM anime ORDER BY anime.ranking"
    )
    favorite_anime_ids = [
        row["anime_id"]
        for row in db.execute(
            "SELECT anime_id FROM favorite_anime WHERE user_id = :user_id",
            user_id=user_id,
        )
    ]
    for anime in anime_data:
        anime["is_favorite"] = anime["id"] in favorite_anime_ids

    return render_template("index.html", anime_data=anime_data, current_page="index")


@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return apology("Missing username", 400)
        if not password:
            return apology("Missing password", 400)
        if not confirmation:
            return apology("Missing confirmation", 400)
        if password != confirmation:
            return apology("Passwords do not match", 400)

        user = db.execute("SELECT * FROM users WHERE username = ?", (username,))
        if user:
            return apology("Username already exists", 400)
        else:
            hashed_password = generate_password_hash(password)
            db.execute(
                "INSERT INTO users (username, hash) VALUES (?, ?)",
                username,
                hashed_password,
            )
            return redirect("/login")
    else:
        return render_template("register.html", current_page="register")


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username", 403)
        elif not request.form.get("password"):
            return apology("must provide password", 403)
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)
        session["username"] = request.form.get("username")
        session["user_id"] = rows[0]["id"]
        return redirect("/")
    else:
        return render_template("login.html", current_page="login")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


def update_data():
    while True:
        get_data_from_api_and_process()
        time.sleep(UPDATE_INTERVAL)


update_thread = threading.Thread(target=update_data)
update_thread.daemon = True
update_thread.start()

if __name__ == "__main__":
    app.run(debug=True)
