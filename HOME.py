import streamlit as st
import pandas as pd
import sqlparse
import psycopg2
import time
from urllib.parse import urlparse

# PostgreSQL Database connection using Streamlit secrets
def create_connection():
    try:
        # Retrieve the database URL from Streamlit secrets
        url = st.secrets["postgresql"]["DB_URL"]
        
        # Parse the URL to extract connection parameters
        parsed_url = urlparse(url)
        
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            host=parsed_url.hostname,
            database=parsed_url.path[1:],  # Remove leading '/'
            user=parsed_url.username,
            password=parsed_url.password,
            port=parsed_url.port
        )
        return conn
    except Exception as e:
        st.error(f"Error connecting to the database: {e}")
        return None


# Execute SQL query and return results as DataFrame
def execute_sql_query(query):
    conn = create_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(query)
            columns = [desc[0] for desc in cur.description]
            result = cur.fetchall()
            cur.close()
            conn.close()
            return pd.DataFrame(result, columns=columns)  # Return DataFrame
        except Exception as e:
            st.error(f"Error executing query: {e}")
            return pd.DataFrame()  # Return an empty DataFrame in case of error
    else:
        return pd.DataFrame()  # Return an empty DataFrame if connection fails


# Welcome section for SQL Galaxy
st.title("SQL GALAXY")
st.subheader("One small query for developers, one giant JOIN for database kind")
st.write('---')

st.image("images/rocket.png", caption="Welcome to SQL Galaxy!*Image Generated by ChatGPT4")

# Tabs for SQL overview and Tips and Tricks
tabs = st.tabs(["What is SQL?", "Beginner SQL Tips", "Intermediate SQL Tips (Joins)", "Advanced SQL Tips (Subqueries)"])

