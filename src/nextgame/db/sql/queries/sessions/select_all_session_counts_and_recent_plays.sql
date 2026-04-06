SELECT games.name as game_name,
    COUNT(sessions.id) AS total_sessions,
    MAX(sessions.played_on) AS last_played_on
FROM sessions
JOIN games
ON games.id = sessions.game_id
GROUP BY sessions.game_id;