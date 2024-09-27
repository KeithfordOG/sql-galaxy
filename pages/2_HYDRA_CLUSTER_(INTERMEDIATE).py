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

# Define stages, questions, answers, hints, and explanations for Intermediate
journey_stages = [
    "Unveiling the Major Expeditions",
    "Largest Moons and Missions",
    "Mars Missions and Their Moons",
    "Planets with Null Discovery Year",
    "Galileo Discoveries and Their Missions"
]

journey_questions = [
    "The Hydra Cluster's archives hold records of many space missions, some with crews larger than three. To unlock your next fuel boost, you need to retrieve the details of these missions. Your goal is to identify the largest crews in order to proceed.\n\n*Retrieve the planet name, mission name, and crew size for missions that had a crew size larger than three, ordered by crew size from largest to smallest.*",
    
    "The largest moon in the database holds clues to your next destination. To proceed, you need to find this moon and the mission associated with its planet.\n\n*Find the largest moon and the mission to its planet.*",
    
    "Mars is a hub of activity with multiple missions and moons. To navigate this stage, you need to retrieve missions to Mars along with their crew sizes and the names of Mars's moons.\n\n*Retrieve missions to Mars and their crew sizes and moons.*",
    
    "Some planets have mysterious origins with unknown discovery years. To uncover these mysteries, retrieve the mission name, discovery year, and mission date for planets with a NULL discovery year.\n\n*Return the mission name, discovery year, and mission date for planets with a NULL discovery year.*",
    
    "Galileo's discoveries are key to unlocking this stage. You need to find all missions to planets discovered by Galileo and their mission dates.\n\n*Retrieve the mission_name and mission_date for planets discovered by Galileo.*"
]

correct_answers = [
    [
        "SELECT planet_name, mission_name, crew_size FROM missions INNER JOIN planets ON missions.planet_id = planets.planet_id WHERE crew_size > 3 ORDER BY crew_size DESC;",
        "SELECT p.planet_name, m.mission_name, m.crew_size FROM missions m INNER JOIN planets p ON m.planet_id = p.planet_id WHERE m.crew_size > 3 ORDER BY m.crew_size DESC;"
    ],
    [
        "SELECT moon_name, mission_name FROM moons INNER JOIN missions ON moons.planet_id = missions.planet_id ORDER BY diameter_km DESC LIMIT 1;",
        "SELECT m.moon_name, mi.mission_name FROM moons m INNER JOIN missions mi ON m.planet_id = mi.planet_id ORDER BY m.diameter_km DESC LIMIT 1;"
    ],
    [
        "SELECT mission_name, moon_name, crew_size FROM missions INNER JOIN planets ON missions.planet_id = planets.planet_id INNER JOIN moons ON moons.planet_id = planets.planet_id WHERE planet_name = 'Mars';",
        "SELECT mi.mission_name, mo.moon_name, mi.crew_size FROM missions mi INNER JOIN planets p ON mi.planet_id = p.planet_id INNER JOIN moons mo ON mo.planet_id = p.planet_id WHERE p.planet_name = 'Mars';"
    ],
    [
        "SELECT mission_name, discovery_year, mission_date FROM missions INNER JOIN planets ON missions.planet_id = planets.planet_id WHERE discovery_year IS NULL;",
        "SELECT mi.mission_name, p.discovery_year, mi.mission_date FROM missions mi INNER JOIN planets p ON mi.planet_id = p.planet_id WHERE p.discovery_year IS NULL;"
    ],
    [
        "SELECT mission_name, mission_date FROM missions INNER JOIN planets ON missions.planet_id = planets.planet_id WHERE discoverer = 'Galileo';",
        "SELECT mi.mission_name, mi.mission_date FROM missions mi INNER JOIN planets p ON mi.planet_id = p.planet_id WHERE p.discoverer = 'Galileo';"
    ]
]

