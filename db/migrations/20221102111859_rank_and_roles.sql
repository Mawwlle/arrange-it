-- migrate:up
INSERT INTO "rank"("name", "description") VALUES ('low', 'Low rank. Not prior events'), ('advance', 'Already good in this. All events'), ('high', 'Subscribes to private events');
INSERT INTO "role"("name", "description") VALUES ('subscriber', 'Can subscribe to event'), ('administrator', 'Verification'), ('organizer', 'Organize events');
INSERT INTO "place"("name", "point") VALUES ('magazin', POINT(1,2)), ('kino', POINT(1,4)), ('concert_hall', POINT(1,1.2323));
INSERT INTO "tag"("name") VALUES ('cats'), ('dogs'), ('eats'), ('jokes'), ('stand up'), ('love');
-- migrate:down

DELETE FROM "place";
DELETE FROM "role";
DELETE FROM "rank";
DELETE FROM "tag";