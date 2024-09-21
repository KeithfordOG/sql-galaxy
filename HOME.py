import streamlit as st
import pandas as pd
import sqlparse
import psycopg2
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
st.title("Welcome to SQL GALAXY")
st.subheader("One small query for developers, one giant JOIN for database kind")
st.image("images/rocket.png", caption="Welcome to SQL Galaxy!*Image Generated by ChatGPT4")

# Tabs for SQL overview and Tips and Tricks
tabs = st.tabs(["What is SQL?", "Easy SQL Tips", "Intermediate SQL Tips (Joins)", "Advanced SQL Tips (Subqueries)"])

# "What is SQL?" Tab
with tabs[0]:
    st.header("What is SQL?")
    st.write("""
    SQL (Structured Query Language) is the standard language used to interact with relational databases, which store data in tables consisting of rows and columns.

    ### How SQL Works:
    SQL follows a client-server model. A user sends a query (like `SELECT * FROM planets`) to the database server, which processes the query and returns the requested data. This interaction allows for seamless communication between applications and data storage systems.

    ### Popular SQL Databases:
    - **PostgreSQL**: Known for advanced querying capabilities and support for complex operations.
    - **MySQL**: Popular for web applications, especially with PHP.
    - **SQL Server**: A Microsoft product used in enterprise environments for high scalability and security.

    ### SQL's Core Role:
    SQL enables efficient data management, allowing users to store, retrieve, and manipulate large datasets. It powers the backend of modern applications, from e-commerce platforms to social media, and plays a vital role in decision-making and data analytics.

    ### Real-World Use Cases:
    - **E-commerce**: Manage inventory, customer data, and orders.
    - **Finance**: Track transactions and generate reports for analysis.
    - **Healthcare**: Store patient records and medical data.
    - **Business Intelligence**: Query and analyze big data for strategic decisions.

    ### A Brief History of SQL:
    SQL was developed in the 1970s by IBM and became the standard for database management. Today, it's supported by almost every major database system, including PostgreSQL, MySQL, and SQL Server.

    SQL has been the foundation of data-driven systems for decades, making it a crucial skill in the data management landscape.
    """)

    # Add the "Ready to Begin Your SQL Journey?" prompt only in this tab
    st.write("---")  # Add a divider for separation
    st.markdown("<h2 style='text-align: center;'>🚀 Ready to Begin Your SQL Journey?</h2>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Scroll up and select the <em>Easy SQL Tips</em> tab to get started!</h3>", unsafe_allow_html=True)


# Easy SQL Tips Tab
with tabs[1]:
    st.header("Easy SQL Tips: SELECT, FROM, WHERE, Comparison Operators, AND/OR & LIKE")

    st.write("""
    Learning these basic SQL commands will help you retrieve and filter data from your database. Let's go over each concept with examples, hints, and expected outputs.
    """)         

    st.write('---')

    st.write("""
     ### THE SELECT STATEMENT (SELECT)
    The `SELECT` statement tells the database which columns you want to retrieve. You can either specify individual columns or use an asterisk (`*`) to select all columns from the table.
    
    ### EXAMPLE 1: Retrieve all the columns from the PLANETS table
    ```sql
    SELECT * FROM planets;
    """)
    
    st.write("""This query will retrieve all columns from the `planets` table.
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

    st.write("""
    ### EXAMPLE 2: Retrieve all the planet names from the PLANETS table
    ```sql
    SELECT planet_name FROM planets;
    ```
    This query will rerieve all the planet names in the `planets` table.
             
    **Expected Output**:
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

    """)

    st.write("---")


# FROM Command section
    st.write("""
    ### THE FROM CLAUSE (FROM)
    The `FROM` clause specifies the table from which to retrieve data. After using `SELECT` to specify the columns, you use `FROM` to tell SQL where to look.

    ### EXAMPLE: Retrieve all the columns from the MISSIONS table
    ```sql
    SELECT * FROM missions;
    """)

    st.write("""
    **Expected Output**:
    | mission_id | planet_id | mission_name     | mission_date | crew_size |
    |------------|-----------|------------------|--------------|-----------|
    | 0          | 1         | Mars Rover Mission | 2004-01-04  | 6         |
    | 1          | 1         | Mars Pathfinder   | 1997-07-04  | 5         |
    | 2          | 3         | Jupiter Probe     | 1973-12-03  | 8         |
    | 3          | 4         | Saturn Orbiter    | 2004-07-01  | 3         |
    | 4          | 5         | Neptune Explorer  | 1989-08-25  | 7         |
    | 5          | 6         | Pluto Flyby       | 2015-07-14  | 3         |
    | 6          | 6         | Venus Research    | 1982-03-05  | 4         |
    | 7          | 8         | Voyager 2         | 1986-01-24  | 0         |
    | 8          | 9         | Mariner 10        | 1974-03-29  | 0         |
    | 9          | 10        | MESSENGER        

    """)

    st.write("---")

    # Comparison Operators section
    st.write("### COMPARISON OPERATORS")

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
    st.write("### THE WHERE CLAUSE (WHERE)")

    st.write("""
    The `WHERE` clause is used to filter records in SQL. It allows you to specify conditions that must be met for rows to be included in the result set.

    You can use the `WHERE` clause with comparison operators (e.g., `=`, `>`, `<`, etc.) to narrow down your results.
    """)

# Example using WHERE Clause
    st.write("### EXAMPLE: Retrieve all missions where the crew size is greater than 3")
    st.write("""
    ```sql
    SELECT * FROM missions WHERE crew_size > 3;
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










# Intermediate Joins Tab
with tabs[2]:
    st.header("Intermediate - Joins")
    st.write("""
    SQL joins allow you to combine data from two or more tables based on related columns. There are several types of joins:

    - **INNER JOIN**: Select records that have matching values in both tables.
    - **LEFT JOIN**: Select all records from the left table, and the matched records from the right table. NULL for unmatched.
    - **RIGHT JOIN**: Select all records from the right table, and the matched records from the left table. NULL for unmatched.
    - **FULL OUTER JOIN**: Select all records where there is a match in either left or right table.
    
    Example:
    ```sql
    SELECT p.planet_name, m.moon_name 
    FROM planets p 
    INNER JOIN moons m 
    ON p.planet_id = m.planet_id;
    ```

    Advanced tips:
    - **Self Joins**: Join a table with itself to compare rows within the same table.
      ```sql
      SELECT a.planet_name, b.planet_name 
      FROM planets a 
      JOIN planets b 
      ON a.distance_from_earth > b.distance_from_earth;
      ```
    - **Optimizing Joins**: Ensure the columns used in joins are indexed to improve performance in large datasets.
    """)

# Advanced Subqueries Tab
with tabs[3]:
    st.header("Advanced - Subqueries")
    st.write("""
    A subquery is a query nested inside another query. These are useful for more complex logic or data filtering.

    - **Scalar Subquery**: Returns a single value.
    - **IN Subquery**: Used to filter results based on a set of values.
    - **EXISTS Subquery**: Used to test for the existence of rows.

    You can also use **CTEs (Common Table Expressions)** to break down complex queries into simpler steps.
    
    Example:
    ```sql
    WITH moon_counts AS (
      SELECT planet_id, COUNT(moon_id) AS num_moons 
      FROM moons 
      GROUP BY planet_id
    )
    SELECT planet_name, num_moons 
    FROM planets 
    INNER JOIN moon_counts 
    ON planets.planet_id = moon_counts.planet_id;
    ```

    Recursive subqueries are also used to process hierarchical data like organizational charts or tree structures.
    """)

