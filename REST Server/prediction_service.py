import minio
import os
import json
import sys
import structlog
from flask import Flask, request, jsonify
import pickle


app = Flask(__name__)


def connection_minio():
    client = minio.Minio(
        endpoint=MINIO_ENDPOINT,
        access_key=MINIO_USERNAME,
        secret_key=MINIO_PASSWORD,
        secure=False
    )
    return client


def download_and_unpickle_model():
    global MODEL, VECTORIZER
    mini = connection_minio()
    objects = mini.list_objects(
        "models", prefix="trained_model", recursive=True,
    )
    target = ''
    for obj in objects:
        target = obj.object_name
    response = pickle.loads(mini.get_object('models', target).read())
    MODEL = response['model']
    VECTORIZER = response['vectorizer']
    print(f"Loaded Model {target} from Minio and is ready to classify emails")


@app.route("/classify", methods=['GET'])
def email_post_request():
    # get email to classify from GET request
    data = json.loads(request.data)
    body = data['email']['body']
    # run prediction
    msgvector = VECTORIZER.transform([body])
    result = MODEL.predict(msgvector)[0]
    # log event
    logger = structlog.get_logger()
    logger.info(event="email::classify", label=result)
    # return JSON object
    return json.dumps({"predicted_class": result})


if __name__ == "__main__":

    MINIO_ENDPOINT = os.environ['MINIO_ENDPOINT']
    MINIO_USERNAME = os.environ['MINIO_USERNAME']
    MINIO_PASSWORD = os.environ['MINIO_PASSWORD']
    MINIO_LOG_FILE = os.environ['MINIO_LOG_FILE']
    MINIO_BUCKET = os.environ['MINIO_BUCKET']

    VECTORIZER = None
    MODEL = None

    try:
        var_list = ['MINIO_ENDPOINT',
                    'MINIO_USERNAME',
                    'MINIO_PASSWORD',
                    'MINIO_BUCKET',
                    'MINIO_LOG_FILE']
        for env_var in var_list:
            if env_var not in os.environ:
                raise TypeError
    except TypeError:
        sys.exit("Error: Please provide all required environmental variables")

    download_and_unpickle_model()

    with open("classifier_log_file.json", "wt", encoding="utf-8") as log_fl:
        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.JSONRenderer()
            ],
            logger_factory=structlog.WriteLoggerFactory(file=log_fl)
        )
        app.run(port=8888, debug=False)
