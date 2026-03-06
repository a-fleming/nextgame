SELECT id as tag_id, name
FROM tags
WHERE name IN __IN_CLAUSE__;