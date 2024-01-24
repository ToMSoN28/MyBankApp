import json
import random
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_models import User, Transaction
from cipherAlgorithm import CipherAlgorithm
from passwordAlgorithm import PasswordAlgorithm


class AccountService:
    session = None
    user = None
    password_set_number = None
    login_attempts = 3

    cipher_fun = CipherAlgorithm()
    password_fun = PasswordAlgorithm()

    def __init__(self, client_number):
        DB_URL = 'sqlite:///myBank.db'
        engine = create_engine(DB_URL, echo=False)
        Session = sessionmaker(bind=engine)
        self.session = Session()
        self.user = self.session.query(User).filter(User.client_number == client_number).first()
        pass

    def change_password(self, password, new_password, new_password_confirmation):
        if new_password_confirmation == new_password:
            if password == new_password:
                return -3   # the same password
            is_strong = self.password_fun.is_strong_password(new_password)
            if is_strong:
                verified = self.password_fun.verify_password(password, self.user.password_hash)
                if verified:
                    hash, char_table, char_hash = self.password_fun.change_password(new_password)
                    self.user.password_hash = hash
                    self.user.password_char_table = json.dumps(char_table)
                    self.user.password_char_hash = json.dumps(char_hash)
                    self.session.commit()
                    return 1    # positive
                else:
                    return 0  # not verified old
            else:
                return -1  # week password
        else:
            return -2           # new != new_confirm

    def show_secure_info(self):
        pesel = self.cipher_fun.decrypt_aes_gcm(self.user.pesel_info, self.user.pesel_tag)
        ccv = self.cipher_fun.decrypt_aes_gcm(self.user.ccv_info, self.user.ccv_tag)
        return pesel, ccv

    def get_login_set(self):
        if self.user:
            password_sets = json.loads(self.user.password_char_table)
        else:
            password_sets = [[0, 4, 5, 7], [1, 6, 7, 8], [0, 2, 3, 4], [1, 2, 6, 8], [0, 1, 4, 8], [0, 3, 5, 6], [0, 1, 3, 8], [1, 2, 3, 5], [1, 2, 3, 8], [3, 4, 6, 7]]
        password_set = password_sets[self.password_set_number]
        return password_set

    def verify_password(self, password):
        if self.user:
            ps_hash = self.user.password_hash
            if self.password_fun.verify_password(password, ps_hash):
                return True
        return False

    def verify_password_char(self, password_char):
        if self.user:
            password_hash_sets = json.loads(self.user.password_char_hash)
            password_hash_set = password_hash_sets[self.password_set_number]
            verified = self.password_fun.verify_password(password_char, password_hash_set)
            if verified:
                return True    # successfully logging in
            else:
                self.login_attempts -= 1
                return False  # logging in failed
        else:
            self.login_attempts -= 1
            return False        # logging in failed

    def show_transfer_list(self):
        translations = []
        for tr in self.user.transactions:
            translations.insert(0, tr.transaction_to_dict())
        return translations

    def money_transfer(self, amount, title, addressee_account_number, addressee_name):
        if self.user.balance - amount < 0:
            return 0    # Not enough money in your account
        if self.user.account_number == addressee_account_number:
            return -1

        addressee_user = self.session.query(User).filter_by(account_number=addressee_account_number).first()
        if addressee_user:
            if addressee_user.name != addressee_name:
                return -1  # Bad addressee info

            _amount = round(amount, 2)
            tr_from = Transaction(from_account_number=self.user.account_number,
                                    from_name=self.user.name,
                                    date=datetime.now(),
                                    amount=-_amount,
                                    title=title,
                                    to_account_number=addressee_user.account_number,
                                    to_name=addressee_user.name
                                    )
            self.user.balance -= amount
            self.user.transactions.append(tr_from)
            tr_to = Transaction(from_account_number=self.user.account_number,
                                  from_name=self.user.name,
                                  date=datetime.now(),
                                  amount=_amount,
                                  title=title,
                                  to_account_number=addressee_user.account_number,
                                  to_name=addressee_user.name
                                  )
            addressee_user.balance += amount
            addressee_user.transactions.append(tr_to)

            self.session.add(tr_from)
            self.session.add(tr_to)
            self.session.commit()
            return 1        # Successful transfer
        else:
            return -1       # No account_number in bd

