-- $ psql
-- CREATE DATABASE quantumrocket_dev;
-- <user>=# \connect quantumrocket_dev;
-- CREATE USER qr;
-- GRANT ALL PRIVILEGES ON DATABASE quantumrocket_dev TO qr;
-- GRANT USAGE ON SCHEMA public TO fluffy;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO qr;
-- ALTER USER "qr" WITH PASSWORD 'fluffy';


--
-- things
--
DROP TABLE IF EXISTS things;
CREATE TABLE IF NOT EXISTS things (
    key     TEXT NOT NULL PRIMARY KEY,
    value   TEXT NOT NULL,
    created TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

INSERT INTO things (key, value) VALUES ('page.index.help', '<p>This is a simple example of a website created using Flask.</p>');

INSERT INTO things (key, value) VALUES ('page.dashboard.help', '<p>On this page, you can monitor stuff.</p>');

INSERT INTO things (key, value) VALUES ('page.my_widgets.help', '<p>This page contains your widgets.</p><p>On this page, you can configure your existing widgets and add new ones.</p>');

INSERT INTO things (key, value) VALUES ('page.my_profile.help', '<p>On this page, you can update your info.</p>');

 
--
-- users
--
DROP TABLE IF EXISTS users;
CREATE TABLE IF NOT EXISTS users (
    user_ulid                   TEXT NOT NULL PRIMARY KEY,
    email                       TEXT NOT NULL,
    display_email               TEXT NOT NULL,
    password                    TEXT NOT NULL,
    full_name                   TEXT NOT NULL DEFAULT '',
    phone                       TEXT NOT NULL DEFAULT '',
    status                      TEXT NOT NULL DEFAULT 'new',  -- 'active', 'inactive', etc.
    pref_show_page_help         TEXT NOT NULL DEFAULT 'yes',
    created                     TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated                     TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

DROP INDEX IF EXISTS i_users_email;
CREATE UNIQUE INDEX i_users_email ON users (lower(email));

DROP INDEX IF EXISTS i_users_status;
CREATE INDEX IF NOT EXISTS i_users_status ON users (status);


--
-- widgets
--
DROP TABLE IF EXISTS widgets;
CREATE TABLE IF NOT EXISTS widgets (
    widget_ulid            TEXT NOT NULL PRIMARY KEY,
    widget_name            TEXT NOT NULL,
    user_ulid              TEXT NOT NULL,
    user_email             TEXT NOT NULL,
    description            TEXT NOT NULL DEFAULT '',
    created                TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated                TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);


--
-- signins
--

DROP TABLE IF EXISTS signins;
CREATE TABLE IF NOT EXISTS signins (
    signin_ulid TEXT NOT NULL PRIMARY KEY,
    user_email  TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'pending',
    created     TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated     TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),

    CONSTRAINT uk_signins_user_email UNIQUE (user_email)
);


--
-- visits
--
DROP TABLE IF EXISTS visits;
CREATE TABLE IF NOT EXISTS visits (
    visit_ulid  TEXT NOT NULL PRIMARY KEY,
    user_ulid   TEXT NOT NULL,
    user_email  TEXT NOT NULL,
    controller  TEXT NOT NULL,
    function    TEXT NOT NULL,
    description TEXT,
    host        TEXT NOT NULL,
    origin      TEXT,
    referer     TEXT,
    language    TEXT,
    user_agent  TEXT,
    created     TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);
