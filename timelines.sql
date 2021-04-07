PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;
CREATE TABLE Posts ( ID int PRIMARY KEY, Username text NOT NULL, Message text);
INSERT INTO Posts (username, message) VALUES ('pemami', 'hello world!');
INSERT INTO Posts (username, message) VALUES ('dumbo', 'I love puppies :)');
COMMIT;
