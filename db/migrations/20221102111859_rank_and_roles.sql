-- migrate:up
INSERT INTO "rank"("name", "description") VALUES ('low', 'Low rank. Not prior events'), ('advance', 'Already good in this. All events'), ('high', 'Subscribes to private events');
INSERT INTO "role"("name", "description") VALUES ('subscriber', 'Can subscribe to event'), ('administrator', 'Verification'), ('organizer', 'Organize events');

-- migrate:down

