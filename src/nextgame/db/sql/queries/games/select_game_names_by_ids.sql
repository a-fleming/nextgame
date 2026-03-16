SELECT name, id AS game_id
FROM games
WHERE id IN __IN_CLAUSE__;