journey_hints = [
    ["Use INNER JOIN to combine the missions and planets tables.", "Filter by crew_size > 3 and order by crew_size DESC."],
    ["Use ORDER BY diameter_km DESC.", "Use LIMIT 1 to find the largest moon and its mission."],
    ["Use INNER JOIN on missions, planets, and moons.", "Filter where planet_name = 'Mars'."],
    ["Use WHERE discovery_year IS NULL.", "Join missions and planets to get mission_name, discovery_year, and mission_date."],
    ["Filter by discoverer = 'Galileo'.", "Join missions and planets to retrieve mission_name and mission_date."]
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

    # Display query results if available
    if st.session_state[f'query_result_{i}'] is not None:
        st.write("**Query Results:**")
        st.dataframe(st.session_state[f'query_result_{i}'])

    # Hints
    with st.expander("Need a hint?"):
        if st.button("Show Hint 1", key=f"hint1_{i}"):
            st.write(journey_hints[i][0])
        if st.button("Show Hint 2", key=f"hint2_{i}"):
            st.write(journey_hints[i][1])

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
                    st.session_state[f'query_result_{i}'] = query_result  # Store results in session state
                    st.write("**Query Results:**")
                    st.dataframe(query_result)
                else:
                    st.write("No results returned.")
            except Exception as e:
                st.error(f"Error executing query: {e}")

            # Check correctness and provide feedback
            if normalized_user_answer in normalized_correct_answers:
                if not st.session_state.answer_correct_journey[i]:
                    st.session_state.answer_correct_journey[i] = True
                    st.session_state.stages_completed += 1

                # Congratulate the user
                st.success(f"Great job, {st.session_state.user_name}! You've completed Stage {i+1}.")

                # Update progress bar
                update_progress(st.session_state.stages_completed)

                # Automatic transition after a delay
                time.sleep(3)

                if i < 4:
                    st.session_state.current_stage = i + 1
                    st.experimental_rerun()
                else:
                    st.balloons()
                    st.write(f"Well Done, {st.session_state.user_name}! 🎉 You've completed the Hero's Journey!")
                    st.write("Explore the **Hercules Supercluster** section for more challenges.")
            else:
                st.error("Incorrect answer. Try again.")

    # Display reference tables at the bottom of each stage
    display_reference_tables()

# Function to display reference tables using markdown
def display_reference_tables():
    st.markdown("## Reference Tables 📄")
    st.write("Below are the tables you can use in your queries:")

    # Static markdown table for the planets table
    st.markdown("""
    ### `planets` 
    | planet_id | planet_name  | distance_from_sun | discoverer               | discovery_year |
    |-----------|--------------|-------------------|--------------------------|----------------|
    | 1         | Mercury      | 57.9              | Known since antiquity    | NULL           |
    | 2         | Venus        | 108.2             | Known since antiquity    | NULL           |
    | 3         | Earth        | 149.6             | N/A                      | NULL           |
    | 4         | Mars         | 227.9             | Galileo                  | 1610           |
    | 5         | Jupiter      | 778.3             | Galileo                  | 1610           |
    | 6         | Saturn       | 1,429.4           | Galileo                  | 1610           |
    | 7         | Uranus       | 2,871             | William Herschel         | 1781           |
    | 8         | Neptune      | 4,495             | Adams                    | 1846           |
    | 9         | Pluto        | 5,906             | Tombaugh                 | 1930           |
    """)

    # Static markdown table for the missions table
    st.markdown("""
   ### `missions` 
    | mission_id | mission_name    | mission_date | planet_id | crew_size |
    |------------|-----------------|--------------|-----------|-----------|
    | 1          | Apollo 11       | 1969-07-20   | 3         | 3         |
    | 2          | Mars Pathfinder | 1996-12-04   | 4         | 0         |
    | 3          | Jupiter Probe   | 1989-10-18   | 5         | 0         |
    | 4          | Saturn Orbiter  | 2004-06-30   | 6         | 0         |
    | 5          | Mars Explorer   | 2001-04-07   | 4         | 0         |
    | 6          | Cassini-Huygens | 1997-10-15   | 6         | 0         |
    | 7          | New Horizons    | 2006-01-19   | 9         | 0         |
    | 8          | Voyager 1       | 1977-09-05   | NULL      | 0         |
    | 9          | Voyager 2       | 1977-08-20   | NULL      | 0         |
    | 10         | MESSENGER       | 2004-08-03   | 1         | 0         |
    | 11         | Big Crew Mission| 2010-05-05   | 5         | 5         |
    | 12         | Larger Crew Mission| 2015-09-09| 6         | 6         |
    """)

    # Static markdown table for the moons table
    st.markdown("""
 ### `moons` 
| moon_id | moon_name  | planet_id | diameter_km | discoverer               | discovery_year |
|---------|------------|-----------|-------------|--------------------------|----------------|
| 1       | Io         | 5         | 3643.2      | Galileo                  | 1610           |
| 2       | Europa     | 5         | 3121.6      | Galileo                  | 1610           |
| 3       | Ganymede   | 5         | 5262.4      | Galileo                  | 1610           |
| 4       | Callisto   | 5         | 4820.6      | Galileo                  | 1610           |
| 5       | Titan      | 6         | 5149.5      | Christiaan Huygens       | 1655           |
| 6       | Enceladus  | 6         | 504.2       | William Herschel         | 1789           |
| 7       | Phobos     | 4         | 22.2        | Asaph Hall               | 1877           |
| 8       | Deimos     | 4         | 12.6        | Asaph Hall               | 1877           |
| 9       | Charon     | 9         | 1212        | James Christy            | 1978           |
    """)

def main():
    # Title and Introduction
    st.title('INTERMEDIATE 🚀')

    # Hydra Cluster Image at the top
    st.image("images/hydra_cluster.png", use_column_width=True)

    # Brief description/intro explaining the five stages and rules
    st.markdown("""
    ### Hydra Cluster Galaxy!
    You've navigated through the Milky Way and now approach the Hydra Cluster, a realm of greater challenges. Here, your SQL skills will be tested with more complex queries involving multiple tables and advanced conditions.

    **Your mission**:
    - Tackle intricate SQL queries that require multi-table joins, aggregations, and precise filtering.
    - Each completed query fuels your ship, bringing you closer to mastering the galaxy.

    **Stages**:
    1. **Unveiling the Major Expeditions**: Retrieve missions with large crews, joining tables and ordering results.
    2. **Largest Moons and Missions**: Find the largest moon and the mission to its planet.
    3. **Mars Missions and Their Moons**: List missions to Mars along with its moons and crew sizes.
    4. **Planets with Null Discovery Year**: Discover missions to planets with unknown discovery years.
    5. **Galileo Discoveries and Their Missions**: Find missions to planets discovered by Galileo.

    **Rules**:
    - Complete each stage in sequence to unlock the next.
    - Hints are available if you're stuck.
    - Submit your SQL query to check your progress, and compare your results with the correct output when successful.

    Prepare yourself, astronaut. The challenges ahead are tougher, but so is your resolve!
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
