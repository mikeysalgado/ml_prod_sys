import json
from flask import Flask, request, jsonify
import os
import psycopg2
from datetime import datetime, timezone


app = Flask(__name__)


def get_db_connection():
    conn = psycopg2.connect(
        host=os.environ['POSTGRES_HOST'],
        database=os.environ['POSTGRES_DATABASE'],
        user=os.environ['POSTGRES_USERNAME'],
        password=os.environ['POSTGRES_PASSWORD'])
    return conn


@app.route("/email", methods=['POST'])
def email_post_request():
    email = json.loads(request.data)
    for key in email:
        if email[key] is None:
            email[key] = "null"
    conn = get_db_connection()
    cur = conn.cursor()
    dt = datetime.now(timezone.utc)
    cur.execute("INSERT INTO emails (received_timestamp, email_object, email_folder) VALUES(%s, %s, %s) RETURNING email_id;", (dt, json.dumps(email), "Inbox"))
    id_of_new_row = int(cur.fetchone()[0])
    cur.close()
    conn.commit()
    conn.close()
    return_object = {"email_id": id_of_new_row}
    return json.dumps(return_object)


app.run(debug=False, port=8888)