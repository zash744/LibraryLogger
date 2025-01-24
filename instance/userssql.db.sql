BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "book" (
	"id"	INTEGER NOT NULL,
	"title"	VARCHAR(250) NOT NULL,
	"year"	INTEGER NOT NULL,
	"rating"	FLOAT,
	"ranking"	INTEGER,
	"review"	VARCHAR(250),
	"img_url"	VARCHAR(250) NOT NULL,
	"user_id"	INTEGER NOT NULL,
	PRIMARY KEY("id"),
	FOREIGN KEY("user_id") REFERENCES "user"("id")
);
CREATE TABLE IF NOT EXISTS "user" (
	"id"	INTEGER NOT NULL,
	"email"	VARCHAR(100) NOT NULL,
	"password"	VARCHAR(100) NOT NULL,
	"name"	VARCHAR(1000) NOT NULL,
	UNIQUE("email"),
	PRIMARY KEY("id")
);
INSERT INTO "book" VALUES (1,'Heartless',2016,10.0,2,'Fantastic','https://covers.openlibrary.org/b/id/8197844-L.jpg',1);
INSERT INTO "book" VALUES (2,'Harry Potter and the Deathly Hallows',2007,10.0,1,'Amazing','https://covers.openlibrary.org/b/id/10110415-L.jpg',1);
INSERT INTO "user" VALUES (1,'ashraf.zain.a@gmail.com','pbkdf2:sha256:600000$lPjd0JHz$291af471cf58b04d377fca2e6a16ac93e5bae635a815f4c46b7204c392baef89','Zain');
INSERT INTO "user" VALUES (2,'gomezema2004@gmail.com','pbkdf2:sha256:600000$e8vqrzFq$2d88ee2aa14e725223761b11b22b2a7bc9a21cae586274eba35a14416627e6b7','Ema');
COMMIT;
