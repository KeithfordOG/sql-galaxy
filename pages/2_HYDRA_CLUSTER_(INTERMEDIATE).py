import streamlit as st
import pandas as pd
import sqlparse
from db_utils import execute_sql_query  # Assuming db_utils.py contains the execute_sql_query function

# Sample data for planets, missions, and moons (you can replace this with your actual CSV data)
planets_df = pd.read_csv('db/planets.csv')
missions_df = pd.read_csv('db/missions.csv')
moons_df = pd.read_csv('db/moons.csv')

#Title
st.title('INTERMEDIATE')

# Image Header for Intermediate Mode
st.image("images/hydra_cluster.png", "Hydra Cluster (Cluster Galaxy) *Generated by ChatGPT4", use_column_width=True)

# List of intermediate queries focusing on JOINs
intermediate_queries = [
    "Retrieve the planet name, mission name, and crew size for missions that had a crew size larger than three, ordered by crew size from largest to smallest.",
    "Find the largest moon and the mission to its planet.",
    "Retrieve missions to Mars and their crew sizes and moons.",
    "Return the mission name, discovery year, and mission date for planets with a NULL discovery year.",
    "Retrieve the mission_name and mission_date for planets discovered by Galileo."
]

# Correct answers indexed by question number for intermediate difficulty
intermediate_answers = [
    [
        # Basic INNER JOIN and WHERE clause
        "SELECT planet_name, mission_name, crew_size FROM missions INNER JOIN planets ON missions.planet_id = planets.planet_id WHERE crew_size > 3 ORDER BY crew_size DESC;",
        # Using table aliases
        "SELECT p.planet_name, m.mission_name, m.crew_size FROM missions m INNER JOIN planets p ON m.planet_id = p.planet_id WHERE m.crew_size > 3 ORDER BY m.crew_size DESC;",
        # Using LIMIT to restrict results
        "SELECT planet_name, mission_name, crew_size FROM missions INNER JOIN planets ON missions.planet_id = planets.planet_id WHERE crew_size > 3 ORDER BY crew_size DESC LIMIT 5;",
        # Using DISTINCT to remove duplicates
        "SELECT DISTINCT planet_name, mission_name, crew_size FROM missions INNER JOIN planets ON missions.planet_id = planets.planet_id WHERE crew_size > 3 ORDER BY crew_size DESC;"
    ],
    [
        # Largest moon and its planet's mission
        "SELECT moon_name, mission_name FROM moons INNER JOIN missions ON moons.planet_id = missions.planet_id ORDER BY diameter_km DESC LIMIT 1;"
    ],
    [
        # INNER JOIN
        "SELECT mission_name, moon_name, crew_size FROM missions INNER JOIN planets ON missions.planet_id = planets.planet_id INNER JOIN moons ON moons.planet_id = planets.planet_id WHERE planet_name = 'Mars';",
        # LEFT JOIN (includes missions without moons)
        "SELECT mission_name, moon_name, crew_size FROM missions LEFT JOIN planets ON missions.planet_id = planets.planet_id LEFT JOIN moons ON moons.planet_id = planets.planet_id WHERE planet_name = 'Mars';",
        # RIGHT JOIN (includes moons without missions)
        "SELECT mission_name, moon_name, crew_size FROM moons RIGHT JOIN planets ON moons.planet_id = planets.planet_id RIGHT JOIN missions ON missions.planet_id = planets.planet_id WHERE planet_name = 'Mars';",
        # FULL OUTER JOIN (includes all missions and moons, even those without matches)
        "SELECT mission_name, moon_name, crew_size FROM missions FULL OUTER JOIN planets ON missions.planet_id = planets.planet_id FULL OUTER JOIN moons ON moons.planet_id = planets.planet_id WHERE planet_name = 'Mars';"
    ],
    [
        # Basic INNER JOIN with NULL discovery year
        "SELECT mission_name, discovery_year, mission_date FROM missions INNER JOIN planets ON missions.planet_id = planets.planet_id WHERE discovery_year IS NULL;",
        # LEFT JOIN
        "SELECT mission_name, discovery_year, mission_date FROM missions LEFT JOIN planets ON missions.planet_id = planets.planet_id WHERE discovery_year IS NULL;",
        # DISTINCT to remove duplicates
        "SELECT DISTINCT mission_name, discovery_year, mission_date FROM missions INNER JOIN planets ON missions.planet_id = planets.planet_id WHERE discovery_year IS NULL;",
        # Including planet_name in the result
        "SELECT mission_name, planet_name, discovery_year, mission_date FROM missions INNER JOIN planets ON missions.planet_id = planets.planet_id WHERE discovery_year IS NULL;",
        # Sorting by mission date
        "SELECT mission_name, discovery_year, mission_date FROM missions INNER JOIN planets ON missions.planet_id = planets.planet_id WHERE discovery_year IS NULL ORDER BY mission_date ASC;"
    ],
    [
        # Basic INNER JOIN with Galileo filter
        "SELECT mission_name, mission_date FROM missions INNER JOIN planets ON missions.planet_id = planets.planet_id WHERE discoverer = 'Galileo';",
        # Using table aliases for cleaner queries
        "SELECT m.mission_name, m.mission_date FROM missions m INNER JOIN planets p ON m.planet_id = p.planet_id WHERE p.discoverer = 'Galileo';",
        # Including planet name for more context
        "SELECT m.mission_name, m.mission_date, p.planet_name FROM missions m INNER JOIN planets p ON m.planet_id = p.planet_id WHERE p.discoverer = 'Galileo';",
        # Ordering the result by mission date
        "SELECT mission_name, mission_date FROM missions INNER JOIN planets ON missions.planet_id = planets.planet_id WHERE discoverer = 'Galileo' ORDER BY mission_date ASC;",
        # Using DISTINCT to avoid duplicate mission names
        "SELECT DISTINCT mission_name, mission_date FROM missions INNER JOIN planets ON missions.planet_id = planets.planet_id WHERE discoverer = 'Galileo';"
    ]
]

