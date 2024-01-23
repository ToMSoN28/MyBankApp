import math
import random
import re
import time

from passlib.hash import argon2
import os, json


class PasswordAlgorithm:

    def generate_combination(self, passwd_len):
        combination = []

        while len(combination) < 10:
            chars_num = random.sample(range(passwd_len), 4)
            chars_num.sort()

            if chars_num not in combination:
                combination.append(chars_num)

        return combination

    def change_password(self, password):
        passwd = password
        passwd_len = len(passwd)

        passwd_salt = os.urandom(16).hex()
        start = time.time()
        passwd_hash = argon2.using(rounds=32, salt=passwd_salt.encode()).hash(passwd)
        print(time.time()-start)
        print(passwd_salt, passwd_hash)

        passwd_char_table = self.generate_combination(passwd_len)
        print(passwd_char_table)
        passwd_char_hash = []
        for j, char_table in enumerate(passwd_char_table):
            tmp = ""

            for i in char_table:
                tmp += passwd[i]

            salt = os.urandom(16).hex()
            hash = argon2.using(rounds=32, salt=salt.encode()).hash(tmp)
            passwd_char_hash.append(hash)
            # print(char_table, tmp, salt, hash)
        # print(passwd_char_hash)
        print(json.dumps(passwd_char_hash))

        return passwd_hash, passwd_char_table, passwd_char_hash

    def verify_password(self, input_passwd, expected_hash):
        verified = argon2.verify(input_passwd, expected_hash)
        if verified:
            print("+")
            return True
        else:
            print("-")
            return False

    def calculate_entropy(self, password):
        stat = {}
        leng = 0

        # Usuwamy białe znaki z hasła
        password = re.sub(r'\s', '', password)

        for znak in password:
            leng += 1
            if znak in stat:
                stat[znak] += 1
            else:
                stat[znak] = 1

        H = 0.0
        for znak in stat:
            # print("{} <=> {}".format(znak, stat[znak]))
            p_i = stat[znak] / leng
            H -= p_i * math.log2(p_i)
        # print(H)
        return H

    def is_strong_password(self, password):
        if len(password) < 8:
            return False
        if not re.search(r'[A-Z]', password):
            return False
        if not re.search(r'[a-z]', password):
            return False
        if not re.search(r'\d', password):
            return False
        if not re.search(r'[^a-zA-Z\d]', password):
            return False
        if self.calculate_entropy(password) < 3:
            return False
        with open("commonPasswords.txt", "r") as file:
            common_passwords = [line.strip() for line in file]
        if password in common_passwords:
            return False

        return True



if __name__ == "__main__":
    alg = PasswordAlgorithm()
    # alg.change_password("123456789")
    # alg.verify_password("1249", "$argon2id$v=19$m=65536,t=12,p=4$M2NmMDExYWU3ZDIzNzlhZTUxZThiMzlhNjg4OTE5ZWQ$ryegTLaz3r0K3N00YUkxZIlkW8VDBw5/B48yN83m9pw")
    if alg.is_strong_password('P@ssw0rd'):
        print('strong')
    else:
        print('week')
    # print(os.urandom(16))
    # print(os.urandom(16).hex())
