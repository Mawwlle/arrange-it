-- migrate:up
INSERT INTO "rank"("designation") VALUES ('organizer'), ('visitor'), ('an avid visitor');
INSERT INTO "role"("name") VALUES ('subscriber'), ('administrator'), ('organizer');

-- migrate:down

