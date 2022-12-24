-- migrate:up

CREATE TABLE "hobby" (
    "id"                INTEGER GENERATED BY DEFAULT AS IDENTITY,
    "designation"       VARCHAR(15) NOT NULL,

    PRIMARY KEY ("id"),
    UNIQUE ("designation")
);


CREATE TABLE "place" (
    "id"                INTEGER GENERATED BY DEFAULT AS IDENTITY,
    "name"              VARCHAR(100) NOT NULL,
    "point"             POINT NOT NULL,

    PRIMARY KEY ("id"),
    UNIQUE ("name")
);


CREATE TABLE "tag" (
    "id"                INTEGER GENERATED BY DEFAULT AS IDENTITY,
    "name"              VARCHAR(10) NOT NULL,

    PRIMARY KEY ("id"),
    UNIQUE ("name")
);


CREATE TABLE "rank" (
    "id"                INTEGER GENERATED BY DEFAULT AS IDENTITY,
    "name"              VARCHAR(15) NOT NULL,
    "description"       VARCHAR(250) NOT NULL,


    PRIMARY KEY ("id"),
    UNIQUE ("name")
);


CREATE TABLE "role" (
    "id"                INTEGER GENERATED BY DEFAULT AS IDENTITY,
    "name"              VARCHAR(15) NOT NULL,
    "description"       VARCHAR(250) NOT NULL,


    PRIMARY KEY ("id"),
    UNIQUE ("name")
);


CREATE TABLE "user" (
    "id"                INTEGER GENERATED BY DEFAULT AS IDENTITY,
    "username"          VARCHAR(256) NOT NULL,
    "password"          VARCHAR(256) NOT NULL,
    "email"             VARCHAR(50) NOT NULL,
    "role"              INT,
    "name"              VARCHAR(25) NOT NULL,
    "birthday"          DATE,
    "info"              TEXT,
    "interests"         VARCHAR(15),
    "rank"              INT,
    "rating"            INT NOT NULL DEFAULT 0,
    "verified"          BOOLEAN NOT NULL DEFAULT FALSE,

    PRIMARY KEY ("id"),
    UNIQUE ("username"),
    UNIQUE ("email"),
    FOREIGN KEY ("role")
        REFERENCES "role"("id")
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY ("rank")
        REFERENCES "rank"("id")
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE "admin" (
    "id"                INTEGER GENERATED BY DEFAULT AS IDENTITY, 
    "user_id"           INTEGER NOT NULL,   

    PRIMARY KEY ("id"),
    UNIQUE("user_id"),
    FOREIGN KEY ("user_id")
        REFERENCES "user"("id")
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE "photo" (
    "id"                INTEGER GENERATED BY DEFAULT AS IDENTITY,
    "photo"             BYTEA,
    "media_type"        VARCHAR(30) NOT NULL,

    PRIMARY KEY ("id")
);

CREATE TYPE STATE AS ENUM ('pending approval', 'active', 'ended', 'rejected');
CREATE TABLE "event" (
    "id"                INTEGER GENERATED BY DEFAULT AS IDENTITY,
    "organizer"         INT NOT NULL,
    "place"             INT NOT NULL,
    "description"       TEXT,
    "photo"             INT,
    "state"             STATE DEFAULT 'pending approval',
    "date"              TIMESTAMP NOT NULL,
    "verified"          BOOLEAN NOT NULL DEFAULT FALSE,


    PRIMARY KEY ("id"),
    UNIQUE ("photo"),
    FOREIGN KEY ("photo")
        REFERENCES "photo"("id")
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY ("place")
        REFERENCES "place"("id")
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE "comment" (
    "id"                INTEGER GENERATED BY DEFAULT AS IDENTITY,
    "text"              VARCHAR(256) NOT NULL,
    "user"              INT NOT NULL,
    "date"              TIMESTAMP NOT NULL,
    "event"             INT NOT NULL,

    PRIMARY KEY ("id"),
    FOREIGN KEY ("user")
        REFERENCES "user"("id")
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY ("event")
        REFERENCES "event"("id")
        ON DELETE CASCADE
        ON UPDATE CASCADE
);


CREATE TABLE "event_tag_mapper" (
    "tag_id"            INT NOT NULL,
    "event_id"          INT NOT NULL,

    PRIMARY KEY ("tag_id", "event_id"),
    FOREIGN KEY ("event_id")
        REFERENCES "event"("id")
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY ("tag_id")
        REFERENCES "tag"("id")
        ON DELETE CASCADE
        ON UPDATE CASCADE
);


CREATE TABLE "user_visit_event" (
    "user_id"             INT NOT NULL,
    "event_id"            INT NOT NULL,
    "visit"               BOOLEAN NOT NULL DEFAULT FALSE,

    PRIMARY KEY ("user_id", "event_id"),
    FOREIGN KEY ("user_id")
        REFERENCES "user"("id")
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY ("event_id")
        REFERENCES "event"("id")
        ON DELETE CASCADE
        ON UPDATE CASCADE
);


CREATE TABLE "user_hobby_mapper" (
    "hobby_id"            INT NOT NULL,
    "user_id"             INT NOT NULL,

    PRIMARY KEY ("user_id", "hobby_id"),
    FOREIGN KEY ("hobby_id")
        REFERENCES "hobby"("id")
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY ("user_id")
        REFERENCES "user"("id")
        ON DELETE CASCADE
        ON UPDATE CASCADE
);


-- migrate:down
DROP TABLE "user_hobby_mapper";
DROP TABLE "user_visit_event";
DROP TABLE "event_tag_mapper";
DROP TABLE "comment";
DROP TABLE "event";
DROP TABLE "photo";
DROP TABLE "admin";
DROP TABLE "user";

DROP TABLE "place";
DROP TABLE "hobby";
DROP TABLE "rank";
DROP TABLE "tag";
DROP TABLE "role";

DROP TYPE STATE;
