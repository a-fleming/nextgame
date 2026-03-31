SELECT games.id AS game_id,
    games.name AS name,
    games.min_players AS min_players,
    games.max_players AS max_players,
    games.est_avg_minutes AS est_avg_minutes, 
    games.weight AS weight
FROM games
WHERE __WHERE_CLAUSE__
ORDER BY name ASC;