# "What is SQL?" Tab
with tabs[0]:
    st.header("What is SQL?")
    st.write("""
    SQL, or Structured Query Language, is the standard for working with relational databases. These databases store information in tables made up of rows and columns. SQL allows users to access, modify, and manage the data in these tables.

    **Ever wondered how online stores keep track of thousands of products, or how social media platforms manage millions of user profiles?** That's SQL at work behind the scenes!

    ---

    ## Understanding Relational Databases

    Before diving into SQL, let's understand what a **relational database** is.

    Imagine a digital filing system where data is neatly organized into tables, much like spreadsheets. Each table represents a specific topic or entity, such as `PLANETS`,  `MISSIONS` or `MOONS`.

    ### Tables, Rows, and Columns

    - **Tables**: Collections of related data organized in rows and columns.
    - **Rows**: Individual records within a table.
    - **Columns**: Specific attributes or fields that describe the data.

    For example, a `PLANETS` table might look like this:

    | planet_id | planet_name | distance_from_earth | discoverer     |
    |-----------|-------------|---------------------|----------------|
    | 1         | Mercury     | 77 million km       | Ancient Greeks |
    | 2         | Venus       | 38 million km       | Babylonians    |
    | 3         | Earth       | 0 km                | N/A            |
    | 4         | Mars        | 55 million km       | Egyptians      |

    ---
    
    ## Primary Keys and Foreign Keys

    Understanding how tables relate to each other is crucial in relational databases.

    ### Primary Keys

    A **primary key** is a column (or a combination of columns) that uniquely identifies each record in a table.

    - **Purpose**: Ensure that each record can be uniquely identified.
    - **Example**: In the `PLANETS` table, `planet_id` serves as the primary key, ensuring every planet has a unique identifier.

    **Planets Table Example:**

    | **planet_id (Primary Key)** | planet_name | distance_from_earth | discoverer     |
    |-----------------------------|-------------|---------------------|----------------|
    | 1                           | Mercury     | 77 million km       | Ancient Greeks |
    | 2                           | Venus       | 38 million km       | Babylonians    |
    | 3                           | Earth       | 0 km                | N/A            |
    | 4                           | Mars        | 55 million km       | Egyptians      |

    ### Foreign Keys

    A **foreign key** is a column in one table that references the primary key of another table, creating a relationship between the two tables.

    - **Purpose**: Link related data across different tables.
    - **Example**: In a `MISSIONS` table, `planet_id` is a foreign key referencing `planet_id` in the `PLANETS` table. This links each mission to the planet it is associated with.
    
    **Missions Table Example:**

    | **mission_id (PK)** | mission_name    | **planet_id (Foreign Key)** |
    |------------|-----------------|-----------------------------|
    | 1          | Apollo 11       | 3                           |
    | 2          | Viking 1        | 4                           |
    | 3          | Mariner 10      | 1                           |
    | 4          | Venus Express   | 2                           |

    
    ---

    ## Why Use SQL?

    SQL is the language that allows you to interact with relational databases effortlessly.

    - **Retrieve Data**: Ask questions like, "Which planets are closer than 100 million km from Earth?"
    - **Insert Data**: Add new records to your tables.
    - **Update Data**: Modify existing information.
    - **Delete Data**: Remove records that are no longer needed.

    **Example Query:**   "Retrieve all planet names from the planets table"          
    ```sql
    SELECT planet_name 
    FROM planets;         
    ```
    **Expected Output:**
    ## Planet Names

    | planet_name |
    |-------------|
    | Venus       |
    | Mars        |
    | Jupiter     |
    | Saturn      |
    | Neptune     |
    | Pluto       |
    | Uranus      |
    | Mercury     |
    | Earth       |

                
    ---

    ## The Core Role of SQL in Real-World Applications

    SQL is essential for efficient data management, powering the backend of modern applications and enabling users to handle large datasets effectively. It plays a vital role in decision-making and data analytics across various industries:

    - **E-commerce**: Managing product catalogs, customer data, and orders.
    - **Finance**: Tracking transactions and generating analytical reports.
    - **Healthcare**: Storing patient records and medical histories.
    - **Social Media**: Handling user profiles, posts, and interactions.
    - **Education**: Managing student information and academic records.
    - **Business Intelligence**: Analyzing big data for strategic decisions.
    - **Transportation**: Managing logistics, tracking shipments, and scheduling.
    - **Government**: Keeping records for public administration and services.

    By enabling quick and reliable access to data, SQL powers the backend of countless applications you use every day.
        
    ---
    
    ## Popular SQL Databases

    There are several SQL database systems, each with unique features:

    - **PostgreSQL**: An open-source database known for its advanced features and strict compliance with SQL standards. It's ideal for complex applications requiring robust data integrity and complex queries.

    - **MySQL**: A widely-used open-source database, especially popular in web applications and with languages like PHP. It's known for its speed and reliability in handling large databases.

    - **SQL Server**: A Microsoft product suitable for enterprise environments requiring high scalability and security. It integrates well with other Microsoft services and offers comprehensive tools for data analysis.

    - **Oracle Database**: Designed for large-scale applications, Oracle offers robust performance, extensive features, and strong security. It's commonly used in enterprise environments that require handling massive amounts of data.

    - **SQLite**: A lightweight, file-based database ideal for mobile apps and small projects. It's serverless, requires zero configuration, and is easy to use, making it perfect for embedded systems and applications with low to medium traffic.

    ---
    ## A Brief History of SQL

    - **1970s**: SQL (Structured Query Language) was developed by IBM researchers Donald D. Chamberlin and Raymond F. Boyce. It was designed to interact with relational databases, based on Edgar F. Codd’s relational model.

    - **1986**: SQL was adopted as a standard by the American National Standards Institute (ANSI), establishing it as the official language for managing and manipulating relational databases.

    - **1987**: The International Organization for Standardization (ISO) also recognized SQL as the standard for database management.

    - **1990s and Beyond**: Over the decades, SQL became the universal language for managing data in relational database management systems (RDBMS). Popular SQL-based databases, like PostgreSQL, MySQL, Oracle, and SQL Server, were developed and widely adopted.

    - **Present Day**: SQL remains a critical tool in data management and is used across virtually every industry. It is supported by all major relational database systems and continues to evolve with new features and optimizations.

    SQL has been the foundation of data-driven systems for decades, and its simplicity, flexibility, and powerful querying capabilities have made it an indispensable skill for data professionals.

    
    

    
    """)

    # Add the "Ready to Begin Your SQL Journey?" prompt only in this tab
    st.write("---")  # Add a divider for separation
    st.markdown("<h2 style='text-align: center;'>🚀 Ready to Start Your SQL Journey?</h2>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Scroll up and select the <em>Beginner Tips</em> tab to get started or test your skills in the Milky Way, Hydra Cluster, or Hercules Supercluster!</h3>", unsafe_allow_html=True)


