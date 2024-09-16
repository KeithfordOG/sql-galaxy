SELECT *
FROM planets AS p
FULL JOIN missions AS m ON p.planet_id = m.planet_id
FULL JOIN moons AS n ON p.planet_id = n.planet_id