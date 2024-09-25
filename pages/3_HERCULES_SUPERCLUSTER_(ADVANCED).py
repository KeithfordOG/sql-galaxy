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

# Define stages, questions, answers, hints, and explanations for Advanced
journey_stages = [
    "The Moon Monarch",
    "Far Reaches of Space",
    "Beyond Average Crews",
    "Moons and Missions",
    "Above Average Moons"
]

journey_questions = [
    "In the vastness of the Hercules Supercluster, one planet stands out with the most moons. To navigate through this region, you need to find this planet.\n\n*Find the planet with the most moons using a subquery.*",
    
    "The distant planets hold secrets beyond 500 million km from Earth. To proceed, you must retrieve missions heading to these far-off worlds.\n\n*Retrieve the mission name and crew size for all missions where the destination planet is further than 500 million km from Earth, using a subquery.*",
    
    "Elite missions often have crew sizes larger than average. Your task is to identify how many such missions exist to unlock the next phase.\n\n*Write a query to find the total number of missions where the crew size was larger than the average crew size of all missions, using a subquery.*",
    
    "Some missions venture to planets with numerous moons. Find these missions to chart your path forward.\n\n*Find the missions where the destination planet has more than 2 moons, using a subquery.*",
    
    "Planets with an above-average number of moons may harbor advanced civilizations. To make contact, you need to list these planets.\n\n*Write a query to retrieve the planets that have more moons than the average number of moons for all planets, using a CTE.*"
]

correct_answers = [
    # Question 1
    [
        "SELECT planet_name FROM planets WHERE planet_id = (SELECT planet_id FROM moons GROUP BY planet_id ORDER BY COUNT(*) DESC LIMIT 1);",
        "SELECT p.planet_name FROM planets p WHERE p.planet_id = (SELECT m.planet_id FROM moons m GROUP BY m.planet_id ORDER BY COUNT(*) DESC LIMIT 1);"
    ],
    # Question 2
    [
        "SELECT mission_name, crew_size FROM missions WHERE planet_id IN (SELECT planet_id FROM planets WHERE distance_from_earth > 500);",
        "SELECT m.mission_name, m.crew_size FROM missions m WHERE m.planet_id IN (SELECT p.planet_id FROM planets p WHERE p.distance_from_earth > 500);"
    ],
    # Question 3
    [
        "SELECT COUNT(*) FROM missions WHERE crew_size > (SELECT AVG(crew_size) FROM missions);",
        "SELECT COUNT(*) AS mission_count FROM missions WHERE crew_size > (SELECT AVG(crew_size) FROM missions);"
    ],
    # Question 4
    [
        "SELECT mission_name FROM missions WHERE planet_id IN (SELECT planet_id FROM moons GROUP BY planet_id HAVING COUNT(moon_id) > 2);",
        "SELECT m.mission_name FROM missions m WHERE m.planet_id IN (SELECT mo.planet_id FROM moons mo GROUP BY mo.planet_id HAVING COUNT(mo.moon_id) > 2);"
    ],
    # Question 5
    [
        """
        WITH moon_counts AS (
            SELECT planet_id, COUNT(moon_id) AS num_moons
            FROM moons
            GROUP BY planet_id
        ), average_moons AS (
            SELECT AVG(num_moons) AS avg_moons FROM moon_counts
        )
        SELECT planet_name
        FROM planets
        WHERE planet_id IN (
            SELECT planet_id FROM moon_counts WHERE num_moons > (SELECT avg_moons FROM average_moons)
        );
        """,
        """
        WITH moon_counts AS (
            SELECT planet_id, COUNT(moon_id) AS num_moons
            FROM moons
            GROUP BY planet_id
        )
        SELECT p.planet_name
        FROM planets p
        JOIN moon_counts mc ON p.planet_id = mc.planet_id
        WHERE mc.num_moons > (SELECT AVG(num_moons) FROM moon_counts);
        """
    ]
]

