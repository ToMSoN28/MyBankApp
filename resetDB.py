import json

from db_models import User, Transaction, Base
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

userTomasz = session.query(User).filter(User.id == 1).first()
userTomasz.name = 'Tomasz'
userTomasz.client_number = 12341234
userTomasz.account_number = 432112344321
userTomasz.balance = 1000

passwordAlgorithm = PasswordAlgorithm()
hash, char_table, char_hash = passwordAlgorithm.change_password("1234567890")
userTomasz.password_hash = hash
userTomasz.password_char_table = json.dumps(char_table)
userTomasz.password_char_hash = json.dumps(char_hash)

cipherAlgorithm = CipherAlgorithm()
pesel = '98053150056'
cipher_pesel, tag_pesel = cipherAlgorithm.encrypt_aes_gcm(pesel.encode())
ccv = '007'
cipher_ccv, tag_ccv = cipherAlgorithm.encrypt_aes_gcm(ccv.encode())
userTomasz.pesel_info = cipher_pesel
userTomasz.pesel_tag = tag_pesel
userTomasz.ccv_info = cipher_ccv
userTomasz.ccv_tag = tag_ccv

for transaction in userTomasz.transactions:
    session.delete(transaction)

# #######################

userPiotr = session.query(User).filter(User.id == 2).first()
userPiotr.name = 'Piotr'
userPiotr.client_number = 45674567
userPiotr.account_number = 765445677654
userPiotr.balance = 1000

passwordAlgorithm = PasswordAlgorithm()
hash, char_table, char_hash = passwordAlgorithm.change_password("1234567890")
userPiotr.password_hash = hash
userPiotr.password_char_table = json.dumps(char_table)
userPiotr.password_char_hash = json.dumps(char_hash)

cipherAlgorithm = CipherAlgorithm()
pesel = '0123456789'
cipher_pesel, tag_pesel = cipherAlgorithm.encrypt_aes_gcm(pesel.encode())
ccv = '213'
cipher_ccv, tag_ccv = cipherAlgorithm.encrypt_aes_gcm(ccv.encode())
userPiotr.pesel_info = cipher_pesel
userPiotr.pesel_tag = tag_pesel
userPiotr.ccv_info = cipher_ccv
userPiotr.ccv_tag = tag_ccv

for transaction in userPiotr.transactions:
    session.delete(transaction)

session.commit()