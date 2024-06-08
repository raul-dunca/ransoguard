import csv
import json
import os
import queue
import re
import subprocess
import threading
import time

import numpy as np
import pandas as pd
from collections import Counter

import pefile
import requests
from PyQt5.QtCore import Qt, QFileInfo, pyqtSlot, pyqtSignal, QPropertyAnimation, QEasingCurve, QMutex, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QFileDialog
from PyQt5.uic import loadUi
from dotenv import load_dotenv
import joblib

from Screens.ReportScreen import ReportScreen
from Screens.Utilities import show_error_message


class MainScreen(QDialog):
    update_progress = pyqtSignal(int)
    error_sig=pyqtSignal(int)
    def __init__(self, widget):
        super(MainScreen, self).__init__()
        loadUi("main.ui", self)
        self.widget = widget
        self.error_queue = queue.Queue()
        self.smooth_progress_animation = None
        self.mutex = QMutex()
        self.error_mtx = QMutex()
        self.dictionary_mtx=QMutex()
        self.error=False
        self.done_threads=0
        self.features_dictionary={}
        self.init_dragndrop_label()
        self.init_buttons()
        self.init_progress_bar()
        self.submit_error=False
        self.get_best_features()
        self.model = joblib.load('ransomware_classifier_rf.pkl')
        self.report_windows = []
        self.report_history = []
        self.load_report_history()
        self.file_in_analysis=""


    def init_progress_bar(self):
        self.progressBar.hide()
        self.loadin_label.hide()
        self.changing_label.hide()
        self.messages = ["Scanning file structure",
                         "Patching up stuff",
                         "Checking for anomalies",
                         "Analyzing file headers",
                         "Inspecting API calls",
                         "Identifying patterns",
                         "Just a little longer",
                         "Finishing things up",
                         "Generating report"]
        self.changing_label.setText(self.messages[0])
        self.current_message_index = 1
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_loadin_label)
        self.timer_changing_label = QTimer(self)
        self.timer_changing_label.timeout.connect(self.update_changing_label)
        self.update_progress.connect(self.update_progress_bar)
        self.error_sig.connect(self.analysis_error)

    def init_dragndrop_label(self):
        self.dragndrop_label.setAcceptDrops(True)
        self.dragndrop_label.dragEnterEvent = self.drag_enter_event
        self.dragndrop_label.dragMoveEvenet = self.drag_move_event
        self.dragndrop_label.dropEvent = self.drop_event

    def init_buttons(self):
        self.historyButton.clicked.connect(self.go_to_history)
        self.settingsButton.clicked.connect(self.go_to_settings)
        self.browse_files_button.clicked.connect(self.browser_files)
        self.menu_button_hovers()
        icon = QIcon('home.png')
        self.homeButton.setIcon(icon)
        icon = QIcon('histroy.png')
        self.historyButton.setIcon(icon)
        icon = QIcon('help.png')
        self.settingsButton.setIcon(icon)

    def drag_enter_event(self,event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def drag_move_event(self,event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def drop_event(self,event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            file_path=event.mimeData().urls()[0].toLocalFile()

            file_info = QFileInfo(file_path)
            if file_info.isSymLink():
                true_path = file_info.symLinkTarget()
            else:
                true_path=file_path
            quoted_file_path = '"{}"'.format(true_path)
            self.file_in_analysis = os.path.basename(true_path)
            self.perform_analysis(quoted_file_path)

    def browser_files(self):
        file_path, _ = QFileDialog.getOpenFileName(self,"Open File","c:\\","All Files (*)")
        if file_path:
            quoted_file_path = '"{}"'.format(file_path)
            self.file_in_analysis = os.path.basename(file_path)
            self.perform_analysis(quoted_file_path)

    def get_best_features(self):
        self.best_features=set()

        with open("best_features.txt", 'r') as file:
            lines = file.readlines()

        for line in lines:
            parts = line.split()
            name = parts[1].strip()
            self.best_features.add(name)


    def show_loading_bar(self):
        self.dragndrop_label.hide()
        self.browse_files_button.hide()
        self.progressBar.show()
        self.loadin_label.show()
        self.changing_label.show()
        self.timer.start(1000)
        self.timer_changing_label.start(12000)

    def hide_loading_bar(self):
        self.done_threads = 0
        self.progressBar.hide()
        self.loadin_label.hide()
        self.changing_label.hide()
        self.changing_label.setText(self.messages[0])
        self.current_message_index = 1
        self.timer.stop()
        self.timer_changing_label.stop()
        self.progressBar.setValue(0)
        self.dragndrop_label.show()
        self.browse_files_button.show()

    def update_loadin_label(self):
        """
        This function generates the . -> ... animation for Loading.
        """
        text = "Loading"
        self.loadin_label.setText(text + "." * (self.loadin_label.text().count(".") + 1))
        if len(self.loadin_label.text()) > len(text) + 3:
            self.loadin_label.setText(text)

    def update_changing_label(self):
        """
        Responsible for changing the text message when loading.
        """
        self.changing_label.setText(self.messages[self.current_message_index])
        self.current_message_index = (self.current_message_index + 1) % len(self.messages)

    def write_dict_to_csv(self):

        fieldnames = self.features_dictionary.keys()
        try:
            with open("output.csv", 'w+', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow(self.features_dictionary)
        except Exception as e:
            print(e)
    def write_dict_to_text(self):
        with open("output.txt", 'w+') as file:
            for key, value in self.features_dictionary.items():
                file.write(f"{key}: {value}\n")

    def perform_analysis(self,file_path):
        """
        Perform static analysis on file_path, it generates 4 threads 1 for each command (pefile,floss,Dependency,exiftool).
        """
        self.show_loading_bar()
        self.error=False
        thread_pefile = threading.Thread(target=self.run_pefile,args=(file_path,))
        thread_floss= threading.Thread(target=self.run_floss,args=(file_path,))
        thread_dynamic=threading.Thread(target=self.run_dynamic,args=(file_path,))
        #thread_dependency=threading.Thread(target=self.run_dependency,args=(file_path,))
        thread_exiftool=threading.Thread(target=self.run_exiftool,args=(file_path,))
        thread_pefile.start()
        thread_floss.start()
        thread_dynamic.start()
        #thread_dependency.start()
        thread_exiftool.start()

    def run_pefile(self,file_path):
        """
        executes pefile on the file_path
        """
        output_file = "output_pefile"
        file_path=file_path.strip('"')          #necessary bcs file_path is quoted (in case it has space) byt pefile takes care of that case already
        try:
            pe = pefile.PE(file_path)
            with open(output_file, "w") as f:
                f.write(str(pe))

            output = str(pe)
            hex_pattern = r"0[xX][0-9A-Fa-f]+"
            title = ""
            section_name = ""
            good_section_names = {"LOAD_CONFIG", "DOS_HEADER", "NT_HEADERS", "FILE_HEADER", "OPTIONAL_HEADER",
                                  "PE Sections", "Directories", "Imported symbols", "TLS", ""}
            index = 0
            imported_symbols = []
            for entry in pe.DIRECTORY_ENTRY_IMPORT:
                imported_symbols.append(entry.dll.decode())  # create a imported symbols list

            for line in output.strip().split('\n'):

                if line.startswith("----------") and line.endswith("----------"):
                    section_name = line.replace('-', '')

                if section_name in good_section_names:

                    if line.startswith("[") and line.endswith("]"):
                        title = line[1:-1]

                    if title == "IMAGE_IMPORT_DESCRIPTOR":  # we are in the Imported Symbols section
                        title = imported_symbols[index]
                        index += 1

                    if title != "" and line.startswith(title):  # add dll functions imported to the feature_dictionary
                        dll = line.split()[0]
                        self.dictionary_mtx.lock()
                        self.features_dictionary[dll] = 1
                        self.dictionary_mtx.unlock()

                    match = re.findall(hex_pattern, line)
                    if match:
                        if len(match) >= 3:
                            field_name, value = line.split()[2], int(match[2], 16)
                            # value = int(value, 16)  or   value = hex_to_int(value)
                        else:
                            field_name, value = line.split()[2], 0

                        if field_name == "Name:" and title == "IMAGE_SECTION_HEADER":  # we are inside the PE Sections section
                            title = line.split(':')[1].strip()
                        else:
                            field_name = field_name[:-1]
                            self.dictionary_mtx.lock()
                            self.features_dictionary[title + "_" + field_name] = value
                            self.dictionary_mtx.unlock()

            self.mutex.lock()
            self.update_progress.emit(25)
        except Exception as e:
            error_message = f"Pefile Error: {e.args[0]}"
            self.error_mtx.lock()
            self.error_queue.put(error_message)
            self.error_sig.emit(1)

    def show_errors(self):
        error_message = ""
        while not self.error_queue.empty():
            error_message += self.error_queue.get().strip() + '\n'
        self.hide_loading_bar()

        show_error_message(error_message)


    @pyqtSlot(int)
    def analysis_error(self,id):
        """
        this is the function that executes when an error signal is emitted
        when all threads are finished (self.done_threads==4) it prints all
        the error messages in one MessageBox.
        """
        self.done_threads+=1
        if self.error==False:           #this is to make sure that no loading animation happens in case of an error
            self.error=True
        if self.done_threads==4:
            self.show_errors()
        self.error_mtx.unlock()

    @pyqtSlot(int)
    def update_progress_bar(self, value):
        """
        this is the function that executes when the update progress signal is
        emitted it creates the animation for the progress bar. it counts the
        threads in the case when an error occurs before this thread execution.
        """
        if not self.error:
            current=self.progressBar.value()

            self.smooth_progress_animation = QPropertyAnimation(self.progressBar, b"value")
            self.smooth_progress_animation.setDuration(10000)  # Animation duration in milliseconds
            self.smooth_progress_animation.setStartValue(current)
            self.smooth_progress_animation.setEndValue(current+value)
            self.smooth_progress_animation.setEasingCurve(QEasingCurve.OutCubic)

            self.smooth_progress_animation.finished.connect(self.animation_finished)
            self.smooth_progress_animation.start()
        else:

            self.mutex.unlock()

            self.error_mtx.lock()
            self.done_threads += 1
            if self.done_threads==4 and self.error==True:
                self.show_errors()
            self.error_mtx.unlock()

    def clean_column_names(self,df):
        df.columns = df.columns.str.replace(r'[^\w.]', '', regex=True)
        df = df.loc[:, ~df.columns.duplicated()]
        return df

    def process_csv_files(self,file_path):

        df = pd.read_csv(file_path)

        if any(df.columns.str.contains(r'\W')):
            df = self.clean_column_names(df)
        df.to_csv("clean.csv", index=False)

    def csv_to_dict(self):
        with open("clean.csv", 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            return next(reader, {})

    def load_report_history(self):
        try:
            with open('report_history.json', 'r') as file:
                loaded_data = json.load(file)

            self.report_history= [(filename, np.array(malware_types), attributes) for filename, malware_types, attributes in loaded_data]
        except FileNotFoundError:
            self.report_history = []


    def save_report_history(self):
        data = [(filename, malware_types.tolist(), attributes) for filename, malware_types, attributes in self.report_history]
        with open('report_history.json', 'w+') as file:
            json.dump(data, file)

    def open_sub_window(self,prediction, summary_dict):

        report_window = ReportScreen(self.widget, prediction,summary_dict,self.file_in_analysis)
        report_window.show()
        self.report_windows.append(report_window)
        self.report_history.append((self.file_in_analysis,prediction, summary_dict))
        self.save_report_history()
        self.update_histroy()


    def animation_finished(self):
        """
        when the progress bar animation is done count the thread and check if this is the last thread,
        in the case when all 4 tools did not encountered errors and if it is just hide the progress bar.
        """
        self.error_mtx.lock()
        self.done_threads += 1
        if self.done_threads == 4 and self.error == True:
            self.show_errors()
        self.error_mtx.unlock()

        if self.progressBar.value()==100:
            self.perform_prediction()

        self.mutex.unlock()

    def perform_prediction(self):
        self.hide_loading_bar()
        self.write_dict_to_csv()
        self.process_csv_files("output.csv")

        cleaned_features = self.csv_to_dict()

        final_dict = {}
        for feature in self.best_features:
            if feature in cleaned_features:
                final_dict[feature] = cleaned_features[feature]
            else:
                final_dict[feature] = 0

        data = pd.DataFrame(final_dict, index=[0])  # Assuming the data is a single sample
        data = data.reindex(sorted(data.columns), axis=1)

        prediction = self.model.predict(data)

        sorted_dict = dict(sorted(final_dict.items()))
        self.open_sub_window(prediction,sorted_dict)

    def run_floss(self,file_path):
        """
        executes floss on the file_path and error handles it
        """

        command = "floss -L -q " + file_path
        #with open ("output_floss",'w') as f:
        #    result=subprocess.run(command, shell=True, stdout=f, stderr=subprocess.PIPE)

        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode !=0:
            error_message = f"Floss Error: failed to analyze sample"
            self.error_mtx.lock()
            self.error_queue.put(error_message)
            self.error_sig.emit(2)
        else:
            output = result.stdout.decode('utf-8')
            self.dictionary_mtx.lock()
            lines = ["str_" + line.strip() for line in output.split('\n') if
                     line.strip() not in self.features_dictionary]
            string_counter = Counter(lines)
            self.features_dictionary.update(string_counter)
            self.dictionary_mtx.unlock()

            self.mutex.lock()
            self.update_progress.emit(25)

    def run_dependency(self,file_path):
        """
        executes Dependencies on the file_path and error handles it
        """

        command = "Dependencies -modules " + file_path
        #with open("output_dep", 'w') as f:
        #    result=subprocess.run(command, shell=True, stdout=f, stderr=subprocess.PIPE)

        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.stderr:
            error_message = f"Dependencies Error: {result.stderr.decode('utf-8')}"
            self.error_mtx.lock()
            self.error_queue.put(error_message)
            self.error_sig.emit(3)
        else:
            output = result.stdout.decode('utf-8')
            lines = output.strip().split('\n')
            for i in range(1,len(lines)):
                line=lines[i]
                parts = line.split('] ')
                if len(parts) > 1:
                    dll_info = parts[1].split(' : ')
                    if len(dll_info)==2:
                        dll=dll_info[0].strip()
                        self.dictionary_mtx.lock()
                        self.features_dictionary[dll] = 1
                        self.dictionary_mtx.unlock()
                    elif len(dll_info)==1:
                        dll=dll_info[0][:-1].strip()
                        self.dictionary_mtx.lock()
                        self.features_dictionary[dll] = 1
                        self.dictionary_mtx.unlock()
                    else:
                        print("WHAT happened??????? Dependency error??")


            self.mutex.lock()
            self.update_progress.emit(25)

    def submit_file(self,file_path, api_key):
        url = "https://www.hybrid-analysis.com/api/v2/submit/file"
        headers = {
            "User-Agent": "Falcon Sandbox",
            "api-key": api_key
        }
        data = {
            "environment_id": 160,  # WINDOWS 10 64 bits
            "hybrid_analysis": True,
            "experimental_anti_evasion": True,
            "script_logging": True,
            "input_sample_tampering": True,
            "network_settings": "simulated",
            "custom_run_time": 180,
        }

        try:
            with open(file_path, "rb") as file:
                files = {"file": file}
                response = requests.post(url, files=files, data=data, headers=headers)
                if response.status_code == 201:
                    return response.json()
                else:
                    return None
        except Exception as e:
            return None

    def get_analysis_report(self,api_key, analysis_id, features_dir):
        url = f"https://www.hybrid-analysis.com/api/v2/report/{analysis_id}/summary"
        headers = {
            "User-Agent": "Falcon Sandbox",
            "api-key": api_key
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:

                json_resp = response.json()

                if json_resp["total_processes"]:
                    self.dictionary_mtx.lock()
                    features_dir["total_processes"] = json_resp["total_processes"]
                    self.dictionary_mtx.unlock()

                for processes in json_resp["processes"]:
                    if processes["name"]:
                        self.dictionary_mtx.lock()
                        features_dir["PROC_" + processes["name"]] = 1
                        self.dictionary_mtx.unlock()

                for attack in json_resp["mitre_attcks"]:
                    if attack["tactic"]:
                        self.dictionary_mtx.lock()
                        features_dir[attack["tactic"]] = 1
                        self.dictionary_mtx.unlock()
                    if attack["technique"]:
                        self.dictionary_mtx.lock()
                        features_dir[attack["technique"]] = 1
                        self.dictionary_mtx.unlock()
                    if attack["attck_id"]:
                        self.dictionary_mtx.lock()
                        features_dir[attack["attck_id"]] = 1
                        self.dictionary_mtx.unlock()

                for signature in json_resp["signatures"]:
                    if signature["name"]:
                        self.dictionary_mtx.lock()
                        features_dir["SIG_" + signature["name"]] = 1
                        self.dictionary_mtx.unlock()
                        if signature["relevance"]:
                            self.dictionary_mtx.lock()
                            features_dir["SIG_" + signature["name"] + "_REL"] = signature["relevance"]
                            self.dictionary_mtx.unlock()
                        if signature["threat_level"]:
                            self.dictionary_mtx.lock()
                            features_dir["SIG_" + signature["name"] + "_THRD_LVL"] = signature["threat_level"]
                            self.dictionary_mtx.unlock()
                return True
            else:
                return None
        except Exception as e:
            return None

    def check_status(self,api_key, analysis_id):
        url = f"https://www.hybrid-analysis.com/api/v2/report/{analysis_id}/state"
        headers = {
            "api-key": api_key
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                resp = response.json()
                if resp["state"] == "SUCCESS":
                    return True
                elif resp["state"] == "ERROR":
                    self.submit_error=True
                    return True
                else:
                    return False
            else:
                self.submit_error=True
                return True
        except Exception as e:
            self.submit_error=True
            return True

    def run_dynamic(self, file_path):
        """
        executes dynamic analysis
        """
        file_path = file_path.strip('"')
        load_dotenv()
        api_key = os.environ.get("API_KEY")
        response = self.submit_file(file_path, api_key)
        self.submit_error=False
        if response:
            analysis_id=response.get("job_id")
            while self.check_status(api_key, analysis_id) != True and not self.error:
                time.sleep(30)
            if self.submit_error:
                error_message = f"Dynamic Error when checking status!"
                self.error_mtx.lock()
                self.error_queue.put(error_message)
                self.error_sig.emit(3)
            else:
                out=self.get_analysis_report(api_key, analysis_id,self.features_dictionary)
                if out :
                    self.mutex.lock()
                    self.update_progress.emit(25)
                else:
                    error_message = f"Dynamic Error when getting report"
                    self.error_mtx.lock()
                    self.error_queue.put(error_message)
                    self.error_sig.emit(3)
        else:
            error_message = f"Dynamic Error when Submitting"
            self.error_mtx.lock()
            self.error_queue.put(error_message)
            self.error_sig.emit(3)

    def run_exiftool(self,file_path):
        """
        executes exiftool on the file_path and error handles it
        """

        command = "exiftool -n  " + file_path
        with open("output_exiftool", 'w') as f:
            result=subprocess.run(command, shell=True, stdout=f, stderr=subprocess.DEVNULL)

        result=subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

        if result.stderr:
            error_message = f"Exiftool Error: {result.stderr.decode('utf-8')}"
            self.error_mtx.lock()
            self.error_queue.put(error_message)
            self.error_sig.emit(4)
        else:
            output = result.stdout.decode('utf-8')


            for line in output.strip().split('\n'):
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                if key.strip() == "ExifTool Version Number":
                    continue

                try:
                    value = int(value)
                except ValueError:
                    try:
                        value = float(value)
                    except ValueError:
                        continue                # Skip if value is not int or float


                self.dictionary_mtx.lock()
                self.features_dictionary[key.strip()] = value
                self.dictionary_mtx.unlock()

            self.mutex.lock()
            self.update_progress.emit(25)


    def go_to_settings(self):
        self.homeButton.setChecked(True)
        self.widget.setCurrentIndex(2)          #4 with login

    def update_histroy(self):
        history_screen_widget = self.widget.widget(1)       #3 with login
        history_screen_widget.set_report_history(self.report_history)

    def go_to_history(self):
        self.homeButton.setChecked(True)
        self.widget.setCurrentIndex(1)                  #3 with login
        self.update_histroy()

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

    def closeEvent(self, event):
        # Close all open report windows when the main window is closed
        for report_window in self.report_windows:
            report_window.close()
        event.accept()