

class SessionClass:
    client_number = None
    set = None
    attempts = None
    transfer_date = {}
    error = None

    def clean(self):
        self.client_number = None
        self.attempts = None
        self.transfer_date = None
        self.error = None