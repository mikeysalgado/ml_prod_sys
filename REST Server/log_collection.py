from datetime import datetime
import pygtail
from time import sleep
import sys
import minio
import os
import json

MINIO_ENDPOINT = os.environ['MINIO_ENDPOINT']
MINIO_USERNAME = os.environ['MINIO_USERNAME']
MINIO_PASSWORD = os.environ['MINIO_PASSWORD']
MINIO_LOG_FILE = os.environ['MINIO_LOG_FILE']
MINIO_BUCKET = os.environ['MINIO_BUCKET']


def connection_minio():
    client = minio.Minio(
        endpoint=MINIO_ENDPOINT,
        access_key=MINIO_USERNAME,
        secret_key=MINIO_PASSWORD,
        secure=False
    )
    return client


def upload_changes_to_minio():
    # open minio connection
    mini = connection_minio()

    # get current datetime and parse file name
    now = datetime.now()
    file_chunk_name = now.strftime("log_file_%m%d%y_%H%M%S.json")

    # create file
    f = open(file_chunk_name, 'w')

    # put all changes into new file
    for line in pygtail.Pygtail(MINIO_LOG_FILE):
        f.write(line)
    f.close()

    # upload new file to minio
    mini.fput_object(MINIO_BUCKET, file_chunk_name, file_chunk_name)

    # delete file
    if os.path.exists(file_chunk_name):
        os.remove(file_chunk_name)


if __name__ == "__main__":
    while True:
        upload_changes_to_minio()
        sleep(60*1)
