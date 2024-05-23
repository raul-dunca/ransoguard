from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets




class ReportScreen(QDialog):
    def __init__(self, widget, prediction, features_dict, filename):
        super(ReportScreen, self).__init__()
        loadUi("report.ui", self)
        self.setWindowTitle('Report: '+filename)
        self.tableWidget.setColumnWidth(0,520)
        self.tableWidget.setColumnWidth(1, 400)
        self.widget = widget
        self.prediction=prediction[0]
        self.features_dict=features_dict
        self.filename=filename
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.set_text()
        self.populate_summary(features_dict)

    def set_text(self):
        self.prediction_label.setText(self.prediction)
        self.filename_label.setText(self.filename)

    def populate_summary(self,features_dict):
        self.tableWidget.setRowCount(len(features_dict))
        self.tableWidget.setColumnCount(2)

        for row, (feature, value) in enumerate(features_dict.items()):
            self.tableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(feature))
            self.tableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem(str(value)))

