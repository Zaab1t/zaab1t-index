DROP TABLE IF EXISTS video;
CREATE TABLE video (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT UNIQUE,
    champ TEXT,
    recorded_on TEXT,
    friends TEXT,
    tags TEXT
);
