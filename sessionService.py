import time
from random import random

from sessionModels import BlockedUser, SessionInfo
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class SessionService:
    def __init__(self):
        DB_URL = 'sqlite:///myBank.db'
        engine = create_engine(DB_URL, echo=False)
        Session = sessionmaker(bind=engine)
        self.session = Session()
        pass

    def block_user(self, client_number, blocking_time):
        block = BlockedUser(client_number=client_number, time=time.time()+blocking_time)
        print('hello from block user ', client_number)
        self.session.add(block)
        self.session.commit()

    def unlock_blocked_users(self):
        current_time = time.time()
        expired_users = self.session.query(BlockedUser).filter(BlockedUser.time < current_time).all()
        for user in expired_users:
            self.session.delete(user)
            self.session.commit()


    def is_user_blocked(self, client_number):
        block = self.session.query(BlockedUser).filter(BlockedUser.client_number == client_number).first()
        if block:
            return block.time
        return False

    def add_session(self, session_id):
        ses = SessionInfo()
        ses.session_id = session_id
        self.session.add(ses)
        self.session.commit()

    def get_client_from_session(self, session_id):
        usr = self.session.query(SessionInfo).filter(SessionInfo.session_id == session_id).first()
        if usr:
            if usr.client_number:
                return usr.client_number
            return -2
        return -1

    def add_client_to_session(self, session_id, client_nr):
        usr = self.session.query(SessionInfo).filter(SessionInfo.session_id == session_id).first()
        if usr:
            usr.client_number = client_nr
            print(usr.session_id, usr.client_number)
            self.session.commit()
            return 1
        return -1

    def get_set_from_session(self, session_id):
        usr = self.session.query(SessionInfo).filter(SessionInfo.session_id == session_id).first()
        if usr:
            if usr.set:
                return usr.set
            return -2
        return -1

    def set_set_to_session(self, session_id, set_num):
        usr = self.session.query(SessionInfo).filter(SessionInfo.session_id == session_id).first()
        if usr:
            usr.set = set_num
            self.session.commit()
        return -1

    def logout_inactive_users(self):
        logout_usr = self.session.query(SessionInfo).filter(SessionInfo.time+60 < time.time()).all()
        for user in logout_usr:
            user.client_number = None
            user.is_login = False
            user.time = time.time() + 3600


    def login_user_in_session(self, session_id, client_number):
        usr = self.session.query(SessionInfo).filter(SessionInfo.session_id == session_id).first()
        if not usr:
            usr = SessionInfo(session_id=session_id)
        usr.client_number = client_number

    def change_session_id(self, session_id, new):
        usr = self.session.query(SessionInfo).filter(SessionInfo.session_id == session_id).first()
        usr.session_id = new
        self.session.commit()

    def is_session_in_info(self, session_id):
        usr = self.session.query(SessionInfo).filter(SessionInfo.session_id == session_id).first()
        if usr:
            return True
        return False

    def set_attempts_in_session(self, session_id, attempts):
        usr = self.session.query(SessionInfo).filter(SessionInfo.session_id == session_id).first()
        if usr:
            usr.attempts = attempts
        return -1

    def get_attempts_in_session(self, session_id):
        usr = self.session.query(SessionInfo).filter(SessionInfo.session_id == session_id).first()
        if usr:
            return usr.attempts
        return -1

    def is_client_login(self, client_number):
        usr = self.session.query(SessionInfo).filter(SessionInfo.client_number == client_number).all()
        for user in usr:
            if user.is_login:
                return True
        return False

    def update_time_in_client(self, client_number, time_step):
        usr = self.session.query(SessionInfo).filter(SessionInfo.client_number == client_number).first()
        if usr:
            usr.time = time_step
            self.session.commit()
            return 1
        return -1

    def set_transaction_to_client(self, client_number, transaction):
        usr = self.session.query(SessionInfo).filter(SessionInfo.client_number == client_number).first()
        if usr:
            usr.transfer_data = transaction
            self.session.commit()
            return 1
        return -1

    def pop_transaction_from_client(self, client_number):
        usr = self.session.query(SessionInfo).filter(SessionInfo.client_number == client_number).first()
        if usr:
            tmp = usr.transfer_data
            usr.transfer_data = None
            self.session.commit()
            return tmp
        return -1

    def set_error_to_client(self, client, error):
        usr = self.session.query(SessionInfo).filter(SessionInfo.client_number == client).first()
        if usr:
            usr.error = error
            self.session.commit()
            return 1
        return -1

    def pop_error_from_client(self, client):
        usr = self.session.query(SessionInfo).filter(SessionInfo.client_number == client).first()
        if usr:
            tmp = usr.error
            usr.error = None
            self.session.commit()
            return tmp
        return -1

    def change_is_login_in_session(self, session_id, bol):
        usr = self.session.query(SessionInfo).filter(SessionInfo.session_id == session_id).first()
        usr.is_login = bol

    def is_session_login(self, session_id):
        usr = self.session.query(SessionInfo).filter(SessionInfo.session_id == session_id).first()
        if usr.is_login:
            return True
        return False

    def clear_session(self):
        self.session.query(BlockedUser).delete()
        self.session.query(SessionInfo).delete()
        self.session.commit()

