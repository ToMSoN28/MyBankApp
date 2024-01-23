import json

# from db_models import User, Transaction, Base
from sessionModels import Base, BlockedUser, SessionInfo
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from transferService import TransferService
from datetime import datetime
from passwordAlgorithm import PasswordAlgorithm
from cipherAlgorithm import CipherAlgorithm

DB_URL = 'sqlite:///myBank.db'

engine = create_engine(DB_URL, echo=True)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# user1 = User(name="Tomasz",
#              client_number=12341234,
#              account_number=432112344321,
#              balance=1000)
#
# user2 = User(name="Piotr",
#              client_number=45674567,
#              account_number=765445677654,
#              balance=1000)

# userTomasz = session.query(User).filter(User.id == 1).first()
# passwordAlgorithm = PasswordAlgorithm()
# hash, char_table, char_hash = passwordAlgorithm.change_password("0123456789")
# userTomasz.password_hash = hash
# userTomasz.password_char_table = json.dumps(char_table)
# userTomasz.password_char_hash = json.dumps(char_hash)
# session.commit()
# cipherAlgorithm = CipherAlgorithm()
# pesel = '01252149547'
# cipher_pesel, tag_pesel = cipherAlgorithm.encrypt_aes_gcm(pesel.encode())
# ccv = '213'
# cipher_ccv, tag_ccv = cipherAlgorithm.encrypt_aes_gcm(ccv.encode())
#
# userTomasz.pesel_info = cipher_pesel
# userTomasz.pesel_tag = tag_pesel
# userTomasz.ccv_info = cipher_ccv
# userTomasz.ccv_tag = tag_ccv

# userTomasz = session.query(User).filter(User.id == 1).first()
# userPiotr = session.query(User).filter(User.id == 2).first()

# transaction_form_T = Transaction(from_account_number=userTomasz.account_number,
#                           from_name=userTomasz.name,
#                           date=datetime.now(),
#                           amount=-100,
#                           title='Test',
#                           to_account_number=userPiotr.account_number,
#                           to_name=userPiotr.name
#                           )
# userTomasz.balance = userTomasz.balance-100
# transaction_to_P = Transaction(from_account_number=userTomasz.account_number,
#                           from_name=userTomasz.name,
#                           date=datetime.now(),
#                           amount=100,
#                           title='Test',
#                           to_account_number=userPiotr.account_number,
#                           to_name=userPiotr.name
#                           )
# userPiotr.balance = userPiotr.balance+100

# tr1 = session.query(Transaction).filter(Transaction.id == 1).first()
# tr2 = session.query(Transaction).filter(Transaction.id == 2).first()
#
# userTomasz.transactions.append(tr1)
# userPiotr.transactions.append(tr2)
#
# session.commit()


# Wyświetlenie listy transakcji dla danego użytkownika
# for transaction in userTomasz.transactions:
#     print(f"Transaction ID: {transaction.id}, Amount: {transaction.amount}, Date: {transaction.date}")


