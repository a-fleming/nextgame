DELETE FROM game_tags
WHERE game_id = (?)
    AND tag_id IN __IN_CLAUSE__;