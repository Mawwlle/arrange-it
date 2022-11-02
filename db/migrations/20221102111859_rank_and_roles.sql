-- migrate:up
INSERT INTO "rank"("designation") VALUES ('a'), ('d'), ('s');
INSERT INTO "role"("name") VALUES ('b'), ('c'), ('e');

-- migrate:down

