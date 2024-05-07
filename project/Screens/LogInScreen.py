import argon2
from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets

from Screens.ResetPasswordScreen import ResetPasswordScreen
from Screens.Utilities import show_warning_message, show_error_message


class SignInScreen(QDialog):  # Login
    def __init__(self, widget, database, hasher):
        super(SignInScreen, self).__init__()
        loadUi("welcome.ui", self)
        self.widget = widget
        self.database = database
        self.hasher = hasher
        self.init_buttons()

    def init_buttons(self):
        self.sign_up_button.clicked.connect(self.go_to_sign_up)
        self.sign_in_button.clicked.connect(self.sign_in)
        self.reset_pass_button.clicked.connect(self.go_to_reset_password)

    def go_to_sign_up(self):
        self.widget.setCurrentIndex(1)
        self.username_field.clear()
        self.password_field.clear()
        self.checkBox.setChecked(False)

    def go_to_main(self):
        self.widget.setCurrentIndex(2)
        self.username_field.clear()
        self.password_field.clear()
        self.checkBox.setChecked(False)

    def go_to_reset_password(self):
        reset = ResetPasswordScreen(self.widget, self.database, self.hasher)
        self.widget.addWidget(reset)
        self.widget.setCurrentWidget(reset)
        self.username_field.clear()
        self.password_field.clear()
        self.checkBox.setChecked(False)

    def sign_in(self):
        username = self.username_field.text()
        password = self.password_field.text()

        if self.validate_username(username) and self.validate_password(password):
            if self.check_for_user(username, password):
                self.go_to_main()

    def check_for_user(self, username, password):
        result = self.database.execute_query('SELECT password,is_active FROM users WHERE username=%s', (username,))
        if len(result)>0:
            db_password=result[0][0]
            db_is_active=result[0][1]
            is_password_matched=False
            try:
                is_password_matched = self.hasher.verify(db_password, password)
            except argon2.exceptions.VerifyMismatchError as e:
                print(e)
            if is_password_matched:
                if db_is_active:
                    return True
                show_error_message("This account is not yet active. Please check your email to activate it !")
                return False
            show_error_message("Invalid username and password combination !")
            return False
        else:
            show_error_message("Invalid username and password combination !")
            return False

    def validate_username(self, username):
        if len(username) > 200:
            show_warning_message("Username can't be longer than 200 characters !")
            return False
        elif len(username) == 0:
            show_warning_message("Username field can't be empty !")
            return False
        else:
            return True

    def validate_password(self, password):
        if len(password) > 200:
            show_warning_message("Password can't be longer than 200 characters !")
            return False
        elif len(password) == 0:
            show_warning_message("Password field can't be empty !")
        else:
            return True

    def on_checkBox_clicked(self):
        if self.checkBox.isChecked():
            self.password_field.setEchoMode(QtWidgets.QLineEdit.Normal)
        else:
            self.password_field.setEchoMode(QtWidgets.QLineEdit.Password)
