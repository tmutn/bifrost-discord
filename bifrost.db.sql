-- Bifrost Election Database DDL

BEGIN TRANSACTION;
DROP TABLE IF EXISTS "voter_votes_electable";
CREATE TABLE IF NOT EXISTS "voter_votes_electable" (
	"member_id"	INTEGER,
	"electable_id"	INTEGER,
	PRIMARY KEY("member_id","electable_id"),
	FOREIGN KEY("member_id") REFERENCES "voter"("member_id")
);
DROP TABLE IF EXISTS "electable_congressman";
CREATE TABLE IF NOT EXISTS "electable_congressman" (
	"member_id"	INTEGER NOT NULL UNIQUE,
	"discord_username"	TEXT UNIQUE,
	"text_channel_id"	INTEGER UNIQUE,
	"guild_id"	INTEGER NOT NULL,
	"list_id"	INTEGER UNIQUE,
	"list_name"	TEXT UNIQUE,
	"list_image"	INTEGER,
	"list_color"	INTEGER,
	"date_joined"	INTEGER DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY("member_id"),
	FOREIGN KEY("guild_id") REFERENCES "election"("election_id")
);
DROP TABLE IF EXISTS "pending_postulation_offer";
CREATE TABLE IF NOT EXISTS "pending_postulation_offer" (
	"postulator_member_id"	INTEGER,
	"postulated_member_id"	INTEGER,
	"confirmation_channel"	INTEGER,
	"role_id"	INTEGER,
	PRIMARY KEY("confirmation_channel","postulated_member_id")
);
DROP TABLE IF EXISTS "election_role";
CREATE TABLE IF NOT EXISTS "election_role" (
	"role_id"	INTEGER UNIQUE,
	"election_id"	INTEGER,
	"role_name"	INTEGER,
	"amount_per_congressman"	INTEGER,
	"is_mandatory"	INTEGER,
	"casts_vote"	INTEGER
);
DROP TABLE IF EXISTS "confirmed_candidate";
CREATE TABLE IF NOT EXISTS "confirmed_candidate" (
	"candidate_member_id"	INTEGER NOT NULL UNIQUE,
	"candidate_postulated_role_id"	INTEGER,
	"congressman_id"	INTEGER NOT NULL
);
DROP TABLE IF EXISTS "election";
CREATE TABLE IF NOT EXISTS "election" (
	"election_id"	INTEGER NOT NULL UNIQUE,
	"starting_date"	INTEGER DEFAULT CURRENT_TIMESTAMP,
	"is_parcial"	INTEGER DEFAULT 1,
	"category_electables_id"	INTEGER UNIQUE,
	"category_booths_id"	INTEGER UNIQUE,
	"postulation_phase"	INTEGER DEFAULT 1,
	PRIMARY KEY("election_id")
);
DROP TABLE IF EXISTS "voter";
CREATE TABLE IF NOT EXISTS "voter" (
	"member_id"	INTEGER,
	"voting_private_channel_id"	INTEGER UNIQUE,
	"guild_id"	INTEGER,
	PRIMARY KEY("member_id")
);
COMMIT;
