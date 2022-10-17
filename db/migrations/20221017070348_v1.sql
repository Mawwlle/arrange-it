-- migrate:up
CREATE TABLE "hobby" (
    designation         VARCHAR(15) NOT NULL,

    PRIMARY KEY (designation)
);


CREATE TABLE "place" (
    name                VARCHAR(100) NOT NULL,
    point               POINT NOT NULL,

    PRIMARY KEY (name)
);


CREATE TABLE "tag" (
    name                VARCHAR(10) NOT NULL,

    PRIMARY KEY (name)
);


CREATE TABLE "rank" (
    designation         VARCHAR(15) NOT NULL,

    PRIMARY KEY (designation)
);


CREATE TABLE "role" (
    name                VARCHAR(15) NOT NULL,

    PRIMARY KEY (name)
);


CREATE TABLE "user" (
    id                  SERIAl,
    nickname            VARCHAR(256) NOT NULL,
    password            VARCHAR(256) NOT NULL, -- !TODO: CREATE HASH
    login               VARCHAR(50) NOT NULL,
    role                VARCHAR(15) NOT NULL,
    name                VARCHAR(25) NOT NULL,
    age                 INT NOT NULL,
    info                TEXT,
    interests           VARCHAR(15) NOT NULL,
    rank                VARCHAR(15) NOT NULL,
    rating              INT NOT NULL DEFAULT 0,

    PRIMARY KEY (id),
    FOREIGN KEY (role) REFERENCES role(name),
    FOREIGN KEY (rank) REFERENCES rank(designation),

    CONSTRAINT user_age CHECK (age > 0 AND age < 120)
);


CREATE TABLE "comment" (
    id                  SERIAL,
    text                VARCHAR(256) NOT NULL,
    "user"              INT NOT NULL,

    PRIMARY KEY (id),
    FOREIGN KEY ("user") REFERENCES user("id")
);


CREATE TYPE STATE AS ENUM ('pending approval', 'active', 'ended', 'rejected');
CREATE TABLE "event" (
    id                  SERIAl,
    organizer           INT NOT NULL,
    subscriber          INT NOT NULL,
    place               VARCHAR(100) NOT NULL,
    photo               BYTEA,
    tag                 VARCHAR(10),
    comment             INT,
    state               STATE,

    PRIMARY KEY (id),
    FOREIGN KEY (place) REFERENCES place(name),
    FOREIGN KEY (comment) REFERENCES comment(id)
);


CREATE TABLE "event_tag_mapper" (
    tag                 VARCHAR(10) NOT NULL,
    event_id            INT NOT NULL,

    PRIMARY KEY (tag, event_id),
    FOREIGN KEY (event_id) REFERENCES event(id),
    FOREIGN KEY (tag) REFERENCES tag(name)
);


CREATE TABLE "user_visit_event" (
    user_id             INT NOT NULL,
    event_id            INT NOT NULL,
    visit               BOOLEAN NOT NULL DEFAULT FALSE,

    PRIMARY KEY (user_id, event_id),
    FOREIGN KEY (user_id) REFERENCES "user"(id),
    FOREIGN KEY (event_id) REFERENCES "event"(id)
);


CREATE TABLE "user_hobby_mapper" (
    designation         VARCHAR(15) NOT NULL,
    "user"                INT NOT NULL,

    PRIMARY KEY ("user", designation),
    FOREIGN KEY (designation) REFERENCES "hobby"(designation),
    FOREIGN KEY ("user") REFERENCES "user"(id)
);




-- migrate:down
DROP TABLE "user_visit_event";
DROP TABLE "event_tag_mapper";
DROP TABLE "user_hobby_mapper";
DROP TABLE "user";
DROP TABLE "event";

DROP TYPE STATE;


DROP TABLE "hobby";
DROP TABLE "place";
DROP TABLE "tag";
DROP TABLE "rank";
DROP TABLE "role";
