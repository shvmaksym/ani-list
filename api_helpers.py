import datetime
import requests
import uuid
import json

from datetime import datetime, timedelta
from cs50 import SQL
from flask import render_template
from functools import wraps

db = SQL("sqlite:///anime_db.db")

last_update_time = None

url = "https://anime-db.p.rapidapi.com/anime"

querystring = {"page": "1", "size": "500"}

headers = {
    "X-RapidAPI-Key": "c0c9c0c5aemshdc879e0714c24c3p167a08jsn20b74cff3cc1",
    "X-RapidAPI-Host": "anime-db.p.rapidapi.com",
}


def get_data_from_api_and_process():
    global data
    response = requests.get(
        url, cookies={"session": str(uuid.uuid4())}, headers=headers, params=querystring
    )
    if response.status_code != 200:
        print(f"API request failed with status code: {response.status_code}")
        return
    try:
        data = response.json()
    except json.JSONDecodeError:
        print("Failed to decode API response JSON")
        return
    if should_update_data():
        global last_update_time
        last_update_time = datetime.now()

        for record in data.get("data", []):
            process_anime_record(record, db)


def process_anime_record(record, db):
    anime_id = int(record.get("_id", -1))
    try:
        db.execute(
            """
            INSERT OR REPLACE INTO anime (id, title, ranking, episodes, image, status, synopsis)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            anime_id,
            record.get("title", ""),
            int(record.get("ranking", 0)),
            int(record.get("episodes", 0)),
            record.get("image", ""),
            record.get("status", ""),
            record.get("synopsis", ""),
        )
    except Exception as e:
        print("Database error:", str(e))


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)

    return decorated_function


def should_update_data():
    global last_update_time

    if last_update_time is None:
        return True
    current_time = datetime.now()
    elapsed_time = current_time - last_update_time
    return elapsed_time >= timedelta(hours=1)


def apology(message, code=400):
    def escape(s):
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code
