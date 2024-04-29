from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi


class SettingsScreen(QDialog):
    def __init__(self, widget):
        super(SettingsScreen, self).__init__()
        loadUi("settings.ui", self)
        self.widget = widget
        self.init_buttons()

    def init_buttons(self):
        self.homeButton.clicked.connect(self.go_to_main)
        self.historyButton.clicked.connect(self.go_to_history)
        self.menu_button_hovers()

    def go_to_main(self):
        self.settingsButton.setChecked(True)
        self.widget.setCurrentIndex(2)

    def go_to_history(self):
        self.settingsButton.setChecked(True)
        self.widget.setCurrentIndex(3)

    def menu_button_hovers(self):
        self.homeButton.enterEvent = lambda event: self.button_enter(event, self.homeButton, self.home_label)
        self.homeButton.leaveEvent = lambda event: self.button_leave(event, self.home_label)

        self.historyButton.enterEvent = lambda event: self.button_enter(event, self.historyButton, self.history_label)
        self.historyButton.leaveEvent = lambda event: self.button_leave(event, self.history_label)

        self.settingsButton.enterEvent = lambda event: self.button_enter(event, self.settingsButton, self.settings_label)
        self.settingsButton.leaveEvent = lambda event: self.button_leave(event, self.settings_label)

    def button_enter(self, event, button, label):
        if not button.isChecked():
            label.setStyleSheet("color: #990011;")

    def button_leave(self, event, label):
        label.setStyleSheet("")
