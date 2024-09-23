import streamlit as st
import pandas as pd
import psycopg2
from urllib.parse import urlparse

# PostgreSQL Database connection function
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

# Function to save results to leaderboard
def save_to_leaderboard(user_name, completion_time, section):
    conn = create_connection()
    if conn:
        try:
            # Convert timedelta (completion_time) to a string in 'hh:mm:ss' format
            completion_time_str = str(completion_time)  # e.g., '00:10:05'
            
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO leaderboard (user_name, completion_time, section)
                VALUES (%s, %s, %s);
            """, (user_name, completion_time_str, section))
            conn.commit()
            cur.close()
            conn.close()
            st.success("Your result has been added to the leaderboard!")
        except Exception as e:
            st.error(f"Error saving to leaderboard: {e}")
    else:
        st.error("Failed to connect to the database.")

# Function to display leaderboard
def display_leaderboard(section):
    conn = create_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT user_name, completion_time, submission_date
                FROM leaderboard
                WHERE section = %s
                ORDER BY completion_time ASC;
            """, (section,))
            leaderboard_data = cur.fetchall()
            cur.close()
            conn.close()

            # Check if any data was returned
            if leaderboard_data:
                # Create a DataFrame to display results in table format
                leaderboard_df = pd.DataFrame(leaderboard_data, columns=['User Name', 'Completion Time', 'Submission Date'])
                st.table(leaderboard_df)  # Display the leaderboard table
            else:
                st.info("No leaderboard data available yet.")  # Show message if no data
        except Exception as e:
            st.error(f"Error retrieving leaderboard: {e}")
    else:
        st.error("Failed to connect to the database.")

# Main Leaderboard Page
st.title("Leaderboard 🌟")
st.subheader("All Results for Beginner Section")

# Display leaderboard for the 'Beginner' section
display_leaderboard('Beginner')

# Option to filter top 10 results
show_top_10 = st.checkbox("Show only top 10 results")

# Re-run the leaderboard display with the limit if top 10 is checked
if show_top_10:
    def display_leaderboard_top_10(section):
        conn = create_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("""
                    SELECT user_name, completion_time, submission_date
                    FROM leaderboard
                    WHERE section = %s
                    ORDER BY completion_time ASC
                    LIMIT 10;
                """, (section,))
                leaderboard_data = cur.fetchall()
                cur.close()
                conn.close()

                if leaderboard_data:
                    leaderboard_df = pd.DataFrame(leaderboard_data, columns=['User Name', 'Completion Time', 'Submission Date'])
                    st.table(leaderboard_df)
                else:
                    st.info("No leaderboard data available yet.")
            except Exception as e:
                st.error(f"Error retrieving leaderboard: {e}")
        else:
            st.error("Failed to connect to the database.")

    # Display the top 10 leaderboard results
    display_leaderboard_top_10('Beginner')
