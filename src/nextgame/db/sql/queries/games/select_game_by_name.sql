SELECT name as game_name,
    id AS game_id,
    min_players ,
    max_players,
    est_avg_minutes,
    weight
FROM games
WHERE name = ?;