# Easy SQL Tips Tab
with tabs[1]:
    st.title("Beginner SQL Objectives:""")

    st.write("""
    1. SELECT/FROM
    2. COMPARISON OPERATORS
    3. WHERE/LIKE
    4. AND/OR
    5. COUNT
    """)

    st.write("""
    Learning these basic SQL commands will help you retrieve and filter data from your database. Let's go over each concept with examples, hints, and expected outputs.
    """)         

    st.write('---')

    st.header("1 - SELECT/FROM")
    st.write("- **SELECT**")
    st.write("The `SELECT` statement tells the database which columns you want to retrieve. You can either specify individual columns or use an asterisk (`*`) to select all columns from the table.")
    st.write("- **FROM**:")
    st.write("The `FROM` clause specifies the table from which to retrieve data. After using `SELECT` to specify the columns, you use `FROM` to tell SQL where to look.")


    st.subheader("""
    EXAMPLE 1:    
    Retrieve the `planet_id` & `planet name` from the `PLANETS` table
 
    ```sql
    SELECT planet_id, planet_name 
    FROM planets;
    ```
    This query will rerieve the `planet_id` and `planet_names` in the `PLANETS` table.

    **Expected Output:**      
    | planet_id | planet_name |
    |-----------|-------------|
    | 1         | Venus       |
    | 2         | Mars        |
    | 3         | Jupiter     |
    | 4         | Saturn      |
    | 5         | Neptune     |
    | 6         | Pluto       |
    | 7         | Uranus      |
    | 8         | Mercury     |
    | 9         | Earth       |

    """)

    st.write("\n" * 5)

    st.write("""
    ### EXAMPLE 2:   
    Retrieve all the columns from the `PLANETS` table
  
    ```sql
    SELECT * 
    FROM planets;
    """)
    
    st.write("""This query will retrieve all columns from the `PLANETS` table.
    """)

    st.write("""
            **Expected Output**:
    | planet_id | planet_name | distance_from_earth | discoverer            | discovery_year |
    |-----------|-------------|---------------------|-----------------------|----------------|
    | 1         | Venus       | 108                 | Babylonians           | -500           |
    | 2         | Mars        | 227.9               | Galileo               | 1610           |
    | 3         | Jupiter     | 778                 | Galileo               | 1610           |
    | 4         | Saturn      | 1,433               | Huygens               | 1655           |
    | 5         | Neptune     | 4,495               | Le Verrier            | 1846           |
    | 6         | Pluto       | 5,906               | Tombaugh              | 1930           |
    | 7         | Uranus      | 2,871               | William Herschel      | 1781           |
    | 8         | Mercury     | 77                  | Known since antiquity | None           |
    | 9         | Earth       | 0                   | Known since antiquity | None           |

    """)
             
    st.write("\n" * 5)

   

    st.write("---")


 
    st.header("2 - COMPARISON OPERATORS")
    st.write("""
    Comparison operators are used in SQL to compare two values. They are typically used in `WHERE` clauses to filter data. Common comparison operators include:

    - `=` : Equal to
    - `!=` or `<>` : Not equal to
    - `>` : Greater than
    - `<` : Less than
    - `>=` : Greater than or equal to
    - `<=` : Less than or equal to
    """)

    st.write("---")

    # WHERE Clause section
    st.header("3 - WHERE/LIKE")
    st.write("- **WHERE**")
    st.write("""
    The `WHERE` clause is used to filter records in SQL. It allows you to specify conditions that must be met for rows to be included in the result set.

    You can use the `WHERE` clause with comparison operators (e.g., `=`, `>`, `<`, etc.) to narrow down your results.
    """)

