import tkinter as tk
import mysql.connector
from mysql.connector import Error
import random
from datetime import datetime

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="jaiminpatel",
    database="Project"
)

def format_datetime(dt):
    return dt.strftime("%I:%M %p, %Y-%m-%d") if dt else "N/A"

root = tk.Tk()
root.title("Login Interface")
root.geometry("530x600")

login_frame = tk.Frame(root)
signup_frame = tk.Frame(root)
main_frame = tk.Frame(root)

info_frame = tk.Frame(main_frame, bg="#ADD8E6")
info_frame.pack(fill=tk.X, padx=5, pady=(5, 10))

login_times_box = tk.Frame(main_frame, bg="#90EE90")
login_times_box.pack(fill=tk.X, padx=5, pady=(0, 10))

login_labels = []

def clear_fields():
    if login_frame.winfo_ismapped():
        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)
    elif signup_frame.winfo_ismapped():
        signup_username_entry.delete(0, tk.END)
        signup_password_entry.delete(0, tk.END)

    login_error_label.config(text="")
    signup_error_label.config(text="")

def show_frame(frame):
    if frame == login_frame or frame == signup_frame:
        clear_fields()
    frame.tkraise()

for i in range(10):
    label = tk.Label(login_times_box, text="", font=("Arial", "12"), bg="#90EE90", fg="black")
    login_labels.append(label)


def login():
    username = username_entry.get()
    password = password_entry.get()

    print(f"Attempting login with Username: {username}, Password: {password}")
    
    try:
        cursor = connection.cursor()
        
        # Fetch user data for the given username only
        cursor.execute("SELECT id, password, act_creation, Login1, Login2, Login3, Login4, Login5, Login6, Login7, Login8, Login9, Login10 FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()

        if result:
            stored_user_id = result[0]
            stored_password = result[1]
            acct_creation_time = result[2]
            login_times = list(result[3:13])  # Convert to list for mutability

            # Check if all login slots are filled
            if all(login_time is not None for login_time in login_times):
                no_more_logins_label.config(text="No more logins possible.")
            else:
                no_more_logins_label.config(text="")

            # Check password
            if stored_password == password:
                login_time = datetime.now()

                # Update the login time in the database
                for i in range(10):
                    if login_times[i] is None:
                        cursor.execute(f"UPDATE users SET Login{i+1} = %s WHERE username = %s", (login_time, username))
                        login_times[i] = login_time  # Update the login_times for display
                        break

                connection.commit()

                # Update account creation label
                acct_creation_label.config(text=f"Account Created: {format_datetime(acct_creation_time)}")

                # Update and display login times
                for idx, label in enumerate(login_labels):
                    if idx < len(login_times) and login_times[idx] is not None:
                        label.config(text=f"Login {idx + 1}: {format_datetime(login_times[idx])}")
                        label.pack(in_=login_times_box, pady=(5, 5))  # Pack the label
                    else:
                        label.pack_forget()  # Hide unused labels

                show_frame(main_frame)  # Show main frame after login
                return

            else:
                login_error_label.config(text="Invalid login credentials", fg="red")
        else:
            login_error_label.config(text="Invalid login credentials", fg="red")

    except Error as e:
        print(f"Error during login: {e}")
        login_error_label.config(text="Error during login. Please try again.", fg="red")

    finally:
        cursor.close()


def signup():
    username = signup_username_entry.get()
    password = signup_password_entry.get()

    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
    exists = cursor.fetchone()[0]

    if exists > 0:
        signup_error_label.config(text="Username already used")
        cursor.close()
        return

    # Generate a unique user ID
    user_id = random.randint(1, 100)
    while True:
        cursor.execute("SELECT COUNT(*) FROM users WHERE id = %s", (user_id,))
        if cursor.fetchone()[0] == 0:
            break
        user_id = random.randint(1, 100)

    try:
        act_creation_time = datetime.now()
        cursor.execute("INSERT INTO users (id, username, password, act_creation) VALUES (%s, %s, %s, %s)",
                       (user_id, username, password, act_creation_time))
        connection.commit()

        signup_error_label.config(text="Signup successful! Please login.")
        acct_creation_label.config(text="")

        for label in login_labels:
            label.config(text="")
            label.pack_forget()

        signup_username_entry.delete(0, tk.END)
        signup_password_entry.delete(0, tk.END)

        show_frame(login_frame)
    except Error as e:
        signup_error_label.config(text=f"Error: {e}")
    finally:
        cursor.close()


def delete_account():
    username = username_entry.get().strip()
    print(f"Username for deletion: '{username}'")

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
        user_exists = cursor.fetchone()[0]
        print(f"User exists: {user_exists}")

        if user_exists == 0:
            login_error_label.config(text="Account not found.", fg="red")
            return

        cursor.execute("DELETE FROM users WHERE username = %s", (username,))
        connection.commit()
        print("Account deleted from database.")

        acct_creation_label.config(text="")
        for label in login_labels:
            label.config(text="")
            label.pack_forget()

        logout()
        login_error_label.config(text="Account deleted successfully.", fg="green")

    except Error as e:
        print(f"Error deleting account: {e}")
        login_error_label.config(text="Error deleting account. Please try again.", fg="red")

    finally:
        cursor.close()

def logout():
    username_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)

    acct_creation_label.config(text="")
    
    for label in login_labels:
        label.config(text="")
        label.pack_forget()

    no_more_logins_label.config(text="")

    show_frame(login_frame)


