from flask import Flask, render_template, request, redirect, url_for, session
import time
from accountService import AccountService

app = Flask(__name__)
app.secret_key = 'super_secret_key'

blocked_users = {}
users_attempts = {}

# Funkcja do sprawdzania, czy użytkownik jest zablokowany
def is_user_blocked(user_id):
    return user_id in blocked_users and blocked_users[user_id] > time.time()

# Funkcja do logowania
def login_user(user_id):
    blocked_users.pop(user_id, None)
    # users_attempts.pop(user_id, None)

# Funkcja do zablokowania użytkownika na określony czas
def block_user(user_id, duration=60):
    blocked_users[user_id] = time.time() + duration


# Middleware do sprawdzania blokad
# @app.before_request
# def check_blocked_users():
#     user_id = session.get('user_id')
#     if user_id and is_user_blocked(user_id):
#         return render_template('blocked.html', remaining_time=int(session['blocked_users'][user_id] - time.time()))

# Strona logowania - wprowadzenie identyfikatora klienta
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        client_number = request.form.get('user_id')
        if not client_number:
            return render_template('login.html', error='Proszę podać identyfikator klienta.')

        if is_user_blocked(client_number):
            return render_template('blocked.html', remaining_time=int(blocked_users[client_number] - time.time()))

        # session['login_attempts'] = 0  # Zresetuj liczbę prób logowania
        users_attempts[client_number] = 0
        login_user(client_number)
        return redirect(url_for('password', client_number=client_number))


    return render_template('login.html')

# Strona logowania - wprowadzenie hasła
@app.route('/password/<client_number>', methods=['GET', 'POST'])
def password(client_number):
    # user_id = session.get('user_id')
    if not client_number or is_user_blocked(client_number):
        return redirect(url_for('login'))

    accountService = AccountService(client_number, 1)

    if request.method == 'POST':
        if client_number not in users_attempts:
            return redirect(url_for('login'))
            # users_attempts[client_number] = 0
        password = request.form.get('password')
        # Sprawdź hasło w bazie danych
        # (zakładam, że masz funkcję do tego, np. check_password_in_database)
        if accountService.verify_password_char(password):
            # Zalogowano pomyślnie
            session['client_number'] = client_number
            return render_template('success.html')

        # session['login_attempts'] = session.get('login_attempts', 0) + 1
        # if session['login_attempts'] >= 3:
        users_attempts[client_number] += 1
        if users_attempts[client_number] >= 3:
            block_user(client_number)
            return render_template('blocked.html', remaining_time=60)

        # Obsługa niepoprawnego hasła
        return render_template('password.html', error='Nieprawidłowy login lub hasło.', client_number=client_number)

    return render_template('password.html', client_number=client_number)

if __name__ == '__main__':
    app.run(debug=True)
