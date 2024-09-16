import streamlit as st
import psycopg2
import pandas as pd

# PostgreSQL Database connection using Streamlit secrets
def create_connection():
    try:
        conn = psycopg2.connect(
            host=st.secrets["postgresql"]["DB_HOST"],  # Get the host from Streamlit secrets
            database=st.secrets["postgresql"]["DB_NAME"],  # Get the database name from Streamlit secrets
            user=st.secrets["postgresql"]["DB_USER"],  # Get the user from Streamlit secrets
            password=st.secrets["postgresql"]["DB_PASSWORD"],  # Get the password from Streamlit secrets
            port=st.secrets["postgresql"].get("DB_PORT", "5432")  # Default port is 5432 if not set
        )
        return conn
    except Exception as e:
        st.error(f"Error connecting to the database: {e}")
        return None

# Execute SQL query and return results
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
            return result, columns
        except Exception as e:
            st.error(f"Error executing query: {e}")
            return None, None
    else:
        return None, None

# Welcome section for SQL Galaxy
st.title("Welcome to SQL GALAXY")
st.subheader("One small query for developers, one giant JOIN for database kind")
st.write("""
    In this game, you will be tested on your SQL knowledge across various difficulty levels. 
    Choose a tab to begin your journey and solve SQL challenges in space!
""")
st.image("images/rocket.png", caption="Ready to launch your SQL skills into space! *Image Generated by ChatGPT4")

# Tabs for SQL overview and Tips and Tricks
tabs = st.tabs(["What is SQL?", "Easy SQL Tips", "Intermediate - Joins", "Advanced - Subqueries"])

# "What is SQL?" Tab
with tabs[0]:
    st.header("What is SQL?")
    st.write("""
    SQL (Structured Query Language) is a standard programming language designed for managing and manipulating relational databases. 
    It allows users to interact with databases through tasks like retrieving data, updating records, inserting new data, and deleting records.

    SQL is essential for interacting with databases and serves as the backbone for modern data storage systems, including e-commerce platforms, data warehouses, and cloud databases.
    
    Key tasks you can perform with SQL include:
    - **Querying data** from a database using `SELECT`
    - **Inserting records** using `INSERT`
    - **Updating existing records** using `UPDATE`
    - **Deleting records** from a table using `DELETE`
    
    Example:
    ```sql
    SELECT * FROM planets;
    ```
    
    SQL has several dialects such as:
    - **PostgreSQL**: Used for advanced SQL queries and large-scale database systems.
    - **MySQL**: Widely used in web applications and open-source projects.
    - **SQLite**: A lightweight database often used for mobile apps.
    """)
    
# Easy Tips Tab
with tabs[1]:
    st.header("Easy SQL Tips")
    st.write("""
    These basic commands will help you get started with SQL:

    - **SELECT**: Retrieve data from a table.
    - **WHERE**: Filter records based on specific conditions.
    - **ORDER BY**: Sort the result set by one or more columns.
    - **GROUP BY**: Group rows that have the same values into summary rows.
    - **COUNT**: Returns the number of rows that match a criterion.
    - **SUM**: Add up numeric values in a column.
    - **MIN/MAX**: Get the minimum or maximum value from a column.
    
    Example: 
    ```sql
    SELECT * FROM planets WHERE distance_from_sun > 100;
    ```
    
    You can also use **joins** to combine data from multiple tables:
    ```sql
    SELECT planet_name, moon_name FROM planets
    INNER JOIN moons ON planets.planet_id = moons.planet_id;
    ```
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

# Section to direct users to try solving problems
st.subheader("Time to Test Your SQL Knowledge!")
st.write("""
    Now that you've reviewed the SQL tips and tricks, it's time to test your knowledge by solving real-world problems.
    
    Use the **side navigation** to select one of the difficulty levels:
    
    - **Milky Way** (Easy)
    - **Hydra Cluster** (Intermediate)
    - **Hercules Supercluster** (Advanced)
    
    Each difficulty tier contains multiple SQL challenges to help you practice your skills. Good luck, and may your queries always return the right results!
""")

# Optional: Example of using the PostgreSQL connection to query data
st.write("Sample Query from PostgreSQL Database:")

# Example query - adjust as needed to match your actual table names and structure
sample_query = "SELECT * FROM planets LIMIT 5;"
result, columns = execute_sql_query(sample_query)

if result and columns:
    # Display the query result in a table format
    st.write(f"Query: {sample_query}")
    st.write(pd.DataFrame(result, columns=columns))
else:
    st.write("No data to display or error with the query.")