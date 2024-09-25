import streamlit as st
import sqlparse
import pandas as pd
import psycopg2 
from streamlit_ace import st_ace
import re
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



# Initialize session state to track correctness, stages, and progress
if 'answer_correct_journey' not in st.session_state:
    st.session_state.answer_correct_journey = [False] * 5
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'current_stage' not in st.session_state:
    st.session_state.current_stage = 0  # Start at Stage 0
if 'stages_completed' not in st.session_state:
    st.session_state.stages_completed = 0  # Track the stages completed

# Function to normalize and format SQL query
def normalize_sql(query):
    return sqlparse.format(query, reindent=True, keyword_case='upper').strip()

# Function to sanitize SQL input
def sanitize_sql_input(sql_input):
    # Remove SQL comments
    sql_input = re.sub(r'--.*', '', sql_input)
    sql_input = re.sub(r'/\*.*?\*/', '', sql_input, flags=re.DOTALL)
    # Strip leading/trailing whitespace
    return sql_input.strip()

def update_progress(stages_completed):
    # Ensure the progress is capped at 100%
    progress_value = min(stages_completed / 5, 1.0)  # This ensures the progress does not exceed 1.0
    st.progress(progress_value)  # Update the progress bar


# Define stages, questions, answers, hints, and explanations
journey_stages = [
    "Mapping the Solar System ",
    "Assessing Past Missions",
    "Uncovering Ancient Knowledge",
    "Navigating Modern Missions",
    "Searching the T-Moons"
]
# Define storylines and questions in a list format
journey_questions = [
    "Your rocket ship's navigation system is down. To proceed, you must map the planets in the solar system by retrieving all records from the planets table.\n\n*Retrieve all records from the planets table.*",
    
    "Before continuing your journey, you need to understand the scope of previous space expeditions. Count the number of missions in the missions table to gain insights.\n\n*How would you count the number of missions in the missions table?*",
    
    "Ancient civilizations hold the key to your next fuel boost. Discover who first identified Venus to unlock the next stage of your journey.\n\n*What is the SQL query to find the discoverer of the planet Venus?*",
    
    "Modern space missions contain vital data for your next fuel boost. Retrieve all missions launched after 1999 to move forward.\n\n*Write a SQL query to retrieve all missions after the year 1999.*",
    
    "To unlock the final fuel reserves, you must locate all moons that begin with the letter 'T'. This is your last challenge before you can return home.\n\n*Write a SQL query to return all the moon names that start with the letter 'T'.*"
]



correct_answers = [
    ["select * from planets", "select planet_id, planet_name, distance_from_sun, discoverer from planets"],
    ["select count(*) from missions", "SELECT COUNT (*) FROM missions"],
    ["select discoverer from planets where planet_name = 'venus'", "select discoverer from planets where planet_id = 6"],
    ["select * from missions where mission_date > '1999-12-31'", "select * from missions where extract(year from mission_date) > 1999"],
    ["select moon_name from moons where moon_name like 't%'", "select moon_name from moons where moon_name ilike 't%'"]
]

journey_hints = [
    ["Start with `SELECT` `*` `FROM`...", "The table you need is `planets`."],
    ["Use `COUNT` `(*)` to count rows.", "The table you need is `missions`."],
    ["`SELECT` only the `discoverer` column","Filter the `planets` table `WHERE` `planet_name` `=` `'Venus'`."],
    ["Filter `mission_date` `>` `1999-12-31`.", "Use the `WHERE` clause with `mission_date` `>` `'1999-12-31'`."],
    ["Use `LIKE` `'T%'` to find names starting with `'T'`.", "The table you need is `moons` and the column is `moon_name`."]
]

# Custom CSS for styling
st.markdown(
    """
    <style>
    .title {
        font-size: 24px;
        color: #2E86C1;
    }
    </style>
    """,
    unsafe_allow_html=True
)


