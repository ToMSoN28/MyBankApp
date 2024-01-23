import json
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
from sessionService import SessionService
from sessionClass import SessionClass

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SESSION_KEY")
app.config['SESSION_COOKIE_HTTPONLY'] = True  # JS can not use session cookie
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'

blocking_time = 120
# max_inactivity_time = 60  # Time in seconds (3 min) = 180
# blocked_users = {}
# logged_in_users = {}
# session_info = {}

routes = ['/login', '/password', '/logout', '/my-account', '/transaction', '/confirm-transaction', '/secret-info', '/change-password']

valid = ValidationService()
sessionService = SessionService()
sessionService.clear_session()


def is_user_blocked(client_number):
    return sessionService.is_user_blocked(client_number)


def login_user_in_session(client_number):
    session_id = session.get('session_id')
    if session_id:
        old_client = sessionService.get_client_from_session(session_id)
        sessionService.add_client_to_session(session_id, client_number)
        sessionService.change_is_login_in_session(session_id, False)
        if old_client == sessionService.get_client_from_session(session_id):
            return sessionService.get_attempts_in_session(session_id)
        else:
            return 0
    else:
        unique_string = f"{request.remote_addr}{secrets.token_hex(16)}"
        session['session_id'] = unique_string
        sessionService.add_session(unique_string)
        sessionService.add_client_to_session(unique_string, client_number)
        return 0

def change_session_id():
    session_id = session.get('session_id')
    while True:
        unique_string = f"{request.remote_addr}{secrets.token_hex(16)}"
        if session_id != unique_string and not sessionService.is_session_in_info(unique_string):
            break
    sessionService.change_session_id(session_id, unique_string)
    session['session_id'] = unique_string


def set_new_session_set(set_num):
    while True:
        tmp = random.randint(0, 9)
        if not tmp == set_num:
            return tmp


def session_set(session_id):
    tmp = sessionService.get_set_from_session(session_id)
    if tmp == -2:
        sessionService.set_set_to_session(session_id, random.randint(0, 9))
    return True

# Middleware do sprawdzania blokad
@app.before_request
def before_every_request():
    sessionService.logout_inactive_users()
    sessionService.unlock_blocked_users()
    session.permanent = True
    app.permanent_session_lifetime = timedelta(seconds=3600)
    if request.path not in routes and not request.path.endswith('favicon.ico'):
        return redirect(url_for('login'))

    session_id = session.get('session_id')
    if session_id:
        if not valid.prevent_sql_injection(session_id):
            session.pop('session_id', None)
            return redirect(url_for('login'))
        ip_address = session_id[:-32]
        if not sessionService.is_session_in_info(session_id) or request.remote_addr != ip_address:
            session.pop('session_id', None)
            return redirect(url_for('login'))
        change_session_id()
        session_id = session.get('session_id')
        if request.path == '/login':
            return
        client_number = sessionService.get_client_from_session(session_id)
        if client_number > 0:
            time_block = sessionService.is_user_blocked(client_number)
            if time_block:
                sessionService.set_attempts_in_session(session_id, 0)
                return render_template('login.html',
                                       error=f'User {client_number} is blocked for {int(time_block - time.time())} s')


# Strona logowania - wprowadzenie identyfikatora klienta
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        client_number = request.form.get('user_id')
        client_number = valid.sanitize_input(client_number)  # sanitize client number
        if valid.client_number_valid(client_number):

            time_block = sessionService.is_user_blocked(client_number)
            if time_block:
                return render_template('login.html',
                                       error=f'User {client_number} is blocked for {int(time_block - time.time())} s')

            if sessionService.is_client_login(client_number):
                return render_template('login.html', error=f'User {client_number} is currently logged in')

            att = login_user_in_session(client_number)
            session_id = session.get('session_id')
            session_set(session_id)
            sessionService.set_attempts_in_session(session_id, att)

            return redirect(url_for('password'))
        else:
            return render_template('login.html')

    session_id = session.get('session_id')
    if session_id:
        sessionService.change_is_login_in_session(session_id, False)
    return render_template('login.html')


# Strona logowania - wprowadzenie hasła
@app.route('/password', methods=['GET', 'POST'])
def password():
    session_id = session.get('session_id')
    client_number = sessionService.get_client_from_session(session_id)
    set_char = sessionService.get_set_from_session(session_id)
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
        if valid.password_char_input_valid(first) and valid.password_char_input_valid(
                second) and valid.password_char_input_valid(third) and valid.password_char_input_valid(fourth):
            password = first + second + third + fourth

            if accountService.verify_password_char(password):
                sessionService.update_time_in_client(client_number, time.time())
                sessionService.set_set_to_session(session_id, set_new_session_set(set_char))  # new set of password char chosen
                sessionService.change_is_login_in_session(session_id, True)
                return redirect(url_for('my_account'))

        attempts = sessionService.get_attempts_in_session(session_id)
        attempts += 1
        sessionService.set_attempts_in_session(session_id, attempts)
        if attempts >= 3:
            sessionService.block_user(client_number, blocking_time)
            return redirect(url_for('login'))

        return render_template('password.html', error='Incorrect login or password.',
                               attempts=3 - attempts,
                               first=char_table[0] + 1,
                               second=char_table[1] + 1,
                               third=char_table[2] + 1,
                               fourth=char_table[3] + 1,
                               client_number=client_number)

    session_id = session.get('session_id')
    sessionService.change_is_login_in_session(session_id, False)
    return render_template('password.html',
                           first=char_table[0] + 1,
                           second=char_table[1] + 1,
                           third=char_table[2] + 1,
                           fourth=char_table[3] + 1,
                           client_number=client_number)