journey_hints = [
    ["Use a subquery with `GROUP BY` and `ORDER BY COUNT(*) DESC` to find the planet ID with the most moons.", "Join this subquery result with the `planets` table to get the planet name."],
    ["Filter planets where `distance_from_earth > 500` in a subquery and use `IN` to retrieve missions to those planets.", "Alternatively, use a subquery in the `WHERE` clause of your `SELECT` statement on `missions`."],
    ["Calculate the average crew size using `AVG(crew_size)` in a subquery.", "Use this average to find missions where `crew_size` is greater than the average."],
    ["Use a subquery with `GROUP BY` and `HAVING COUNT(moon_id) > 2` to find planet IDs.", "Retrieve mission names where `planet_id` is in this subquery result."],
    ["Use a CTE (`WITH` clause) to calculate the number of moons per planet.", "Calculate the average number of moons and select planets with more moons than this average."]
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
                st.success(f"Excellent work, {st.session_state.user_name}! You've completed Stage {i+1}.")

                # Update progress bar
                update_progress(st.session_state.stages_completed)

                # Automatic transition after a delay
                time.sleep(3)

                if i < 4:
                    st.session_state.current_stage = i + 1
                    st.experimental_rerun()
                else:
                    st.balloons()
                    st.write(f"Congratulations, {st.session_state.user_name}! 🎉 You've conquered the Hercules Supercluster!")
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
    | planet_id | planet_name  | distance_from_earth | discoverer               | discovery_year |
    |-----------|--------------|---------------------|--------------------------|----------------|
    | 1         | Mercury      | 77                  | Known since antiquity    | NULL           |
    | 2         | Venus        | 108                 | Known since antiquity    | NULL           |
    | 3         | Earth        | 0                   | N/A                      | NULL           |
    | 4         | Mars         | 225                 | Galileo                  | 1610           |
    | 5         | Jupiter      | 778                 | Galileo                  | 1610           |
    | 6         | Saturn       | 1,433               | Galileo                  | 1610           |
    | 7         | Uranus       | 2,871               | William Herschel         | 1781           |
    | 8         | Neptune      | 4,495               | Adams                    | 1846           |
    | 9         | Pluto        | 5,906               | Tombaugh                 | 1930           |
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
    | moon_id | moon_name  | planet_id | moon_diameter_km | discoverer               | discovery_year |
    |---------|------------|-----------|------------------|--------------------------|----------------|
    | 1       | Io         | 5         | 3643.2           | Galileo                  | 1610           |
    | 2       | Europa     | 5         | 3121.6           | Galileo                  | 1610           |
    | 3       | Ganymede   | 5         | 5262.4           | Galileo                  | 1610           |
    | 4       | Callisto   | 5         | 4820.6           | Galileo                  | 1610           |
    | 5       | Titan      | 6         | 5149.5           | Christiaan Huygens       | 1655           |
    | 6       | Enceladus  | 6         | 504.2            | William Herschel         | 1789           |
    | 7       | Mimas      | 6         | 396.4            | William Herschel         | 1789           |
    | 8       | Phobos     | 4         | 22.2             | Asaph Hall               | 1877           |
    | 9       | Deimos     | 4         | 12.6             | Asaph Hall               | 1877           |
    | 10      | Charon     | 9         | 1212             | James Christy            | 1978           |
    """)

def main():
    # Title and Introduction
    st.title('ADVANCED 🚀')

    # Hercules Supercluster Image at the top
    st.image("images/hercules_supercluster.png", use_column_width=True)

    # Brief description/intro explaining the five stages and rules
    st.markdown("""
    ### Welcome to the Hercules Supercluster Galaxy!
    You've journeyed far and now stand at the edge of the Hercules Supercluster, the pinnacle of SQL challenges. Here, you will face the most complex queries involving subqueries and Common Table Expressions (CTEs).

    **Your mission**:
    - Solve intricate SQL problems that require advanced concepts like subqueries and CTEs.
    - Each challenge overcome brings you closer to becoming a SQL master.

    **Stages**:
    1. **The Moon Monarch**: Identify the planet with the most moons using subqueries.
    2. **Far Reaches of Space**: Retrieve missions to distant planets using subqueries.
    3. **Beyond Average Crews**: Find missions with above-average crew sizes using subqueries.
    4. **Moons and Missions**: Discover missions to planets with numerous moons using subqueries.
    5. **Above Average Moons**: List planets with more moons than average using a CTE.

    **Rules**:
    - Complete each stage in sequence to unlock the next.
    - Hints are available if you're stuck.
    - Submit your SQL query to check your progress, and compare your results with the correct output when successful.

    Brace yourself, astronaut. The challenges here are formidable, but so are your skills!
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
