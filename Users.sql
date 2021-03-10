PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;
CREATE TABLE Users (Username text PRIMARY KEY, Password text NOT NULL, Email varchar(255) NOT NULL);
CREATE TABLE Following (Username text NOT NULL PRIMARY KEY, Follow text, FOREIGN KEY (USERNAME) REFERENCES Users (Username));
COMMIT;