def render_stage(i):
    st.markdown(f"<div class='title'>Stage {i+1}: {journey_stages[i]} 🌌</div>", unsafe_allow_html=True)
    st.write(journey_questions[i])

    # Input with SQL code editor
    user_answer = st_ace(
        placeholder=f"Write your SQL query for Stage {i+1} here...",
        language="sql",
        theme="cobalt",
        key=f"ace_editor_{i}",
        auto_update=True
    )

    # Initialize session state to store query results
    if f'query_result_{i}' not in st.session_state:
        st.session_state[f'query_result_{i}'] = None

    # Hints
    with st.expander("Need a hint?"):
        if st.button("Show Hint 1", key=f"hint1_{i}"):
            st.write(journey_hints[i][0])
        if st.button("Show Hint 2", key=f"hint2_{i}"):
            st.write(journey_hints[i][1])

    # Button to submit answer
    if st.button(f"Submit Answer for Stage {i+1}", key=f"submit_journey_{i}"):
        # Sanitize and normalize user input
        user_answer_sanitized = sanitize_sql_input(user_answer)
        normalized_user_answer = normalize_sql(user_answer_sanitized).lower().strip(';')
        normalized_correct_answers = [
            normalize_sql(sanitize_sql_input(answer)).lower().strip(';')
            for answer in correct_answers[i]
        ]

        if normalized_user_answer == '':
            st.write("Please enter your SQL query.")
        else:
            # Display the query results regardless of correctness
            try:
                query_result = execute_sql_query(user_answer)
                if query_result is not None and not query_result.empty:
                    st.session_state[f'query_result_{i}'] = query_result  # Store user query results in session state
                else:
                    st.session_state[f'query_result_{i}'] = pd.DataFrame({"Result": ["No results returned"]})
            except Exception as e:
                st.error(f"Error executing query: {e}")
                st.session_state[f'query_result_{i}'] = pd.DataFrame({"Error": [str(e)]})

            # Check correctness and provide feedback
            if normalized_user_answer in normalized_correct_answers:
                if not st.session_state.answer_correct_journey[i]:
                    st.session_state.answer_correct_journey[i] = True
                    st.session_state.stages_completed += 1

                # Congratulate the user
                st.success(f"Good job, {st.session_state.user_name}! You've completed Stage {i+1}.")

                # Automatic transition for stages (handled similarly to Stage 5)
                if i < 4:
                    time.sleep(3)
                    st.session_state.current_stage = i + 1
                    st.experimental_rerun()
                else:
                    st.balloons()
                    st.write(f"Well Done, {st.session_state.user_name}! 🎉 You've completed the Hero's Journey!")
                    # Update progress to 100% on the final stage
                    st.progress(1.0)
            else:
                st.error("Incorrect answer. Try again.")

    # Display "Your Query Results" (User's query output)
    if st.session_state[f'query_result_{i}'] is not None:
        st.markdown("### Your Query Results:")
        st.dataframe(st.session_state[f'query_result_{i}'])

    # Display the expected output for this stage
    expected_output = get_expected_output(i)
    st.markdown("### Expected Output:")
    st.dataframe(expected_output)

    # **Ensure the reference tables are always displayed at the bottom**
    display_reference_tables()

import pandas as pd

def get_expected_output(stage):
    if stage == 0:
        # Expected output for Stage 1: Retrieve all records from the planets table
        return pd.DataFrame({
            "planet_id": [1, 2, 3, 4, 5, 6, 7, 8, 9],
            "planet_name": ["Venus", "Mars", "Jupiter", "Saturn", "Neptune", "Pluto", "Uranus", "Mercury", "Earth"],
            "distance_from_earth": [108, 225, 778, 1_433, 4_495, 5_906, 2_871, 77, 0],
            "discoverer": ["Babylonians", "Galileo", "Galileo", "Huygens", "Le Verrier", "Tombaugh", "William Herschel", "Known since antiquity", "Known since antiquity"],
            "discovery_year": [-500, 1610, 1610, 1655, 1846, 1930, 1781, None, None]
        })

    elif stage == 1:
        # Expected output for Stage 2: Count the number of missions in the missions table
        return pd.DataFrame({
            "count": [11]
        })

    elif stage == 2:
        # Expected output for Stage 3: Discover who first identified Venus
        return pd.DataFrame({
            "discoverer": ["Babylonians"]
        })

    elif stage == 3:
        # Expected output for Stage 4: Retrieve all missions launched after 1999
        return pd.DataFrame({
            "mission_id": [1, 4, 6, 10, 11],
            "planet_id": [1, 3, 5, 8, 8, ],
            "mission_name": ["Mars Rover Mission", "Saturn Orbiter", "Pluto Flyby", "MESSENGER", "BepiColombo"],
            "mission_date": ["2004-01-04","2004-07-01", "2015-07-14", "2004-08-03", "2018-10-20"],
            "crew_size": [6, 3, 3, 0, 0]
        })

    elif stage == 4:
        # Expected output for Stage 5: Return all the moons that start with the letter 'T'
        return pd.DataFrame({
            "moon_name": ["Triton", "Titan"]
        })



    else:
        # Default case if the stage is out of range
        return pd.DataFrame({
            "Result": ["No expected output available"]
        })





