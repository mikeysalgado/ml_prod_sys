# Setup required for Ingestion Service and Mock Mailbox
### By Noah Stiemke, Micheal Salgado, Kyle Robinson

## Create Database
postgres=# CREATE DATABASE email_ingestion;
postgres=# \c email_ingestion;
email_ingestion=#

## Create User
email_ingestion=# CREATE USER your-desired-user-name WITH PASSWORD 'your-password'

*Please do not use example user and password as actual user and password*

## Run Database Creation Script
\i 'C:/Path/To/Creation/Script/DB_creation.sql'

## Define Environment Variables
POSTGRES_HOST = 127.0.0.1
POSTGRES_DATABASE = email_ingestion
POSTGRES_USERNAME = your-desired-user-name
POSTGRES_PASSWORD = your-password

## Run Scripts
POSTGRES_DATABASE=email_ingestion POSTGRES_USERNAME=ingestion_service POSTGRES_PASSWORD='puppet-soil-SWEETEN' POSTGRES_HOST=127.0.0.1 python email_service.py

POSTGRES_DATABASE=email_ingestion POSTGRES_USERNAME=ingestion_service POSTGRES_PASSWORD='puppet-soil-SWEETEN' POSTGRES_HOST=127.0.0.1 python ingestion_service.py

## Run Simulation
1. Run both services
2. python spam_simulator.py simulate-user --email-dir C:/Temp/email_json_dataset1 --email-url http://127.0.0.1:8888/ --mailbox-url http://127.0.0.1:8889/ --number-emails 1000 --average-events-per-email 20

## Minio Environment Variables
MINIO_BUCKET=log-files;MINIO_ENDPOINT=127.0.0.1:9000;MINIO_LOG_FILE=log_file.json;MINIO_PASSWORD=your_password_here;MINIO_USERNAME=log-depositor;