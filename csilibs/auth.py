import sys, os, platform, json, subprocess

from PySide2.QtWidgets import (
    QApplication,  QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QDialog
)

import hashlib
import base64
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from utils import pathme

class PasswordInputDialog(QDialog):
    def __init__(self, max_attempts=3, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Password Input')
        self.max_attempts = max_attempts
        self.attempts = 0

        layout = QVBoxLayout()

        self.password_label = QLabel(f'Enter your sudo password (Attempts remaining: {max_attempts})')
        layout.addWidget(self.password_label)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.submit_button = QPushButton('Submit')
        self.submit_button.clicked.connect(self.on_submit)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def on_submit(self):
        self.password = self.password_input.text()
        self.attempts += 1
        self.password_input.setText('')
        self.password_label.setText(f'Enter your sudo password (Attempt: {self.attempts}/{self.max_attempts})')
        self.accept()  # Close the dialog and return the entered password

def checkpass():
    password = ""

    command = ["sudo", "-S", "-v"]    # just to check sudo password requires or not
    requires_pass = subprocess.run(command,input=password.encode()).returncode  # checks without supplying password
    if requires_pass == 0:
        return 0

    no_of_attempts = 3
    attempted = 0

    app = QApplication.instance() or QApplication([])
    while requires_pass and attempted < no_of_attempts:
        dialog = PasswordInputDialog(max_attempts=no_of_attempts - attempted)
        if dialog.exec_():
            password = dialog.password

            command = ["sudo", "-S", "-v"]
            try:
                subprocess.run(command, input=password.encode(), check=True)
                return password  # Return the password if the sudo token validation was successful
            except subprocess.CalledProcessError:
                attempted += 1
                continue

    return ""


#------------------------- APIKeys encryption methods --------------------------------------------#


def gen_key(password=0):     # generate key for Fernet() using password.
    # genKey doesn't stores key for a better security, generates it at runtime.   
    if password == 0:
        password = input("Enter Password: ").encode()
    else:
        password = password.encode()
    salt=b"Just4FillingTheRequirementOfPBKDF2HMAC"  
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000
    )
    derived=kdf.derive(password)
    key = base64.urlsafe_b64encode(derived)
    return key

# Conditional path assigning for APIkeys due to removal of path it can work with pathme
if os.path.exists('data/APIKeys.json') or os.path.exists('data/APIKeys.enc'):
    api_json_path = 'data/APIKeys.json'
    api_enc_path = 'data/APIKeys.enc'
else:
    api_json_path = pathme("data/APIKeys.json")
    api_enc_path = pathme("data/APIKeys.enc")

def encrypt(key):
    f = Fernet(key)

    # encrypting APIKeys.json
    with open(api_json_path, 'rb') as plain_file:
        plain_data = plain_file.read()
    
    encrypted_data = f.encrypt(plain_data)

    with open(api_enc_path, 'wb') as encrypted_file:
        encrypted_file.write(encrypted_data)

    # Removing plaintext data file
    os.remove(api_json_path)
    
    return True

def decrypt(key):
    f = Fernet(key)

    try:
        # Decrypting APIKeys.enc
        with open(api_enc_path, 'rb') as encrypted_file:
            encrypted_data = encrypted_file.read()
        
        plain_data = f.decrypt(encrypted_data)

        with open(api_json_path, 'wb') as plain_file:
            plain_file.write(plain_data)
    
        return True
    
    except InvalidToken:
        print("Invalid Password to Decrypt")
        return False



def gen_md5(file_path):
    md5_hash = hashlib.md5()
    with open(file_path, 'rb') as file:
        # Read the file in chunks to handle large files efficiently
        for chunk in iter(lambda: file.read(4096), b''):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()
    