# Example using WHERE Clause
    st.subheader("EXAMPLE:") 
    st.write("Retrieve all missions where the `crew_size` is greater than 3")
    st.write("""
    ```sql
    SELECT * 
    FROM missions 
    WHERE crew_size > 3;
    """)
    st.write("""
    **Expected Output**:
    | mission_id | planet_id | mission_name     | mission_date | crew_size |
    |------------|-----------|------------------|--------------|-----------|
    | 0          | 1         | Mars Rover Mission | 2004-01-04  | 6         |
    | 1          | 1         | Mars Pathfinder   | 1997-07-04  | 5         |
    | 2          | 3         | Jupiter Probe     | 1973-12-03  | 8         |
    | 3          | 5         | Neptune Explorer  | 1989-08-25  | 7         |
    | 4          | 7         | Venus Research    | 1982-03-05  | 4         |

    """)

    st.write("")
    st.write("\n" * 2)  # Adds two blank lines for extra space
    st.write("\n" * 2)  # Adds two blank lines for extra space
    

    st.write("- **LIKE**")
    st.write("""
    The `LIKE` operator in SQL is used for pattern matching in string data. It allows you to search for specific patterns in a column's values. You can use two wildcard characters:
    - `%`: Represents zero or more characters.
    - `_`: Represents a single character.

    The `LIKE` operator is commonly used with the `WHERE` clause to filter results based on patterns.
    """)

    # Example using LIKE
    st.subheader("EXAMPLE:")
    st.write("Retrieve the `moon_name` that start with the letter 'C' ")
    st.write("""
    ```sql
    SELECT moon_name 
    FROM moons 
    WHERE moon_name LIKE 'C%'
    """)
    st.write("""
    | moon_name |
    |-----------|
    | Callisto  |
    | Charon    |

    """)

    st.write("---")

    st.header("4 - AND/OR")

    st.write("""
    The `AND` and `OR` operators are used to combine multiple conditions in a `WHERE` clause. These operators help refine search results based on multiple criteria:

    - **AND**: All conditions must be true for a record to be included.
    """)

    st.write("""
    - **OR**: At least one condition must be true for a record to be included.
    """)


    st.subheader("EXAMPLE 1:")
    st.write("Find the mission that took place after the year 1999 AND has a `crew_size` greater than 5")
    st.write("""
    ```sql
    SELECT * 
    FROM missions 
    WHERE mission_date > '1999-12-31' AND crew_size > 5;         
    """)
    st.write("""
    **Expected Output**:
    | mission_id | planet_id | mission_name     | mission_date | crew_size |
    |------------|-----------|------------------|--------------|-----------|
    | 1          | 1         | Mars Rover Mission | 2004-01-04  | 6         |

    """)

    st.subheader("EXAMPLE 2:")
    st.write("Find all the records for planets discovered after 1700 OR further than 1400 from Earth")
    st.write("""
    ```sql
    SELECT * 
    FROM planets 
    WHERE discovery_year > 1700 OR distance_from_earth > 1400;
    """)

    st.write("""
    **Expected Output**:
    | planet_id | planet_name | distance_from_earth | discoverer        | discovery_year |
    |-----------|-------------|---------------------|-------------------|----------------|
    | 3         | Saturn      | 1433                | Huygens           | 1655           |
    | 4         | Neptune     | 4495                | Le Verrier        | 1846           |
    | 5         | Pluto       | 5906                | Tombaugh          | 1930           |
    | 7         | Uranus      | 2871                | William Herschel  | 1781           |

    """)
    st.write('---')

    # Add the COUNT objective
    st.header("5 - COUNT")
    st.write("- **COUNT**")
    st.write("""
    The `COUNT` function returns the number of rows that match a specified condition. It's often used to determine how many rows exist in a table or how many rows satisfy a `WHERE` clause condition.
    """)

    st.subheader("EXAMPLE :") 
    st.write("Count the number of planets in the PLANETS table")
    st.write("""
    ```sql
    SELECT COUNT(*) 
    FROM planets;
    ```
    This query counts the total number of rows (planets) in the `PLANETS` table.
    """)

    st.write("""
    **Expected Output**:
    | count |
    |---------------|
    | 9             |
    """)


    st.write("")
    st.write("\n" * 2)  # Adds two blank lines for extra space
    st.write("\n" * 2)  # Adds two blank lines for extra space


    # Add a congratulatory message for completing the beginner objectives
    st.write("---")  # Add a divider for separation
    st.markdown("<h2 style='text-align: center;'>🎉 Congratulations on Completing the Beginner SQL Objectives!</h2>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'Now, test your skills in the <em>Now, test your skills in the Milky Way Beginner Challenge</em> or move to the next tab for <em>Intermediate Tips</em> to learn about SQL Joins!</h3>", unsafe_allow_html=True)



