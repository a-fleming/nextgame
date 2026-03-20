SELECT sessions.id AS session_id,
    sessions.played_on AS played_on,
    games.name AS game_name,
    sessions.player_count AS player_count,
    sessions.duration_minutes AS duration_minutes
FROM sessions
JOIN games
    ON sessions.game_id = games.id;