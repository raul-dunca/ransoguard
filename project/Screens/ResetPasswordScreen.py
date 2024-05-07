import os
import secrets
import smtplib
import ssl
import string
import threading

from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi
from dotenv import load_dotenv

from Screens.Utilities import show_information_message


class ResetPasswordScreen(QDialog):
    def __init__(self, widget, database, hasher):
        super(ResetPasswordScreen, self).__init__()
        loadUi("reset_password.ui", self)
        self.widget = widget
        self.database=database
        self.hasher=hasher
        self.init_buttons()

    def init_buttons(self):
        self.reset_button.clicked.connect(self.when_clicked)
        self.backButton.clicked.connect(self.go_to_sign_in)

    def when_clicked(self):
        threading.Thread(target=self.send_email).start()
        show_information_message("Your password has been reset. Please check your email for further instructions.")
        self.go_to_sign_in()

    def generate_random_password(self, length):
        characters = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(secrets.choice(characters) for _ in range(length))
        return password

    def go_to_sign_in(self):
        self.widget.removeWidget(self)
        self.widget.setCurrentIndex(0)

    def send_email(self):
        email=self.email_field.text()
        result=self.database.execute_query('SELECT is_active FROM users WHERE email=%s', (email,))
        if len(result)>0:
            is_active=result[0][0]
            if is_active:

                temporary_password=self.generate_random_password(8)
                hashed_password = self.hasher.hash(temporary_password)
                self.database.execute_query('UPDATE users SET password = %s WHERE email=%s', (hashed_password,email))
                activation_message = f'''Subject: RansoGuard Password Reset
Dear user,
        
Your password has been successfully reset. Please find your temporary password below:
        
Temporary Password: {temporary_password}
        
For security reasons, we recommend changing your password after logging in.
        
If you did not request this password reset, please contact us immediately.
        
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
                    server.sendmail(sender, email, activation_message)
