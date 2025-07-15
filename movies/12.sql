SELECT a.title
FROM movies a
JOIN stars b ON a.id = b.movie_id
JOIN stars c ON a.id = c.movie_id
JOIN people p1 ON b.person_id = p1.id
JOIN people p2 ON c.person_id = p2.id
WHERE p1.name = 'Bradley Cooper' AND p2.name = 'Jennifer Lawrence'
