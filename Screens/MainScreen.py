import queue
import subprocess
import threading

import pefile
from PyQt5.QtCore import Qt, QFileInfo, pyqtSlot, pyqtSignal, QPropertyAnimation, QEasingCurve, QMutex, QTimer
from PyQt5.QtWidgets import QDialog, QFileDialog
from PyQt5.uic import loadUi

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
        self.error=False
        self.done_threads=0
        self.init_dragndrop_label()
        self.init_buttons()
        self.init_progress_bar()

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
            self.perform_static_analysis(quoted_file_path)

    def browser_files(self):
        file_path, _ = QFileDialog.getOpenFileName(self,"Open File","c:\\","All Files (*)")
        if file_path:
            quoted_file_path = '"{}"'.format(file_path)
            self.perform_static_analysis(quoted_file_path)


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


    def perform_static_analysis(self,file_path):
        """
        Perform static analysis on file_path, it generates 4 threads 1 for each command (pefile,floss,Dependency,exiftool).
        """
        self.show_loading_bar()
        self.error=False
        thread_pefile = threading.Thread(target=self.run_pefile,args=(file_path,))
        thread_floss= threading.Thread(target=self.run_floss,args=(file_path,))
        thread_dependency=threading.Thread(target=self.run_dependency,args=(file_path,))
        thread_exiftool=threading.Thread(target=self.run_exiftool,args=(file_path,))
        thread_pefile.start()
        thread_floss.start()
        thread_dependency.start()
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
            self.mutex.lock()
            self.update_progress.emit(25)
        except Exception as e:
            error_message = f"Pefile Error: {e.args[0]}"
            self.error_mtx.lock()
            self.error_queue.put(error_message)
            self.error_sig.emit(1)

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
            error_message=""
            while not self.error_queue.empty():
                error_message += self.error_queue.get().strip() + '\n'
            self.hide_loading_bar()

            show_error_message(error_message)
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
            self.error_mtx.unlock()

    def animation_finished(self):
        """
        when the progress bar animation is done count the thread and check if this is the last thread,
        in the case when all 4 tools did not encountered errors and if it is just hide the progress bar.
        """
        self.error_mtx.lock()
        self.done_threads += 1
        self.error_mtx.unlock()

        if self.progressBar.value()==100:
            self.hide_loading_bar()
        self.mutex.unlock()



    def run_floss(self,file_path):
        """
        executes floss on the file_path and error handles it
        """

        command = "floss " + file_path
        with open ("output_floss",'w') as f:
            result=subprocess.run(command, shell=True, stdout=f, stderr=subprocess.PIPE)

        if result.returncode !=0:
            error_message = f"Floss Error: failed to analyze sample"
            self.error_mtx.lock()
            self.error_queue.put(error_message)
            self.error_sig.emit(2)
        else:
            self.mutex.lock()
            self.update_progress.emit(25)

    def run_dependency(self,file_path):
        """
        executes Dependencies on the file_path and error handles it
        """

        command = "Dependencies -modules " + file_path
        with open("output_dep", 'w') as f:
            result=subprocess.run(command, shell=True, stdout=f, stderr=subprocess.PIPE)

        if result.stderr:
            error_message = f"Dependencies Error: {result.stderr.decode('utf-8')}"
            self.error_mtx.lock()
            self.error_queue.put(error_message)
            self.error_sig.emit(3)
        else:
            self.mutex.lock()
            self.update_progress.emit(25)

    def run_exiftool(self,file_path):
        """
        executes exiftool on the file_path and error handles it
        """

        command = "exiftool " + file_path
        with open("output_exiftool", 'w') as f:
            result=subprocess.run(command, shell=True, stdout=f, stderr=subprocess.DEVNULL)

        if result.stderr:
            error_message = f"Exiftool Error: {result.stderr.decode('utf-8')}"
            self.error_mtx.lock()
            self.error_queue.put(error_message)
            self.error_sig.emit(4)
        else:
            self.mutex.lock()
            self.update_progress.emit(25)

    def go_to_settings(self):
        self.homeButton.setChecked(True)
        self.widget.setCurrentIndex(4)

    def go_to_history(self):
        self.homeButton.setChecked(True)
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