# Function to display reference tables using markdown
def display_reference_tables():
    st.markdown("## Reference Tables 📄")
    st.write("Below are the tables you can use in your queries:")

    # Static markdown table for the planets table
    st.markdown("""
    ### `planets` 
    | planet_id | planet_name  | distance_from_earth| discoverer       | discovery_year |
    |-----------|--------------|---------------------|------------------|----------------|
    | 1         | Venus        | 108                 | Babylonians      | -500           |
    | 2         | Mars         | 225                 | Galileo          | 1610           |
    | 3         | Jupiter      | 778                 | Galileo          | 1610           |
    | 4         | Saturn       | 1,433               | Huygens          | 1655           |
    | 5         | Neptune      | 4,495               | Le Verrier       | 1846           |
    | 6         | Pluto        | 5,906               | Tombaugh         | 1930           |
    | 7         | Uranus       | 2,871               | William Herschel | 1781           |
    | 8         | Mercury      | 77                  | Known since antiquity | None      |
    | 9         | Earth        | 0                   | Known since antiquity | None      |
    """)

    # Static markdown table for the missions table
    st.markdown("""
    ### `missions` 
    | mission_id | planet_id | mission_name     | mission_date | crew_size |
    |------------|-----------|------------------|--------------|-----------|
    | 1          | 1         | Mars Rover Mission| 2004-01-04   | 6         |
    | 2          | 1         | Mars Pathfinder   | 1997-07-04   | 5         |
    | 3          | 2         | Jupiter Probe     | 1973-12-03   | 8         |
    | 4          | 3         | Saturn Orbiter    | 2004-07-01   | 3         |
    | 5          | 4         | Neptune Explorer  | 1989-08-25   | 7         |
    | 6          | 5         | Pluto Flyby       | 2015-07-14   | 3         |
    | 7          | 6         | Venus Research    | 1982-03-05   | 4         |
    | 8          | 7         | Voyager 2         | 1986-01-24   | 0         |
    | 9          | 8         | Mariner 10        | 1974-03-29   | 0         |
    | 10         | 8         | MESSENGER         | 2004-08-03   | 0         |
    | 11         | 8         | BepiColombo       | 2018-10-20   | 0         |
    """)

    # Static markdown table for the moons table
    st.markdown("""
    ### `moons` 
    | moon_id | moon_name  | planet_id | diameter_km | discovered_by        | discovery_year |
    |---------|------------|-----------|-------------|----------------------|----------------|
    | 1       | Phobos     | 4         | 22.20       | Asaph Hall           | 1877           |
    | 2       | Deimos     | 4         | 12.40       | Asaph Hall           | 1877           |
    | 3       | Io         | 5         | 3643.20     | Galileo              | 1610           |
    | 4       | Europa     | 5         | 3121.60     | Galileo              | 1610           |
    | 5       | Ganymede   | 5         | 5262.40     | Galileo              | 1610           |
    | 6       | Callisto   | 5         | 4820.60     | Galileo              | 1610           |
    | 7       | Titan      | 6         | 5150.00     | Christiaan Huygens   | 1655           |
    | 8       | Enceladus  | 6         | 504.00      | William Herschel     | 1789           |
    | 9       | Triton     | 8         | 2706.80     | William Lassell      | 1846           |
    | 10      | Charon     | 9         | 1212.00     | James Christy        | 1978           |
    """)



def main():
    # Title and Introduction
    st.title('BEGINNER 🚀')

    # Milky Way Image at the top
    st.image("images/milkyway.png", use_column_width=True)

    # Brief description/intro explaining the five stages and rules
    st.markdown("""
    ### Milky Way Galaxy!
    Welcome to the Milky Way, the starting point of your galactic journey. You’ve ventured deep into the heart of our home galaxy, where the first steps in mastering SQL await. In this beginner section, you’ll encounter the foundations of data exploration, learning to navigate the stars through essential queries.


    **Stages**:
    1. **Mapping the Solar System**: Retrieve all the planets in the planets table.
    2. **Assessing Past Missions**: Count all the missions in the missions table.
    3. **Uncovering Ancient Knowledge**: Discover who first identified Venus.
    4. **Navigating Modern Missions**: Find missions launched after 1999.
    5. **Searching the T-Moons**: Locate all moons that start with the letter 'T'.
    
    **Rules**:
    - Enter your name below and press 'Enter' to begin
    - Complete each stage in sequence to unlock the next.
    - Hints are available if you're stuck.
    - Submit your SQL query to check your progress, and compare your results with the correct output when successful.
    
    Let's get started, and may your SQL skills fuel your journey back home!
    """)

    # Initialize and update the progress bar
    update_progress(st.session_state.stages_completed)  # Ensure this runs at the beginning of the main function

    # Input for user's name
    st.session_state.user_name = st.text_input("Enter your astronaut's name:")

    if st.session_state.user_name:
        # Ensure stages are accessed sequentially
        current_stage = st.session_state.current_stage

        # Create tabs for stages
        stages = [f"Stage {i+1}" for i in range(5)]
        tabs = st.tabs(stages)

        for i in range(5):
            with tabs[i]:
                if i <= current_stage:
                    render_stage(i)
                else:
                    st.write("You need to complete the previous stages to access this stage.")


if __name__ == "__main__":
    main()
