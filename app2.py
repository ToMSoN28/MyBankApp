import os
import random
import secrets
from datetime import timedelta

from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for, session
import time
from flask_session import Session
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv

from accountService import AccountService
from validationService import ValidationService
from sessionClass import SessionClass

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SESSION_KEY")
app.config['SESSION_COOKIE_HTTPONLY'] = True    # JS can not use session cookie
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'


blocking_time = 120
max_inactivity_time = 180  # Time in seconds (3 min) = 180
blocked_users = {}
logged_in_users = {}
session_info = {}

valid = ValidationService()


# Funkcja do sprawdzania, czy użytkownik jest zablokowany
def is_user_blocked(client_number):
    return client_number in blocked_users and blocked_users[client_number] > time.time()


# Funkcja do logowania
def login_user_in_session(client_number):
    session_id = session.get('session_id')
    if session_id:
        session_info[session_id].client_number = client_number
    else:
        unique_string = f"{request.remote_addr}{secrets.token_hex(16)}"
        print(unique_string)
        session['session_id'] = unique_string
        tmp = SessionClass()
        tmp.client_number = client_number
        session_info[unique_string] = tmp

def change_session_id():
    session_id = session.get('session_id')
    while True:
        unique_string = f"{request.remote_addr}{secrets.token_hex(16)}"
        print(unique_string)
        if session_id != unique_string:
            break
    print(session_id, unique_string)
    print(session_info[session_id].client_number)
    session_info[unique_string] = session_info.pop(session_id)

    session['session_id'] = unique_string
    print(session_info[unique_string].client_number)

# Funkcja do zablokowania użytkownika na określony czas
def block_user(client_number, duration=blocking_time):
    blocked_users[client_number] = time.time() + duration


def logout_inactive_users():
    logout_client_numbers = [key for key, _time in logged_in_users.items() if
                             (time.time() - _time) > max_inactivity_time]
    for client_number in logout_client_numbers:
        keys_to_del_in_session = [key for key, _session_info in session_info.items() if _session_info.client_nmber == client_number]
        for key in keys_to_del_in_session:
            del session_info[key]
        logged_in_users.pop(client_number, None)
    return True

def set_new_session_set(set_num):
    while True:
        tmp = random.randint(0, 9)
        if not tmp == set_num:
            return tmp


def session_set(session_id):
    # session_id = session.get('session_id')
    if session_info[session_id].set is None:
        session_info[session_id].set = random.randint(0, 9)
    return True


# Middleware do sprawdzania blokad
@app.before_request
def before_every_request():
    logout_inactive_users()
    session.permanent = True
    app.permanent_session_lifetime = timedelta(seconds=61)

    session_id = session.get('session_id')
    if session_id:
        if session_id not in session_info:
            session.pop('session_id', None)
            return redirect(url_for('login'))
        change_session_id()
        session_id = session.get('session_id')
        client_number = session_info[session_id].client_number
        if client_number and is_user_blocked(client_number):
            session_info[session_id].clean()  # clearing session after block
            return render_template('login.html',
                                   error=f'User {client_number} is blocked for {int(blocked_users[client_number] - time.time())} s')


# Strona logowania - wprowadzenie identyfikatora klienta
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        client_number = request.form.get('user_id')

        if is_user_blocked(client_number):
            return render_template('login.html',
                                   error=f'User {client_number} is blocked for {int(blocked_users[client_number] - time.time())} s')

        if client_number in logged_in_users:
            return render_template('login.html', error=f'User {client_number} is currently logged in')

        client_number = valid.sanitize_input(client_number)     # sanitize client number
        if valid.client_number_valid(client_number):
            # session['login_attempts'] = 0  # Zresetuj liczbę prób logowania
            login_user_in_session(client_number)
            session_id = session.get('session_id')
            session_set(session_id)
            session_info[session_id].attempts = 0

            return redirect(url_for('password'))
        else:
            return render_template('login.html')

    return render_template('login.html')


