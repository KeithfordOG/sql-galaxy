-- Step 2: Connect to the database
\c sql_odyssey;

-- Step 3: Create planets table with additional constraints and index
CREATE TABLE IF NOT EXISTS planets (
    planet_id SERIAL PRIMARY KEY,
    planet_name VARCHAR(50) NOT NULL,
    distance_from_earth INT CHECK (distance_from_earth >= 0),
    discoverer VARCHAR (100),
    discovery_year INT CHECK (discovery_year >= -500)
);

CREATE INDEX idx_planets_discovery_year ON planets (discovery_year);

-- Step 4: Create missions table
CREATE TABLE IF NOT EXISTS missions (
    mission_id SERIAL PRIMARY KEY,
    planet_id INT REFERENCES planets(planet_id),
    mission_name VARCHAR (100) NOT NULL,
    mission_date DATE,
    crew_size INT
);

CREATE INDEX idx_missions_planet_id ON missions (planet_id);

-- Step 5: Create moons table
CREATE TABLE IF NOT EXISTS moons (
    moon_id SERIAL PRIMARY KEY,         
    moon_name VARCHAR(100) NOT NULL,     
    planet_id INT REFERENCES planets(planet_id),  
    diameter_km DECIMAL(10, 2),       
    discovered_by VARCHAR(100),         
    discovery_year INT                   
);

CREATE INDEX idx_moons_planet_id ON moons (planet_id);

-- Step 6: Insert planets data
INSERT INTO planets (planet_name, distance_from_earth, discoverer, discovery_year)
VALUES 
('Venus', 108, 'Babylonians', -500),
('Mars', 225, 'Galileo', 1610),
('Jupiter', 778, 'Galileo', 1610),
('Saturn', 1433, 'Huygens', 1655),
('Neptune', 4495, 'Le Verrier', 1846),
('Pluto', 5906, 'Tombaugh', 1930),
('Uranus', 2871, 'William Herschel', 1781),
('Mercury', 77, 'Known since antiquity', NULL),
('Earth', 0, 'Known since antiquity', NULL);

-- Step 7: Insert missions data
INSERT INTO missions (planet_id, mission_name, mission_date, crew_size)
VALUES
(1, 'Mars Rover Mission', '2004-01-04', 6),
(1, 'Mars Pathfinder', '1997-07-04', 5),
(2, 'Jupiter Probe', '1973-12-03', 8),
(3, 'Saturn Orbiter', '2004-07-01', 3),
(4, 'Neptune Explorer', '1989-08-25', 7),
(5, 'Pluto Flyby', '2015-07-14', 3),
(6, 'Venus Research', '1982-03-05', 4),
(7, 'Voyager 2', '1986-01-24', 0),  
(8, 'Mariner 10', '1974-03-29', 0),  
(8, 'MESSENGER', '2004-08-03', 0),   
(8, 'BepiColombo', '2018-10-20', 0);

-- Step 8: Insert moons data
INSERT INTO moons (moon_name, planet_id, diameter_km, discovered_by, discovery_year)
VALUES 
('Phobos', 1, 22.2, 'Asaph Hall', 1877),
('Deimos', 1, 12.4, 'Asaph Hall', 1877),
('Io', 2, 3643.2, 'Galileo', 1610),
('Europa', 2, 3121.6, 'Galileo', 1610),
('Ganymede', 2, 5262.4, 'Galileo', 1610),
('Callisto', 2, 4820.6, 'Galileo', 1610),
('Titan', 3, 5150, 'Christiaan Huygens', 1655),
('Enceladus', 3, 504, 'William Herschel', 1789),
('Triton', 4, 2706.8, 'William Lassell', 1846),
('Charon', 5, 1212, 'James Christy', 1978);
