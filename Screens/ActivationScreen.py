import os
import secrets
import smtplib
import ssl
import threading

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi
from dotenv import load_dotenv

from Screens.Utilities import show_information_message, show_error_message


class ActivationScreen(QDialog):
    initialization_complete = pyqtSignal()
    def __init__(self, widget, email, database):
        super(ActivationScreen, self).__init__()
        loadUi("activate_account.ui", self)
        self.widget = widget
        self.email = email
        self.database = database
        self.activate_button.clicked.connect(self.check_code)
        threading.Thread(target=self.send_email).start()

    def go_to_sign_in(self):
        self.widget.removeWidget(self)
        self.widget.setCurrentIndex(0)

    def check_code(self):
        user_code = self.activ_code_field.text()
        result=self.database.execute_query('SELECT code FROM users WHERE email=%s', (self.email,))
        if len(result) > 0:
            actual_code = result[0][0]
            if user_code==actual_code:
                self.database.execute_query('UPDATE users SET code = NULL, is_active = TRUE WHERE email=%s',  (self.email,))
                show_information_message("Account activated successfully !")
                self.go_to_sign_in()
                return

        show_error_message("The code is incorrect !")

    def generate_activation_code(self, length):
        return ''.join(secrets.choice('0123456789') for _ in range(length))

    def send_email(self):
        activation_code = self.generate_activation_code(6)
        self.database.execute_query('UPDATE users SET code = %s WHERE email=%s', (activation_code, self.email))
        activation_message = f'''Subject: RansoGuard Activation Code
Dear user,

Thank you for registering. Your activation code is: {activation_code}

Please use this code to activate your account.

Best regards,
RansoGuard
'''

        load_dotenv()
        port = os.environ.get("EMAIL_PORT")
        smtp_server = os.environ.get("EMAIL_SMTP_SERV")
        sender = os.environ.get("EMAIL_SENDER")
        password = os.environ.get("EMAIL_PASS")

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender, password)
            server.sendmail(sender, self.email, activation_message)

        #self.initialization_complete.emit()
