import streamlit as st

# About Me Page Header
st.title("About Me")


# Introduction Section
st.header("Hi, I'm Keith Moore! 🚀")
st.write("""
I'm a passionate developer with a love for data and all things SQL. I created **SQL Galaxy** to help both beginners and seasoned developers improve their SQL skills through interactive challenges inspired by space exploration.

As a developer aiming to become proficient in full stack development, SQL and data management are essential tools in my toolkit. Through this project, I hope to inspire others to enjoy the problem-solving aspect of SQL while learning the key concepts in a fun and engaging way.
""")

# Project Purpose Section
st.header("What is SQL Galaxy?")
st.write("""
**SQL Galaxy** is an interactive game designed to enhance SQL learning by offering challenges of increasing difficulty, from basic queries to advanced subqueries and joins. The idea is simple: you solve SQL problems to navigate through different galaxies and levels.

Each query represents a learning opportunity, with explanations and solutions provided for each step. The game covers fundamental SQL operations such as `SELECT`, `JOIN`, and `WHERE`, and progresses into more complex concepts like `CTEs` and `subqueries`.
""")

# Technologies Used Section
st.header("Technologies Used 🌐")
st.write("""
SQL Galaxy was built using the following technologies:
- **Streamlit**: For creating the interactive web-based interface.
- **Heroku**: For deployment
- **PostgreSQL**: As the backend database to store and query data.
- **Python (psycopg2)**: For handling database connections and executing SQL queries.
- **Pandas**: To display query results in a tabular format.
- **VS Code**: For coding and development.
- **GitHub**: For version control and collaboration.
- **ChatGPT4**: For image generation
""")

# Skills Highlighted Section
st.header("Skills Highlighted 📊")
st.write("""
Through this project, I aim to showcase and improve the following skills:
- **SQL Mastery**: Writing complex queries with `JOINs`, `subqueries`, and `CTEs`.
- **Database Design**: Structuring relational databases for efficient querying.
- **Backend Development**: Integrating Python with PostgreSQL.
- **Data Analysis**: Using SQL and Python to retrieve and analyze data.
- **Frontend Development**: Building interactive web applications using Streamlit.
""")

# Future Plans Section
st.header("Future Plans for SQL Galaxy 🚀")
st.write("""
SQL Galaxy is just the beginning! Here are some future features and updates I plan to add:
- **Leaderboard**: A ranking system where users can compare scores.
- **Timed Challenges**: Introducing time-based challenges to add an extra layer of difficulty.
- **New Galaxy Levels**: Adding more advanced queries, including window functions and query optimization techniques.
- **User Submissions**: Allow users to submit their own SQL challenges to the game.
""")

# Call to Action Section
st.subheader("Connect with Me")
st.write("""
Im always looking to connect with fellow developers and data enthusiasts. Feel free to reach out to me through my [GitHub](https://github.com/KeithfordOG/) or connect on LinkedIn to discuss this project or anything related to SQL, databases, or full stack development.
""")

st.image("images/galaxy_about.png", caption="SQL Galaxy - Journey to SQL Mastery", use_column_width=True)