# Strona logowania - wprowadzenie hasła
@app.route('/password', methods=['GET', 'POST'])
def password():
    session_id = session.get('session_id')
    if session_id not in session_info:
        session.pop('session_id', None)
        return redirect(url_for('login'))
    client_number = session_info[session_id].client_number
    set_char = session_info[session_id].set
    if not client_number or is_user_blocked(client_number) or not set_char:
        return redirect(url_for('login'))

    accountService = AccountService(client_number)
    accountService.password_set_number = set_char
    char_table = accountService.get_login_set()

    if request.method == 'POST':
        first = request.form.get('first')
        second = request.form.get('second')
        third = request.form.get('third')
        fourth = request.form.get('fourth')
        if valid.password_char_input_valid(first) and valid.password_char_input_valid(second) and valid.password_char_input_valid(third) and valid.password_char_input_valid(fourth):
            password = first + second + third + fourth

            if accountService.verify_password_char(password):
                logged_in_users[client_number] = time.time()
                session_info[session_id].set = set_new_session_set(set_char)   # new set of password char chosen
                print(session_info[session_id].set)
                return redirect(url_for('my_account'))

        session_info[session_id].attempts += 1
        if session_info[session_id].attempts >= 3:
            block_user(client_number)
            return redirect(url_for('login'))

        return render_template('password.html', error='Incorrect login or password.',
                               attempts=3 - session_info[session_id].attempts,
                               first=char_table[0]+1,
                               second=char_table[1]+1,
                               third=char_table[2]+1,
                               fourth=char_table[3]+1,
                               client_number=client_number)

    return render_template('password.html',
                           first=char_table[0]+1,
                           second=char_table[1]+1,
                           third=char_table[2]+1,
                           fourth=char_table[3]+1,
                           client_number=client_number)


@app.route('/logout', methods=['GET'])
def logout():
    session_id = session.get('session_id')
    if session_id not in session_info:
        session.pop('session_id', None)
        return redirect(url_for('login'))
    client_number = session_info[session_id].client_number
    if client_number in logged_in_users:
        logged_in_users.pop(client_number)
    session_info[session_id].clean()
    # session.pop('session_id', None)
    return redirect(url_for('login'))


@app.route('/my-account', methods=['GET'])
def my_account():
    session_id = session.get('session_id')
    if session_id not in session_info:
        session.pop('session_id', None)
        return redirect(url_for('login'))
    client_number = session_info[session_id].client_number
    if client_number and client_number in logged_in_users:

        logged_in_users[client_number] = time.time()
        accountService = AccountService(client_number)
        name = accountService.user.name
        account_number = accountService.user.account_number
        balance = accountService.user.balance
        transactions = accountService.show_transfer_list()

        return render_template('myAccount.html', name=name, account_number=account_number,
                               balance=balance, transactions=transactions)

    return redirect(url_for('logout'))  # Wyloguj, jeśli brak danych sesji


@app.route('/transaction', methods=['GET', 'POST', 'PUT'])
def transaction():
    session_id = session.get('session_id')
    if session_id not in session_info:
        session.pop('session_id', None)
        return redirect(url_for('login'))
    client_number = session_info[session_id].client_number
    if client_number and client_number in logged_in_users:

        if request.method == 'POST':
            amount = request.form.get('amount')
            title = request.form.get('title')
            to_account_number = request.form.get('recipient_account_number')
            to_name = request.form.get('recipient_name')
            accountService = AccountService(client_number)
            error = ""
            if not valid.transaction_amount_value_valid(amount, accountService.user.balance):
                error += "Incorrect amount value. "
            if not valid.transaction_title_valid(title):
                error += "Incorrect title. "
            if not valid.transaction_recipient_account_number_valid(to_account_number):
                error += "Incorrect recipient account number. "
            if not valid.transaction_recipient_name_valid(to_name):
                error += "Incorrect name. "
            if error != "":
                return render_template('transaction.html', error=error)
            session_info[session_id].transaction = {
                'amount': amount,
                'title': title,
                'to_account_number': to_account_number,
                'to_name': to_name
            }
            print(session_info[session_id].transaction)
            return redirect(url_for('confirm_transaction'))

        logged_in_users[client_number] = time.time()
        error_code = session_info[session_id].error
        if error_code:
            session_info[session_id].error = None
            return render_template('transaction.html', error=error_code)
        return render_template('transaction.html')

    return redirect(url_for('logout'))  # Wyloguj, jeśli brak danych sesji


