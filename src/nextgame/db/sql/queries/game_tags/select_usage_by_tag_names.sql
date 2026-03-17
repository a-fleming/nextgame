SELECT tags.name AS tag_name, COUNT(*) AS usage
FROM game_tags 
JOIN tags 
    ON game_tags.tag_id = tags.id 
WHERE tag_name IN __IN_CLAUSE__
GROUP BY tag_name;