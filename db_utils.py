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
