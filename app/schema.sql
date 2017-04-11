DROP TABLE IF EXISTS video;
CREATE TABLE video (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    champ TEXT,
    recorded_on TEXT,
    friends TEXT,
    tags TEXT
);
