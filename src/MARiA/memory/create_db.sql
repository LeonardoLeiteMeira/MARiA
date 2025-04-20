CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE users (
  id                       UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
  name                     TEXT         NOT NULL,
  email                    TEXT,
  accepts_communications   BOOLEAN      NOT NULL DEFAULT FALSE,
  phone_number             TEXT         NOT NULL UNIQUE,
  created_at               TIMESTAMPTZ  NOT NULL DEFAULT now()
);

insert into users (name, email, accepts_communications, phone_number) values ('Leonardo Leite Meira', 'leonardo.leitemeira10@gmail.com', TRUE, '+5531933057272');

select * from users;

select name, email from users where accepts_communications = true;

CREATE TABLE IF NOT EXISTS checkpoints (
  thread_id   UUID         NOT NULL DEFAULT uuid_generate_v4(),
  user_id     UUID         NOT NULL,
  checkpoint  BYTEA        NOT NULL,
  thread_ts   TIMESTAMPTZ  NOT NULL DEFAULT now(),
  parent_ts   TIMESTAMPTZ,
  PRIMARY KEY (thread_id, thread_ts),
  CONSTRAINT fk_user
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS threads (
  thread_id   UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id     UUID        NOT NULL  REFERENCES users(id),
  created_at  TIMESTAMPTZ NOT NULL  DEFAULT now(),
  status      TEXT        NOT NULL  DEFAULT 'open'
);

