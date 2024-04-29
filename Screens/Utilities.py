from PyQt5.QtWidgets import QMessageBox


def show_warning_message(message):

    msg_box = QMessageBox()
    msg_box.setWindowTitle("Warning")
    msg_box.setIcon(QMessageBox.Warning)
    msg_box.setText(message)
    ok_button = msg_box.addButton(QMessageBox.Ok)
    ok_button.setStyleSheet("""
            QPushButton {
                font: bold 10pt;
                font-family: "Century Gothic";

            }
        """)
    msg_box.setStyleSheet("""
         QMessageBox {
             background-color: #FCF6F5;
             font: bold 10pt;
             font-family:"Century Gothic";
         }
     """)
    msg_box.exec()


def show_error_message(message):
    msg_box = QMessageBox()
    msg_box.setWindowTitle("Error")
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setText(message)
    ok_button = msg_box.addButton(QMessageBox.Ok)
    ok_button.setStyleSheet("""
            QPushButton {
                font: bold 10pt;
                font-family: "Century Gothic";

            }
        """)
    msg_box.setStyleSheet("""
         QMessageBox {
             background-color: #FCF6F5;
             font: bold 10pt;
             font-family:"Century Gothic";
         }
     """)
    msg_box.exec()


def show_information_message(message):
    msg_box = QMessageBox()
    msg_box.setWindowTitle("Information")
    msg_box.setIcon(QMessageBox.Information)
    msg_box.setText(message)
    ok_button = msg_box.addButton(QMessageBox.Ok)
    ok_button.setStyleSheet("""
            QPushButton {
                font: bold 10pt;
                font-family: "Century Gothic";

            }
        """)
    msg_box.setStyleSheet("""
         QMessageBox {
             background-color: #FCF6F5;
             font: bold 10pt;
             font-family:"Century Gothic";
         }
     """)
    msg_box.exec()


