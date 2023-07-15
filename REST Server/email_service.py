import json
from flask import Flask, request, jsonify
import os
import sys
import psycopg2
from psycopg2 import errors, errorcodes
import structlog
from datetime import datetime, timezone
from marshmallow import Schema, fields, validate
import logging

app = Flask(__name__)


def get_db_connection():
    conn = psycopg2.connect(
        host=os.environ['POSTGRES_HOST'],
        database=os.environ['POSTGRES_DATABASE'],
        user=os.environ['POSTGRES_USERNAME'],
        password=os.environ['POSTGRES_PASSWORD'])
    return conn


def determine_label_id(label_name):
    label_id = None
    if label_name == 'spam':
        label_id = 1
    elif label_name == 'read':
        label_id = 2
    elif label_name == 'important':
        label_id = 3
    return label_id


class EmailSchema(Schema):
    # defines schema for what email should contain and their type
    field_to = fields.Str()
    field_from = fields.Str()
    field_subject = fields.Str()
    field_body = fields.Str()


class getStringSchema(Schema):
    # checks that the user inputs an email_id something of at least length > 0
    email_id = fields.Str(required=True, validate=validate.Length(min=1))


@app.route("/mailbox/email/<email_id>", methods=['GET'])
def get_email(email_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT email_object FROM emails WHERE email_id = '{email_id}';")
    email = cur.fetchone()[0]
    cur.close()
    conn.close()
    logger = structlog.get_logger()
    logger.info(event="email::id::get", email_id=email_id)

    # check getEmail email_id for a length greater than 0
    schema = getStringSchema()
    error = schema.validate({"email_id": email_id})
    if error:
        logging.warning("Error")
        return json.dumps(error), 400

    response_data = {"email": email}

    email_schema = EmailSchema()
    response_data_email_data = response_data["email"]
    email_data = {
        "field_to": response_data_email_data["to"],
        "field_from": response_data_email_data["from"],
        "field_subject": response_data_email_data["subject"],
        "field_body": response_data_email_data["body"]
    }

    error = email_schema.validate(email_data)
    if error:
        logging.warning("Error")
        return json.dumps(error), 400

    return json.dumps(response_data), 200


@app.route("/mailbox/email/<email_id>/folder", methods=['GET'])
def get_folder(email_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT email_folder FROM emails WHERE email_id = '{email_id}';")
    folder = cur.fetchone()[0]
    cur.close()
    conn.close()
    logger = structlog.get_logger()
    logger.info(event="email::id::folder::get", email_id=email_id)

    schema = getStringSchema()
    error = schema.validate({"email_id": email_id})
    if error:
        return json.dumps(error), 400

    return json.dumps({"Folder": folder}), 200


@app.route("/mailbox/email/<email_id>/labels", methods=['GET'])
def get_label(email_id):
    schema = getStringSchema()
    error = schema.validate({"email_id": email_id})
    if error:
        return json.dumps(error), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        f"SELECT labels.label_value FROM email_label JOIN labels ON email_label.label_id = labels.label_id WHERE email_label.email_id={email_id};")
    labels = cur.fetchall()
    cur.close()
    conn.close()
    logger = structlog.get_logger()
    logger.info(event="email::id::labels::get", email_id=email_id)
    return json.dumps({"labels": labels})


@app.route("/mailbox/folder/<folder>", methods=['GET'])
def get_folder_contents(folder):
    schema = getStringSchema()
    error = schema.validate({"email_id": folder})
    if error:
        return json.dumps(error), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT email_id FROM emails WHERE email_folder = '{folder}';")
    email_ids = cur.fetchall()
    cur.close()
    conn.close()
    logger = structlog.get_logger()
    logger.info(event="email:folder::get", folder=folder)
    return json.dumps({folder: email_ids})


@app.route("/mailbox/label/<label>", methods=['GET'])
def get_label_contents(label):
    schema = getStringSchema()
    error = schema.validate({"email_id": label})
    if error:
        return json.dumps(error), 400

    label_id = determine_label_id(label)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        f"SELECT email_label.email_id FROM email_label JOIN labels ON email_label.label_id = labels.label_id WHERE email_label.label_id={label_id};")
    email_ids = cur.fetchall()
    cur.close()
    conn.close()
    logger = structlog.get_logger()
    logger.info(event="email::label::get", label=label)
    return json.dumps({label: email_ids})


@app.route("/mailbox/email/<email_id>/folder/<folder>", methods=['PUT'])
def move_email(email_id, folder):
    schema = getStringSchema()
    error = schema.validate({"email_id": email_id})
    error2 = schema.validate({"email_id": folder})
    if error or error2:
        return json.dumps(error), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"UPDATE emails SET email_folder='{folder}' WHERE email_id={email_id}")
    cur.close()
    conn.close()
    logger = structlog.get_logger()
    logger.info(event="email::id::folder::put", email_id=email_id, folder=folder)
    return json.dumps({"Status": "success"})


@app.route("/mailbox/email/<email_id>/label/<label>", methods=['PUT'])
def mark_email(email_id, label):
    schema = getStringSchema()
    error = schema.validate({"email_id": email_id})
    error2 = schema.validate({"email_id": label})
    if error or error2:
        return json.dumps(error), 400

    label_id = determine_label_id(label)
    if label is None:
        return json.dumps({"ERROR": "invalid label"})
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO email_label (email_id, label_id) VALUES(%s, %s);", (email_id, label_id))
        cur.close()
        conn.commit()
        conn.close()
    except psycopg2.IntegrityError as e:
        if e.pgcode != psycopg2.errorcodes.UNIQUE_VIOLATION:
            return json.dumps({"Status": "Error"})

    logger = structlog.get_logger()
    logger.info(event="email::id::label::put", email_id=email_id, label=label)

    return json.dumps({"Status": "Success"})


@app.route("/mailbox/email/<email_id>/label/<label>", methods=['DELETE'])
def remove_label(email_id, label):
    schema = getStringSchema()
    error = schema.validate({"email_id": email_id})
    error2 = schema.validate({"email_id": label})
    if error or error2:
        return json.dumps(error), 400

    label_id = determine_label_id(label)
    if label is None:
        return json.dumps({"ERROR": "invalid label"})

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM email_label WHERE email_id={email_id} AND label_id={label_id}")
    cur.close()
    conn.commit()
    conn.close()

    logger = structlog.get_logger()
    logger.info(event="email::id::label::delete", email_id=email_id, label=label)

    return json.dumps({"Status": "success"})


@app.route("/mailbox/healthcheck", methods=["GET"])
def healthcheck():
    encountered_failure = False

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        query = "SELECT count(*) FROM emails;"
        cur.execute(query)
        count = cur.fetchone()[0]
        conn.close()
        db_healthy = True
    except:
        db_healthy = False
        encountered_failure = True

    if encountered_failure:
        status_code = 500  # internal server error
    else:
        status_code = 200

    return jsonify({"database": {"healthy": db_healthy}}), status_code


if __name__ == "__main__":
    try:
        var_list = ['POSTGRES_HOST',
                    'POSTGRES_DATABASE',
                    'POSTGRES_USERNAME',
                    'POSTGRES_PASSWORD']
        for env_var in var_list:
            if env_var not in os.environ:
                raise TypeError
    except TypeError:
        sys.exit("Error: Please provide all required environmental variables")

    with open("log_file.json", "wt", encoding="utf-8") as log_fl:
        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.JSONRenderer()
            ],
            logger_factory=structlog.WriteLoggerFactory(file=log_fl)
        )
        app.run(port=8889, debug=False)
