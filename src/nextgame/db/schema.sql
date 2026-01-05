-- Create games table
CREATE TABLE IF NOT EXISTS games (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    min_players INTEGER NOT NULL CHECK (min_players >= 1),
    max_players INTEGER NOT NULL,
    est_avg_minutes FLOAT NOT NULL CHECK (est_avg_minutes > 0),
    weight FLOAT,
    CHECK (min_players <= max_players)
);

-- Create tags table
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

-- Create game_tags table
CREATE TABLE IF NOT EXISTS game_tags (
    game_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    UNIQUE (game_id, tag_id)
);

-- Create sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY,
    game_id INTEGER NOT NULL,
    player_count INTEGER NOT NULL CHECK (player_count >= 1),
    duration_minutes INTEGER NOT NULL CHECK (duration_minutes > 0),
    played_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (game_id) REFERENCES games(id)
);