# Intermediate Joins Tab
with tabs[2]:
    st.title("Intermediate SQL Objectives:")

    st.write("""
    1. INNER JOIN
    2. LEFT JOIN
    3. RIGHT JOIN
    4. FULL OUTER JOIN
    5. ALIASING
    """)

    st.write("""
    These intermediate SQL concepts will help you manipulate and combine data more effectively. Let's go over each objective with examples, hints, and expected outputs.
    """)

    st.write('---')

    # INNER JOIN section
    st.header("1 - INNER JOIN")
    st.write("""
    The `INNER JOIN` selects records that have matching values in both tables. It's the most commonly used type of join.
    """)

    st.subheader("EXAMPLE : ")
    st.write("Retrieve planet names and their corresponding mission names using INNER JOIN")
    st.write("""
    ```sql
    SELECT planets.planet_name, missions.mission_name
    FROM planets
    INNER JOIN missions ON planets.planet_id = missions.planet_id;
    ```
    This query retrieves all planets and their respective missions by matching `planet_id`.
    """)

    st.write("""
    **Expected Output**:
    | planet_name | mission_name    |
    |-------------|-----------------|
    | Mars        | Mars Rover      |
    | Jupiter     | Jupiter Probe   |
    | Saturn      | Saturn Orbiter  |
    """)

    st.write("\n" * 5)

    st.write("---")

    # LEFT JOIN section
    st.header("2 - LEFT JOIN")
    st.write("""
    The `LEFT JOIN` returns all records from the left table (e.g., `PLANETS`), and the matched records from the right table (e.g., `MISSIONS`). If there’s no match, NULL values will be returned.
    """)

    st.subheader("EXAMPLE :") 
    st.write("Retrieve planet names and their corresponding mission names, but include planets with no missions.")
    st.write("""
    ```sql
    SELECT planets.planet_name, missions.mission_name
    FROM planets
    LEFT JOIN missions ON planets.planet_id = missions.planet_id;
    ```
    This query returns all planets, even those with no missions.
    """)

    st.write("""
    **Expected Output**:
    | planet_name | mission_name    |
    |-------------|-----------------|
    | Mars        | Mars Rover      |
    | Jupiter     | Jupiter Probe   |
    | Saturn      | NULL            |
    """)

    st.write("\n" * 5)

    st.write("---")

    # RIGHT JOIN section
    st.header("3 - RIGHT JOIN")
    st.write("""
    The `RIGHT JOIN` returns all records from the right table (e.g., `MISSIONS`), and the matched records from the left table (e.g., `PLANETS`). If there’s no match, NULL values will be returned.
    """)

    st.subheader("EXAMPLE :") 
    st.write("Retrieve mission names and their corresponding planet names, but include all missions even if they don’t have a corresponding planet.")
    st.write("""
    ```sql
    SELECT planets.planet_name, missions.mission_name
    FROM planets
    RIGHT JOIN missions ON planets.planet_id = missions.planet_id;
    ```
    This query returns all missions, even those without corresponding planets.
    """)

    st.write("""
    **Expected Output**:
    | planet_name | mission_name    |
    |-------------|-----------------|
    | Mars        | Mars Rover      |
    | NULL        | Unknown Mission |
    """)

    st.write("\n" * 5)

    st.write("---")

    # FULL OUTER JOIN section
    st.header("4 - FULL OUTER JOIN")
    st.write("""
    The `FULL OUTER JOIN` returns all records when there is a match in either the left or right table. If there is no match, NULL values will be returned for unmatched records.
    """)

    st.subheader("EXAMPLE :") 
    st.write("Retrieve all planet names and mission names, including planets without missions and missions without planets.")
    st.write("""
    ```sql
    SELECT planets.planet_name, missions.mission_name
    FROM planets
    FULL OUTER JOIN missions ON planets.planet_id = missions.planet_id;
    ```
    This query retrieves all planets and missions, including unmatched rows.
    """)

    st.write("""
    **Expected Output**:
    | planet_name | mission_name    |
    |-------------|-----------------|
    | Mars        | Mars Rover      |
    | Jupiter     | NULL            |
    | NULL        | Unknown Mission |
    """)

    st.write("\n" * 5)

    st.write("---")

    # Aliasing Section (last objective)
    st.header("5 - ALIASING")
    st.write("- **Aliasing**")
    st.write("""
    Aliasing allows you to assign temporary names to tables or columns in your SQL queries, making the code easier to read and write. You can create aliases using the `AS` keyword.
    """)

    st.subheader("EXAMPLE: Create an alias for a column and a table.")
    st.write("""
    ```sql
    SELECT p.planet_name AS name, m.mission_name AS mission
    FROM planets AS p
    INNER JOIN missions AS m ON p.planet_id = m.planet_id;
    ```
    This query creates aliases for both the table names (`planets` as `p`, `missions` as `m`) and the column names (`planet_name` as `name`, `mission_name` as `mission`).
    """)

    st.write("""
    **Expected Output**:
    | name     | mission          |
    |----------|------------------|
    | Mars     | Mars Rover       |
    | Jupiter  | Jupiter Probe    |
    | Saturn   | Saturn Orbiter   |
    """)

    st.write("\n" * 5)

    st.write("---")

    # Add a congratulatory message for completing the intermediate objectives
    st.write("---")  # Add a divider for separation
    st.markdown("<h2 style='text-align: center;'>🎉 Congratulations on Completing the Intermediate SQL Objectives!</h2>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Now that you've learned about SQL Joins and Aliasing, you can test your skills or move to the next section for more advanced concepts!</h3>", unsafe_allow_html=True)


