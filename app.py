from flask import Flask, request, redirect, url_for, session, flash, render_template
from datetime import datetime
import random
import json

app = Flask(__name__)
app.secret_key = 'aP9v47xJ0$zB7jG9dH2u8QkL6mNyfXwS3tV2!cU5pF4nRmD1eW'

# Helper function for formatting datetime
def format_datetime(dt):
    return dt.strftime("%I:%M %p, %Y-%m-%d") if dt else "N/A"

# Load data from JSON file
def load_data():
    with open("data.json", "r") as file:
        return json.load(file)

# Save data to JSON file
def save_data(data):
    with open("data.json", "w") as file:
        json.dump(data, file, indent=4)

@app.route('/')
def home():
    return redirect(url_for('login'))  # Redirect to login page when accessing the root URL

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        data = load_data()
        user = data.get(username)
        
        if user and user['password'] == password:
            # Update login time
            login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            user['login_times'].append(login_time)
            save_data(data)
            
            # Set session variables
            session['username'] = username
            session['acct_creation_time'] = user['act_creation']
            session['login_times'] = user['login_times']
            return redirect(url_for('main'))
        else:
            flash("Invalid login credentials", category='error')

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        signup_username = request.form['username']
        signup_password = request.form['password']

        data = load_data()
        
        if signup_username in data:
            flash("Username already used", category='error')
        else:
            user_id = random.randint(1, 100)
            acct_creation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data[signup_username] = {
                "id": user_id,
                "username": signup_username,
                "password": signup_password,
                "act_creation": acct_creation_time,
                "login_times": []
            }
            save_data(data)
            flash("Signup successful! Please login.", category='success')
            return redirect(url_for('login'))
            
    return render_template('signup.html')

@app.route('/main')
def main():
    if 'username' not in session:
        return redirect(url_for('login'))

    acct_creation_time = format_datetime(datetime.strptime(session['acct_creation_time'], "%Y-%m-%d %H:%M:%S"))
    login_times = [format_datetime(datetime.strptime(lt, "%Y-%m-%d %H:%M:%S")) for lt in session['login_times']]
    
    return render_template('main.html', username=session['username'], acct_creation_time=acct_creation_time, login_times=login_times)

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/delete_account', methods=['POST'])
def delete_account():
    if 'username' in session:
        data = load_data()
        data.pop(session['username'], None)
        save_data(data)
        flash("Account deleted successfully.", category='success')
        session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