@app.route('/logout', methods=['GET'])
def logout():
    session_id = session.get('session_id')
    client_number = sessionService.get_client_from_session(session_id)
    if sessionService.is_client_login(client_number):
        sessionService.add_client_to_session(session_id, None)
        sessionService.change_is_login_in_session(session_id, False)
    # session_info[session_id].clean()
    # session.pop('session_id', None)
    return redirect(url_for('login'))


@app.route('/my-account', methods=['GET'])
def my_account():
    session_id = session.get('session_id')
    client_number = sessionService.get_client_from_session(session_id)
    if client_number < 1 or not sessionService.is_session_login(session_id):
        return redirect(url_for('login'))
    sessionService.update_time_in_client(client_number, time.time())
    accountService = AccountService(client_number)
    name = accountService.user.name
    account_number = accountService.user.account_number
    balance = accountService.user.balance
    transactions = accountService.show_transfer_list()

    return render_template('myAccount.html', name=name, account_number=account_number,
                           balance=balance, transactions=transactions)


@app.route('/transaction', methods=['GET', 'POST'])
def transaction():
    session_id = session.get('session_id')
    client_number = sessionService.get_client_from_session(session_id)
    if client_number < 1 or not sessionService.is_session_login(session_id):
        return redirect(url_for('login'))
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
        if accountService.user.account_number == int(to_account_number):
            error += 'You can not send money yourself. '
        # print(type(accountService.user.account_number), type(to_account_number))
        if error != "":
            return render_template('transaction.html', error=error)
        transaction = {
            'amount': amount,
            'title': title,
            'to_account_number': to_account_number,
            'to_name': to_name
        }
        sessionService.set_transaction_to_client(client_number, transaction)
        return redirect(url_for('confirm_transaction'))

    sessionService.update_time_in_client(client_number, time.time())
    error_code = sessionService.pop_error_from_client(client_number)
    if error_code:
        sessionService.set_error_to_client(client_number, None)
        return render_template('transaction.html', error=error_code)
    return render_template('transaction.html')


@app.route('/confirm-transaction', methods=['GET', 'POST'])
def confirm_transaction():
    session_id = session.get('session_id')
    client_number = sessionService.get_client_from_session(session_id)
    if client_number < 1 or not sessionService.is_session_login(session_id):
        return redirect(url_for('login'))
    if request.method == 'POST':
        accountService = AccountService(client_number)
        password = request.form.get('password')
        if accountService.verify_password(password) and valid.password_valid(password):
            transaction_data = sessionService.pop_transaction_from_client(client_number)
            if not transaction_data:
                return render_template('transaction.html', error='Server error, try again')
            tr = accountService.money_transfer(float(transaction_data['amount']),
                                               transaction_data['title'],
                                               transaction_data['to_account_number'],
                                               transaction_data['to_name'])
            if tr == 1:
                return redirect(url_for('my_account'))
            elif tr == 0:
                sessionService.set_error_to_client(client_number,
                                                   'Not enough money in your account to execute transaction')
                return redirect(url_for('transaction'))
            else:
                sessionService.set_error_to_client(client_number, 'Bad recipient information')
                return redirect(url_for('transaction'))
        else:
            sessionService.set_error_to_client(client_number, 'Incorrect password')
            return redirect(url_for('transaction'))

    sessionService.update_time_in_client(client_number, time.time())
    return render_template('confirmTransaction.html')


@app.route('/secret-info', methods=['GET'])
def secret_info():
    session_id = session.get('session_id')
    client_number = sessionService.get_client_from_session(session_id)
    if client_number < 1 or not sessionService.is_session_login(session_id):
        return redirect(url_for('login'))
    sessionService.update_time_in_client(client_number, time.time())
    accountService = AccountService(client_number)
    pesel, ccv = accountService.show_secure_info()
    return render_template('secretInfo.html', pesel=pesel.decode(), ccv=ccv.decode())


@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
    session_id = session.get('session_id')
    client_number = sessionService.get_client_from_session(session_id)
    if client_number < 1 or not sessionService.is_session_login(session_id):
        return redirect(url_for('login'))
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

    sessionService.update_time_in_client(client_number, time.time())
    return render_template('changePassword.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    # app.run()
