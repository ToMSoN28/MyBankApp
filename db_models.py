from sqlalchemy import DateTime, BigInteger, Column, Integer, String, Sequence, Float, LargeBinary, Date, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    client_number = Column(Integer, unique=True)
    password_hash = Column(String)
    password_char_table = Column(String)  # json.dumps(array_data)
    password_char_hash = Column(String)  # json.loads(array_column)
    account_number = Column(BigInteger, unique=True)
    balance = Column(Float)
    pesel_info = Column(LargeBinary)
    pesel_tag = Column(LargeBinary)
    ccv_info = Column(LargeBinary)
    ccv_tag = Column(LargeBinary)

    transactions = relationship('Transaction', back_populates='user')


class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    from_account_number = Column(Integer)
    from_name = Column(String)
    date = Column(DateTime)
    amount = Column(Float)
    title = Column(String)
    to_account_number = Column(Integer)
    to_name = Column(String)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='transactions')

    def transaction_to_dict(self):
        return {
            'from_account_number': self.from_account_number,
            'from_name': self.from_name,
            'date': self.date,
            'amount': self.amount,
            'title': self.title,
            'to_account_number': self.to_account_number,
            'to_name': self.to_name
        }