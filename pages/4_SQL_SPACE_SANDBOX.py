import streamlit as st
import pandas as pd
import sqlparse
import psycopg2

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


# Function to execute SQL query and return result as DataFrame
def execute_sql_query(query):
    conn = create_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(query)
            columns = [desc[0] for desc in cur.description]  # Get column names
            result = cur.fetchall()  # Fetch all rows
            cur.close()
            conn.close()
            return pd.DataFrame(result, columns=columns)  # Return result as DataFrame
        except Exception as e:
            st.error(f"Error running query: {e}")
            return None
    else:
        return None

# Title and Introduction
st.title("SQL Sandbox 🌌")

# Image Header for Sandbox Mode
st.image("images/space_sandbox.png", "*SQL Sandbox - Practice your queries*", use_column_width=True)


st.write("""
    Welcome to the SQL Sandbox! Here, you can practice writing your own SQL queries on the `planets`, `missions`, and `moons` tables.
    
    Experiment with queries to retrieve, filter, and manipulate data across the tables in our galactic dataset. 
    There's no wrong answer—just learning and exploring!
    
    Example queries to get you started:
    - `SELECT * FROM planets;`
    - `SELECT mission_name, crew_size FROM missions WHERE crew_size > 3;`
    - `SELECT moon_name FROM moons WHERE planet_id = 2;`
""")

# Input section for user SQL query
user_query = st.text_area("Enter your SQL query below:", value="SELECT * FROM planets LIMIT 5;", height=150)

# Execute button
if st.button("Execute Query"):
    # Normalize user's SQL query
    normalized_user_query = sqlparse.format(user_query, reindent=True, keyword_case='upper').strip()
    
    # Display the normalized query for clarity
    st.write(f"Your query: \n```sql\n{normalized_user_query}\n```")
    
    # Execute the user's query
    query_result = execute_sql_query(normalized_user_query)  # Execute the query
    
    # If there are results, display them in a table
    if query_result is not None and not query_result.empty:
        st.write(query_result)  # This displays the DataFrame as a nicely formatted table
    else:
        st.write("Query executed but returned no results.")

# Display the tables from the database

st.title('Data from the Tables')

# Planets Table
st.subheader('🌍 Planets Table')
st.write("This table contains detailed information about planets, including their distance from the sun, discoverers, and unique IDs.")
planets_query = "SELECT * FROM planets;"  # Query the planets table from PostgreSQL
planets_df = execute_sql_query(planets_query)
if planets_df is not None:
    st.write(planets_df)
else:
    st.write("No data available or error fetching planets table.")

# Missions Table
st.subheader('🚀 Missions Table')
st.write("This table contains the details of various space missions, including their destination planets and crew sizes.")
missions_query = "SELECT * FROM missions;"  # Query the missions table from PostgreSQL
missions_df = execute_sql_query(missions_query)
if missions_df is not None:
    st.write(missions_df)
else:
    st.write("No data available or error fetching missions table.")

# Moons Table
st.subheader('🌕 Moons Table')
st.write("This table tracks all the moons, their diameters, discoverers, and the planets they orbit.")
moons_query = "SELECT * FROM moons;"  # Query the moons table from PostgreSQL
moons_df = execute_sql_query(moons_query)
if moons_df is not None:
    st.write(moons_df)
else:
    st.write("No data available or error fetching moons table.")

# Schema Information for reference
st.subheader("Schema Information")

# Planets Table Schema
st.subheader('🌍 Planets Table Schema')
st.write("""
- `planet_id`: INT  
- `planet_name`: VARCHAR  
- `distance_from_earth`: INT  
- `discoverer`: VARCHAR  
- `discovery_year`: INT  
- `moons`: INT  
- `has_rings`: BOOLEAN
""")

# Missions Table Schema
st.subheader('🚀 Missions Table Schema')
st.write("""
- `mission_id`: INT  
- `planet_id`: INT (references `planets.planet_id`)  
- `mission_name`: VARCHAR  
- `mission_date`: DATE  
- `crew_size`: INT
""")

# Moons Table Schema
st.subheader('🌕 Moons Table Schema')
st.write("""
- `moon_id`: INT  
- `moon_name`: VARCHAR  
- `planet_id`: INT (references `planets.planet_id`)  
- `diameter_km`: DECIMAL  
- `discovered_by`: VARCHAR  
- `discovery_year`: INT
""")

# Footer message
st.write("Have fun practicing SQL and exploring the galaxy of data!")
