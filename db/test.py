import streamlit as st

# Test if Streamlit can read the secrets
try:
    db_user = st.secrets["postgresql"]["DB_USER"]
    db_password = st.secrets["postgresql"]["DB_PASSWORD"]
    db_host = st.secrets["postgresql"]["DB_HOST"]
    db_name = st.secrets["postgresql"]["DB_NAME"]
    db_port = st.secrets["postgresql"].get("DB_PORT", "5432")  # Default port 5432

    # Display the retrieved secrets (you might want to avoid printing the password in real usage)
    st.write("Database User:", db_user)
    st.write("Database Host:", db_host)
    st.write("Database Name:", db_name)
    st.write("Database Port:", db_port)

except Exception as e:
    st.error(f"Error: {e}")
