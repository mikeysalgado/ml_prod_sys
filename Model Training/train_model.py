import io
import json
import minio
import os
import pickle
import pandas as pd
from datetime import datetime
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression

# Minio
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


def load_data():
    # Importing model parameters
    imported_params = None
    with open('model_results_2023-05-12_11-11-59.json') as f:
        imported_params = json.load(f)

    # Importing training data
    pathname = "C:/Users/salgadom/Documents/CS4981/P1-repository/cs4981_lab1_email_classifier/part-00000-a994d54f-2d6b-4f3e-b9d1-21c14ae09d0a-c000.json"
    email_data = []
    with open(pathname, encoding='utf8') as json_file:
        for row in json_file:
            row_data = json.loads(row)

            row_dict = {'email_id': row_data['email_id'],
                        'received_timestamp': row_data['received_timestamp'],
                        'body': json.loads(row_data['email_object'])['body'],
                        'label': row_data['label']}

            email_data.append(row_dict)

    # Creating Pandas DataFrame
    emails_df = pd.DataFrame.from_dict(email_data)

    return imported_params, emails_df


def train_model(imported_params, emails_df):
    if imported_params is not None:
        # Reading parameters
        print(imported_params)
        params = imported_params['best_params']

        # Initializing and fitting CountVectorizer
        vectorizer = CountVectorizer(min_df=params['vectorizer__min_df'])
        train_counts = vectorizer.fit_transform(emails_df['body'].values)

        # Initializing model
        model = LogisticRegression(C=params['classifier__C'], penalty=params['classifier__penalty'], solver=params['classifier__solver'])

        # Training model on all data
        model.fit(train_counts.toarray(), emails_df['label'].to_numpy())
        return model, vectorizer
    return None


def upload_file(model, vectorizer):
    client = connection_minio()

    # Saving model as a pickle file
    model_filename = datetime.now().strftime("trained_model_%Y-%m-%d_%H-%M-%S.pkl")
    pickle_file = pickle.dumps({'model': model,'vectorizer': vectorizer})

    client.put_object(bucket_name='models',
                      object_name=model_filename,
                      data=io.BytesIO(pickle_file),
                      length=len(pickle_file))


if __name__ == "__main__":
    print("Importing data...")
    imported_params, emails_df = load_data()
    print("Training model...")
    model, vectorizer = train_model(imported_params, emails_df)
    print("Uploading to bucket...")
    upload_file(model, vectorizer)
