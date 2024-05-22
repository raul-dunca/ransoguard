import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QWidget, QStackedWidget, QLabel, QLineEdit, QVBoxLayout, QMessageBox
import argon2

from Screens.ActivationScreen import ActivationScreen
from Screens.HistoryScreen import HistoryScreen
from Screens.LogInScreen import SignInScreen
from Screens.MainScreen import MainScreen
from Screens.RegisterScreen import SignUpScreen
from Screens.Settings import SettingsScreen
from database.DatabaseManager import DatabaseManager


app = QApplication(sys.argv)
widget = QStackedWidget()
widget.setWindowTitle('RansoGuard')

database= DatabaseManager()
hasher=argon2.PasswordHasher()

sign_in_screen = SignInScreen(widget, database, hasher)
#widget.addWidget(sign_in_screen)

sign_up_screen = SignUpScreen(widget, database, hasher)
#widget.addWidget(sign_up_screen)

main_screen = MainScreen(widget)
widget.addWidget(main_screen)


history_screen = HistoryScreen(widget)
widget.addWidget(history_screen)

settings_screen = SettingsScreen(widget)
widget.addWidget(settings_screen)

widget.setFixedHeight(700)
widget.setFixedWidth(1050)
widget.show()



try:
    sys.exit(app.exec_())
except:
    print("Exiting")
