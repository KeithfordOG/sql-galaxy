import streamlit as st
import psycopg2
import pandas as pd
from urllib.parse import urlparse

# PostgreSQL Database connection using Streamlit secrets
def create_connection():
    try:
        # Get the DATABASE_URL from Streamlit secrets
        database_url = st.secrets["postgresql"]["DATABASE_URL"]
        
        # Parse the DATABASE_URL
        url = urlparse(database_url)
        
        # Extract components from the URL
        conn = psycopg2.connect(
            host=url.hostname,
            database=url.path[1:],  # Remove the leading '/'
            user=url.username,
            password=url.password,
            port=url.port
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
            print(f"Error executing query: {e}")
            return pd.DataFrame()  # Return empty DataFrame if error
    else:
        return pd.DataFrame()
