SELECT name, id AS game_id
FROM games
WHERE name IN __IN_CLAUSE__;