@app.route('/confirm-transaction', methods=['GET', 'POST'])
def confirm_transaction():
    session_id = session.get('session_id')
    if session_id not in session_info:
        session.pop('session_id', None)
        return redirect(url_for('login'))
    client_number = session_info[session_id].client_number
    if client_number and client_number in logged_in_users:

        if request.method == 'POST':
            accountService = AccountService(client_number)
            password = request.form.get('password')
            if accountService.verify_password(password) and valid.password_valid(password):
                transaction_data = session_info[session_id].transaction
                print(transaction_data)
                if not transaction_data:
                    return render_template('transaction.html', error='Server error, try again')

                session_info[session_id].transaction = {}
                tr = accountService.money_transfer(float(transaction_data['amount']),
                                                   transaction_data['title'],
                                                   transaction_data['to_account_number'],
                                                   transaction_data['to_name'])
                if tr == 1:
                    return redirect(url_for('my_account'))
                elif tr == 0:
                    session['error_code'] = 'Not enough money in your account to execute transaction'
                    return redirect(url_for('transaction'))
                else:
                    session['error_code'] = 'Bad recipient information'
                    return redirect(url_for('transaction'))
            else:
                session['error_code'] = 'Incorrect password'
                return redirect(url_for('transaction'))

        logged_in_users[client_number] = time.time()
        return render_template('confirmTransaction.html')

    return redirect(url_for('logout'))


@app.route('/secret-info', methods=['GET'])
def secret_info():
    session_id = session.get('session_id')
    if session_id not in session_info:
        session.pop('session_id', None)
        return redirect(url_for('login'))
    client_number = session_info[session_id].client_number
    if client_number and client_number in logged_in_users:
        logged_in_users[client_number] = time.time()
        accountService = AccountService(client_number)
        pesel, ccv = accountService.show_secure_info()
        return render_template('secretInfo.html', pesel=pesel.decode(), ccv=ccv.decode())

    return redirect(url_for('logout'))  # Wyloguj, jeśli brak danych sesji


@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
    session_id = session.get('session_id')
    if session_id not in session_info:
        session.pop('session_id', None)
        return redirect(url_for('login'))
    client_number = session_info[session_id].client_number
    if client_number and client_number in logged_in_users:

        if request.method == 'POST':
            actual = request.form.get('password')
            new = request.form.get('new_password')
            confirm = request.form.get('confirm_password')
            print(valid.password_valid(actual), valid.password_valid(new), valid.password_valid(confirm))
            if not valid.password_valid(actual) or not valid.password_valid(new) or not valid.password_valid(confirm):
                return render_template('changePassword.html',
                                       error='Server error, try again')
            accountService = AccountService(client_number)
            tmp = accountService.change_password(actual, new, confirm)
            if tmp == -2:
                return render_template('changePassword.html',
                                       error='The new password is different from the confirmation')
            elif tmp == -3:
                return render_template('changePassword.html', error='The new password is the same as the old one')
            elif tmp == -1:
                return render_template('changePassword.html',
                                       error='The new password is week, try with stronger password')
            elif tmp == 0:
                return render_template('changePassword.html', error='Incorrect actual password')
            elif tmp == 1:
                return redirect(url_for('my_account'))

        logged_in_users[client_number] = time.time()
        return render_template('changePassword.html')

    return redirect(url_for('logout'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    # app.run()