tk.Label(login_frame, text="Login", font=("Arial", 18)).pack(pady=20)
tk.Label(login_frame, text="Username:").pack()
username_entry = tk.Entry(login_frame)
username_entry.pack()
tk.Label(login_frame, text="Password:").pack()
password_entry = tk.Entry(login_frame, show="*")
password_entry.pack()
login_button = tk.Button(login_frame, text="Login", command=login)
login_button.pack(pady=10)
login_error_label = tk.Label(login_frame, text="", fg="red")
login_error_label.pack()
signup_button = tk.Button(login_frame, text="Sign Up", command=lambda: show_frame(signup_frame))
signup_button.pack(pady=10)

tk.Label(signup_frame, text="Sign Up", font=("Arial", 18)).pack(pady=20)
tk.Label(signup_frame, text="Username:").pack()
signup_username_entry = tk.Entry(signup_frame)
signup_username_entry.pack()
tk.Label(signup_frame, text="Password:").pack()
signup_password_entry = tk.Entry(signup_frame, show="*")
signup_password_entry.pack()
register_button = tk.Button(signup_frame, text="Register", command=signup)
register_button.pack(pady=10)
signup_error_label = tk.Label(signup_frame, text="", fg="red")
signup_error_label.pack()
login_redirect_button = tk.Button(signup_frame, text="Back to Login", command=lambda: show_frame(login_frame))
login_redirect_button.pack(pady=10)

title_frame = tk.Frame(main_frame)
title_frame.pack(pady=20)

acct_creation_label = tk.Label(info_frame, text="", font=("Arial", "14"), bg="#ADD8E6", fg="black")
acct_creation_label.pack(pady=5)

no_more_logins_label = tk.Label(main_frame, text="", fg="red", font=("Arial", "14"))
no_more_logins_label.pack(pady=5)

logout_button = tk.Button(main_frame, text="Logout", command=logout, bg="#FFFFFF", fg="#000000", font=("Arial", 14), width=20)
logout_button.pack(pady=5)

delete_account_button = tk.Button(main_frame, text="Delete Account", command=delete_account, bg="#FF0000", fg="#000000", font=("Arial", 14), width=20)
delete_account_button.pack(pady=10)

for frame in (login_frame, signup_frame, main_frame):
    frame.place(relwidth=1, relheight=1)

show_frame(login_frame)

root.mainloop()
