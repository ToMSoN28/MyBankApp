import re

import bleach


class ValidationService:

    def sanitize_input(self, input_str):
        cleaned_input = bleach.clean(input_str, tags=[], attributes={}, strip=True)
        return cleaned_input

    def prevent_sql_injection(self, input_str):
        if re.match(r'^[\w\s.,!?@#&()\[\]{}%\-_+=*<>:;"\'+/|\\]*$', input_str):
            return True
        else:
            return False

    def client_number_valid(self, client_number):
        try:
            liczba = int(client_number)

            if len(client_number) == 8:
                return True
            else:
                return False
        except ValueError:
            return False

    def password_char_input_valid(self, single_char):
        if len(single_char) == 1:
            return True
        else:
            return False

    def transaction_amount_value_valid(self, amount, balance):
        try:
            float_value = float(amount)
            pattern = r'^\d+(\.\d{1,2})?$'
            if float_value > 0 and balance-float_value > 0 and re.match(pattern, amount):
                return True
            else:
                return False
        except ValueError:
            return False

    def transaction_title_valid(self, title):
        title = self.sanitize_input(title)
        return self.prevent_sql_injection(title)


    def transaction_recipient_account_number_valid(self, account_number):
        try:
            liczba = int(account_number)

            if len(account_number) == 12:
                return True
            else:
                return False
        except ValueError:
            return False

    def transaction_recipient_name_valid(self, name):
        name = self.sanitize_input(name)
        return self.prevent_sql_injection(name)

    def password_valid(self, password):
        return self.prevent_sql_injection(password)