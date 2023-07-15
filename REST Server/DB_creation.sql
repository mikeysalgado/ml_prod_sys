DROP TABLE IF EXISTS emails CASCADE;

CREATE TABLE emails(
	email_id integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
	received_timestamp timestamp NOT NULL,
	email_object jsonb NOT NULL,
	email_folder text NOT NULL
);

DROP TABLE IF EXISTS labels CASCADE;

CREATE TABLE labels(
	label_id integer PRIMARY KEY,
	label_value TEXT NOT NULL
);

INSERT INTO labels(label_id, label_value) VALUES(1, 'spam');
INSERT INTO labels(label_id, label_value) VALUES(2, 'read');
INSERT INTO labels(label_id, label_value) VALUES(3, 'important');

DROP TABLE IF EXISTS email_label CASCADE;

CREATE TABLE email_label (
  email_id integer NOT NULL,
  label_id integer NOT NULL,
  PRIMARY KEY (email_id, label_id),
  CONSTRAINT fk_email FOREIGN KEY(email_id) REFERENCES emails(email_id),
  CONSTRAINT fk_label FOREIGN KEY(label_id) REFERENCES labels(label_id)
);

GRANT SELECT, INSERT, UPDATE ON emails TO ingestion_service;
GRANT SELECT, INSERT, UPDATE, DELETE ON email_label TO ingestion_service;
GRANT SELECT, INSERT, UPDATE ON labels TO ingestion_service;