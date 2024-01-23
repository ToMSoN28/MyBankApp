from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_models import User, Transaction


class TransferService:

    session = None
    user = None

    def __init__(self, client_number):
        DB_URL = 'sqlite:///myBank.db'
        engine = create_engine(DB_URL, echo=True)
        Session = sessionmaker(bind=engine)
        self.session = Session()
        self.user = self.session.query(User).filter(User.client_number == client_number).first()
        pass

    def money_transfer(self, amount, title, addressee_account_number):
        addressee_user = self.session.query(User).filter_by(account_number=addressee_account_number).first()
        if addressee_user:
            tr_from = Transaction(from_account_number=self.user.account_number,
                                    from_name=self.user.name,
                                    date=datetime.now(),
                                    amount=-amount,
                                    title=title,
                                    to_account_number=addressee_user.account_number,
                                    to_name=addressee_user.name
                                    )
            self.user.balance -= amount
            self.user.transactions.append(tr_from)
            tr_to = Transaction(from_account_number=self.user.account_number,
                                  from_name=self.user.name,
                                  date=datetime.now(),
                                  amount=amount,
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

    def show_transfer_list(self):
        translations = []
        for tr in self.user.transactions:
            translations.append(tr.transaction_to_dict())
        return translations