# Hints for each question
intermediate_hints = [
    "Use `INNER JOIN` to combine the missions and planets tables, and use `WHERE` to filter crew sizes larger than 3. Use `ORDER BY crew_size DESC` to sort the results.",
    "Use `ORDER BY diameter_km DESC` and `LIMIT 1` to find the largest moon.",
    "You can use different types of joins depending on the result you want. Try `INNER JOIN` to get exact matches, `LEFT JOIN` to include missions without moons, `RIGHT JOIN` to include moons without missions, or `FULL OUTER JOIN` to include everything.",
    "Use `WHERE discovery_year IS NULL` to filter for planets with no discovery year. You can also include both `mission_name`, `discovery_year`, and `mission_date` in the result.",
    "Use `WHERE discoverer = 'Galileo'` to filter planets and return the `mission_name` and `mission_date`. You can include `planet_name` for more details. Use `INNER JOIN` to combine the planets and missions tables."
]

# Function to normalize and format SQL query
def normalize_sql(query):
    return sqlparse.format(query, reindent=True, keyword_case='upper').strip()

# Initialize session state to track correctness and progress
if 'answer_correct_intermediate' not in st.session_state:
    st.session_state.answer_correct_intermediate = [False] * len(intermediate_queries)  # Track correctness for each intermediate question

if 'questions_completed' not in st.session_state:
    st.session_state.questions_completed = 0  # Track how many questions have been completed

# Create tabs for each intermediate question
tabs = st.tabs([f"Question {i+1}" for i in range(len(intermediate_queries))])

# Loop through each question and set up a tab
for i, query in enumerate(intermediate_queries):
    with tabs[i]:
        st.title(f"Question {i+1} ✨")
        st.write(query)

        # Use text_area for multi-line input
        user_answer = st.text_area(f"Your Answer for Question {i+1}", key=f"intermediate_answer_{i}")

        # Hint section
        with st.expander("Need a hint?"):
            st.write(intermediate_hints[i])

        # Submit button for each question
        if st.button(f"Submit Answer for Question {i+1}", key=f"submit_intermediate_{i}"):
            # Normalize user's answer and correct answers
            normalized_user_answer = normalize_sql(user_answer)
            normalized_correct_answers = [normalize_sql(answer) for answer in intermediate_answers[i]]

            # Always run the user's query and show the result (even if it's wrong)
            st.write(f"Your Attempted Query: \n```sql\n{user_answer}\n```")
            try:
                query_result = execute_sql_query(user_answer)  # Execute the user's SQL query
                st.write(query_result)  # Show the SQL query result
            except Exception as e:
                st.error(f"Error running query: {e}")

            # Check if the user's answer matches any normalized correct solutions
            if normalized_user_answer in normalized_correct_answers:
                if not st.session_state.answer_correct_intermediate[i]:  # Ensure it's only counted once
                    st.session_state.questions_completed += 1  # Increment completed count only once
                    st.session_state.answer_correct_intermediate[i] = True
                st.success("Great job! That's correct.")
            else:
                st.error("Incorrect answer. Please try again.")

        # Display the correct answer if the user has answered correctly
        if st.session_state.answer_correct_intermediate[i]:
            st.write(f"You've answered Question {i+1} correctly.")

# Show progress
st.subheader(f"Progress: {st.session_state.questions_completed} out of {len(intermediate_queries)} questions completed! 👩‍🚀")

# Schema Title
st.title('Schema')

# Planets Table (Fetched from PostgreSQL)
st.subheader('🌍 Planets Table')
st.write("This table contains detailed information about planets, including their distance from the sun, discoverers, and unique IDs.")
planets_query = "SELECT * FROM planets;"  # Query the planets table from PostgreSQL
planets_df = execute_sql_query(planets_query)
st.write(planets_df)

# Missions Table (Fetched from PostgreSQL)
st.subheader('🚀 Missions Table')
st.write("This table contains the details of various space missions, including their destination planets and crew sizes.")
missions_query = "SELECT * FROM missions;"  # Query the missions table from PostgreSQL
missions_df = execute_sql_query(missions_query)
st.write(missions_df)

# Moons Table (Fetched from PostgreSQL)
st.subheader('🌕 Moons Table')
st.write("This table tracks all the moons, their diameters, discoverers, and the planets they orbit.")
moons_query = "SELECT * FROM moons;"  # Query the moons table from PostgreSQL
moons_df = execute_sql_query(moons_query)
st.write(moons_df)
