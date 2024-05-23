from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QListWidgetItem
from PyQt5.uic import loadUi

from Screens.ReportScreen import ReportScreen


class HistoryScreen(QDialog):
    def __init__(self, widget):
        super(HistoryScreen, self).__init__()
        loadUi("history.ui", self)
        self.widget = widget
        self.report_history=[]
        self.listWidget.itemClicked.connect(self.on_item_clicked)
        self.report_windows_oppened=[]
        self.init_buttons()

    def init_buttons(self):
        self.homeButton.clicked.connect(self.go_to_main)
        self.settingsButton.clicked.connect(self.go_to_settings)
        self.menu_button_hovers()
        icon = QIcon('home.png')
        self.homeButton.setIcon(icon)
        icon = QIcon('histroy.png')
        self.historyButton.setIcon(icon)
        icon = QIcon('settings.png')
        self.settingsButton.setIcon(icon)

    def go_to_settings(self):
        self.historyButton.setChecked(True)
        self.widget.setCurrentIndex(4)

    def go_to_main(self):
        self.historyButton.setChecked(True)
        self.widget.setCurrentIndex(2)

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

    def set_report_history(self,report_history):
        self.listWidget.clear()
        self.report_history=report_history
        self.populate_list_widget()

    def populate_list_widget(self):
        for tree_pair in self.report_history:
            file_name=tree_pair[0]
            if len(file_name)>50:
                file_name=file_name[:50]+"..."
            prediction=tree_pair[1]
            item_text = f"{file_name}: {prediction[0]}"

            item = QListWidgetItem(item_text)

            self.listWidget.addItem(item)

    def on_item_clicked(self, item):
        index = self.listWidget.row(item)
        report_window = ReportScreen(self.widget, self.report_history[index][1], self.report_history[index][2], self.report_history[index][0])
        report_window.show()
        self.report_windows_oppened.append(report_window)