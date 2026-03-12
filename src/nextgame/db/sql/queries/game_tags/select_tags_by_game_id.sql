SELECT tags.id AS tag_id, tags.name AS tag_name
FROM game_tags
JOIN tags
    ON tags.id = game_tags.tag_id
WHERE game_tags.game_id = (?);