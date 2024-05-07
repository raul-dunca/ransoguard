import re


from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets

from Screens.ActivationScreen import ActivationScreen
from Screens.Utilities import show_warning_message, show_information_message


class SignUpScreen(QDialog):    #Register
    def __init__(self, widget, database, hasher):
        super(SignUpScreen, self).__init__()
        loadUi("sign_up.ui", self)
        self.widget=widget
        self.database=database
        self.hasher = hasher
        self.init_buttons()

    def init_buttons(self):
        self.sign_in_button.clicked.connect(self.go_to_sign_in)
        self.sign_up_button.clicked.connect(self.sign_up)

    def go_to_activation_page(self,email):
        activation=ActivationScreen(self.widget, email, self.database)
        self.widget.addWidget(activation)
        self.widget.setCurrentWidget(activation)

        self.email_field.clear()
        self.username_field.clear()
        self.password_field.clear()
        self.confirm_password_field.clear()
        self.checkBox.setChecked(False)

    def go_to_sign_in(self):
        self.widget.setCurrentIndex(0)
        self.email_field.clear()
        self.username_field.clear()
        self.password_field.clear()
        self.confirm_password_field.clear()
        self.checkBox.setChecked(False)

    def sign_up(self):
        email = self.email_field.text()
        username = self.username_field.text()
        password = self.password_field.text()
        confirm_password = self.confirm_password_field.text()

        if self.validate_email(email) and self.validate_username(username) and self.validate_password(password) and self.check_passwords_match(password, confirm_password):
            if self.does_user_exists(email):
                show_warning_message("This email is already associated with an account !")
            else:
                self.create_user(email,username,password)
                show_information_message("Your account was created successfully !")
                self.go_to_activation_page(email)

    def does_user_exists(self,email):
        if len(self.database.execute_query('SELECT * FROM users WHERE email=%s', (email,))) > 0:
            return True
        return False

    def create_user(self, email, username, password):
        hashed_password = self.hasher.hash(password)
        self.database.execute_query('INSERT INTO users(email, username, password, is_active) VALUES (%s,%s,%s,false)', (email, username, hashed_password))

    def validate_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if bool(re.match(pattern, email)):
            return True
        else:
            show_warning_message("Invalid email !")
            return False

    def validate_username(self, username):
        if len(username)<4:
            show_warning_message("Username needs to have at leas 4 characters !")
            return False
        elif len(username)>200:
            show_warning_message("Username can't be longer than 200 characters !")
            return False
        elif len(self.database.execute_query('SELECT * FROM users WHERE username=%s', (username,))) > 0:
            show_warning_message("Username already taken !")
            return False
        else:
            return True

    def validate_password(self, password):
        if len(password) < 8:
            show_warning_message("Password needs to have at leas 8 characters !")
            return False
        elif len(password) > 200:
            show_warning_message("Password can't be longer than 200 characters !")
            return False
        elif not self.check_upper_and_lower(password):
            show_warning_message("Include both lower and upper case characters !")
            return False
        elif not bool(re.search(r'\d', password)):
            show_warning_message("Include at least one number !")
            return False
        elif not bool(re.search(r'[^\w\s]', password)):
            show_warning_message("Include at least one symbol !")
            return False
        else:
            return True

    def check_passwords_match(self, password, confirm_password):
        if password == confirm_password:
            return True
        else:
            show_warning_message("The password and password confirmation do not match !")
            return False

    def check_upper_and_lower(self, password):
        upper = False
        lower = False
        for char in password:
            if char.isalpha():
                if char.islower():
                    lower = True
                else:
                    upper = True
        return lower and upper


    def on_checkBox_clicked(self):
        if self.checkBox.isChecked():
            self.password_field.setEchoMode(QtWidgets.QLineEdit.Normal)
            self.confirm_password_field.setEchoMode(QtWidgets.QLineEdit.Normal)
        else:
            self.password_field.setEchoMode(QtWidgets.QLineEdit.Password)
            self.confirm_password_field.setEchoMode(QtWidgets.QLineEdit.Password)
