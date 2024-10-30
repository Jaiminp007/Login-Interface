import streamlit as st
import mysql.connector
from mysql.connector import Error
import random
from datetime import datetime

# Database connection
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="jaiminpatel",
    database="Project"
)

# Helper function for formatting datetime
def format_datetime(dt):
    return dt.strftime("%I:%M %p, %Y-%m-%d") if dt else "N/A"

# Streamlit UI
st.title("Login Interface")

# Frames for login and signup
if 'page' not in st.session_state:
    st.session_state.page = 'login'

# Login Frame
if st.session_state.page == 'login':
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_error_label = st.empty()
    if st.button("Login"):
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT id, password, act_creation, Login1, Login2, Login3, Login4, Login5, Login6, Login7, Login8, Login9, Login10 FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()

            if result:
                stored_user_id = result[0]
                stored_password = result[1]
                acct_creation_time = result[2]
                login_times = list(result[3:13])  # Convert to list for mutability

                # Password Check
                if stored_password == password:
                    login_time = datetime.now()
                    for i in range(10):
                        if login_times[i] is None:
                            cursor.execute(f"UPDATE users SET Login{i+1} = %s WHERE username = %s", (login_time, username))
                            login_times[i] = login_time
                            break
                    connection.commit()
                    # Set session state variables
                    st.session_state.page = 'main'
                    st.session_state.username = username  # Store username in session
                    st.session_state.acct_creation_time = acct_creation_time
                    st.session_state.login_times = login_times
                else:
                    login_error_label.error("Invalid login credentials")
            else:
                login_error_label.error("Invalid login credentials")

        except Error as e:
            login_error_label.error("Error during login. Please try again.")
        finally:
            cursor.close()

    if st.button("Go to Sign Up"):
        st.session_state.page = 'signup'

# Signup Frame
elif st.session_state.page == 'signup':
    st.subheader("Sign Up")
    signup_username = st.text_input("Username", key="signup_username")
    signup_password = st.text_input("Password", type="password", key="signup_password")
    signup_error_label = st.empty()
    if st.button("Register"):
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (signup_username,))
        exists = cursor.fetchone()[0]
        if exists > 0:
            signup_error_label.error("Username already used")
        else:
            user_id = random.randint(1, 100)
            while True:
                cursor.execute("SELECT COUNT(*) FROM users WHERE id = %s", (user_id,))
                if cursor.fetchone()[0] == 0:
                    break
                user_id = random.randint(1, 100)
            try:
                act_creation_time = datetime.now()
                cursor.execute("INSERT INTO users (id, username, password, act_creation) VALUES (%s, %s, %s, %s)", (user_id, signup_username, signup_password, act_creation_time))
                connection.commit()
                signup_error_label.success("Signup successful! Please login.")
                st.session_state.page = 'login'
            except Error as e:
                signup_error_label.error(f"Error: {e}")
            finally:
                cursor.close()

    if st.button("Back to Login"):
        st.session_state.page = 'login'

# Main Frame
elif st.session_state.page == 'main':
    st.subheader(f"Welcome to your Account, {st.session_state.username}")
    acct_creation_label = f"Account Created: {format_datetime(st.session_state.acct_creation_time)}"
    st.write(acct_creation_label)

    st.write("Login Times:")
    for idx, login_time in enumerate(st.session_state.login_times):
        if login_time:
            st.write(f"Login {idx + 1}: {format_datetime(login_time)}")

    if st.button("Logout"):
        st.session_state.page = 'login'
        st.session_state.acct_creation_time = None
        st.session_state.login_times = []
        st.session_state.username = None

    if st.button("Delete Account"):
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM users WHERE username = %s", (st.session_state.username,))
            connection.commit()
            st.write("Account deleted successfully.")
            st.session_state.page = 'login'
        except Error as e:
            st.write(f"Error deleting account: {e}")
        finally:
            cursor.close()