# Advanced Subqueries Tab
with tabs[3]:
    st.title("Advanced SQL Objectives:")

    st.write("""
    1. ORDER BY
    2. GROUP BY / HAVING
    3. SUBQUERIES
    4. COMMON TABLE EXPRESSIONS (CTEs)
    """)

    st.write("""
    These advanced SQL concepts will help you manage, organize, and retrieve data more efficiently. Let's go over each objective with examples, hints, and expected outputs.
    """)

    st.write('---')

    # ORDER BY section
    st.header("1 - ORDER BY")
    st.write("""
    The `ORDER BY` clause is used to sort the result set in either ascending (`ASC`) or descending (`DESC`) order based on one or more columns.
    """)

    st.subheader("EXAMPLE :") 
    st.write("Retrieve planet names and sort them by distance from Earth in descending order")
    st.write("""
    ```sql
    SELECT planet_name, distance_from_earth
    FROM planets
    ORDER BY distance_from_earth DESC;
    ```
    This query retrieves the planet names and sorts them based on their distance from Earth in descending order.
    """)

    st.write("""
    **Expected Output**:
    | planet_name | distance_from_earth |
    |-------------|---------------------|
    | Pluto       | 5906                |
    | Neptune     | 4495                |
    | Uranus      | 2871                |
    """)

    st.write("\n" * 5)

    st.write("---")

    # GROUP BY / HAVING section
    st.header("2 - GROUP BY / HAVING")
    st.write("""
    The `GROUP BY` clause groups rows that have the same values in specified columns. It’s often used with aggregate functions (`COUNT`, `SUM`, `AVG`, etc.). The `HAVING` clause is used to filter groups based on a condition.
    """)

    st.subheader("EXAMPLE :") 
    st.write("Group missions by planet and count how many missions each planet has")
    st.write("""
    ```sql
    SELECT planet_id, COUNT(mission_id) AS total_missions
    FROM missions
    GROUP BY planet_id;
    ```
    This query counts the total number of missions for each planet.
    """)

    st.write("""
    **Expected Output**:
    | planet_id | total_missions |
    |-----------|----------------|
    | 1         | 2              |
    | 2         | 1              |
    | 3         | 1              |
    """)

    st.write("\n" * 5)

    st.subheader("EXAMPLE :") 
    st.write("Use HAVING to filter planets with more than 1 mission")
    st.write("""
    ```sql
    SELECT planet_id, COUNT(mission_id) AS total_missions
    FROM missions
    GROUP BY planet_id
    HAVING COUNT(mission_id) > 1;
    ```
    This query filters planets that have more than 1 mission.
    """)

    st.write("""
    **Expected Output**:
    | planet_id | total_missions |
    |-----------|----------------|
    | 1         | 2              |
    """)

    st.write("\n" * 5)

    st.write("---")

    # Subqueries section
    st.header("3 - SUBQUERIES")
    st.write("""
    A **subquery** is a query nested inside another query. Subqueries allow you to run multiple queries within a single SQL statement and can be used for filtering, calculating values, and more.
    """)

    st.subheader("EXAMPLE :") 
    st.write("Retrieve planets with more than one mission using a subquery")
    st.write("""
    ```sql
    SELECT planet_name
    FROM planets
    WHERE planet_id IN (
      SELECT planet_id
      FROM missions
      GROUP BY planet_id
      HAVING COUNT(mission_id) > 1
    );
    ```
    This subquery first identifies the `planet_id` of planets with more than one mission. The outer query retrieves the names of those planets.
    """)

    st.write("""
    **Expected Output**:
    | planet_name |
    |-------------|
    | Mars        |
    """)

    st.write("\n" * 5)

    st.write("---")

    # CTEs section
    st.header("4 - COMMON TABLE EXPRESSIONS (CTEs)")
    st.write("""
    A **Common Table Expression (CTE)** is a temporary result set defined within the execution scope of a `SELECT`, `INSERT`, `UPDATE`, or `DELETE` statement. CTEs make complex queries easier to manage and read.
    """)

    st.subheader("EXAMPLE :") 
    st.write("Use a CTE to find the total number of missions to each planet")
    st.write("""
    ```sql
    WITH mission_counts AS (
      SELECT planet_id, COUNT(mission_id) AS total_missions
      FROM missions
      GROUP BY planet_id
    )
    SELECT planets.planet_name, mission_counts.total_missions
    FROM planets
    INNER JOIN mission_counts ON planets.planet_id = mission_counts.planet_id;
    ```
    This query first calculates the total number of missions per planet in the CTE and then joins the results to retrieve the planet names.
    """)

    st.write("""
    **Expected Output**:
    | planet_name | total_missions |
    |-------------|----------------|
    | Mars        | 2              |
    """)

    st.write("\n" * 5)

    st.write("---")

    # Add a congratulatory message for completing the advanced objectives
    st.write("---")  # Add a divider for separation
    st.markdown("<h2 style='text-align: center;'>🎉 Congratulations on Completing the Advanced SQL Objectives!</h2>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>You have now mastered ORDER BY, GROUP BY/HAVING, Subqueries, and CTEs! Now, test your skills with more challenging problems or revisit previous sections for review.</h3>", unsafe_allow_html=True)


