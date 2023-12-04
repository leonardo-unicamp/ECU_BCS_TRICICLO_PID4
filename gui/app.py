# Author: Leonardo Rossi Leao
# Description: main application
# Created at: 2023-10-27
# Last update: 2023-10-28

import sys
import os
import numpy as np

from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QStyle, QFileDialog, QVBoxLayout, QLabel

from widgets.matplotlibwidget import MatplotlibWidget

from modules.observer import Observer
from modules.communication import Communication

from windows.connection import ConnectionWindow
from windows.parameters import ParametersWindow


class App(QMainWindow):


    signal_update_values = pyqtSignal(str, float)


    def __init__(self) -> None:
        super(App, self).__init__()
        loadUi("ui/app.ui", self)

        self.save_data = {
            "save": False,
            "path": None,
        }
        self.plots = []
        self.plots_data = {}

        self.plot_area_widget = QWidget()       
        self.plot_layout = QVBoxLayout()

        self.conn_window  = ConnectionWindow()
        self.param_window = ParametersWindow()
        
        self.comm = Communication()

        self.conn_window.signal_connect.connect(self.deviceConnected)
        self.conn_window.signal_disconnect.connect(self.deviceDisconnected)

        self.param_window.signal_add.connect(self.addPlot)

        self.signal_update_values.connect(self.updateDisplayValues)
        self.btn_connect_change.clicked.connect(self.conn_window.show)
        self.btn_add_plot.clicked.connect(self.param_window.show)
        self.btn_play.clicked.connect(self.play)
        self.btn_stop.clicked.connect(self.stop)

        self.btn_play.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.btn_stop.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))

        self.scrollArea.setWidgetResizable(True)
        

    def deviceConnected(self, comm_type: str, device: str):

        """
        Handles with the device connection.
        """

        style  = "background-color: %s; border: 1px solid black;"
        status = f"{comm_type.capitalize()} - {device}"

        self.led_connect_status.setStyleSheet(style % "#378805")
        self.lb_connect_status.setText(status)


    def deviceDisconnected(self):

        """
        Handles with the device disconnection.
        """

        style  = "background-color: %s; border: 1px solid black;"
        status = "No device connected"

        self.led_connect_status.setStyleSheet(style % "#C21807")
        self.lb_connect_status.setText(status)


    def play(self):

        """
        Sends a command to start receive streaming data and
        requests to user indicate the save folder.
        """
    
        folder = QFileDialog.getExistingDirectory(self, "Select the destination folder")
        if folder != "":
            if not os.path.exists(folder):
                os.makedirs(folder) 
            self.save_data["path"] = folder
            self.save_data["save"] = True

            self.btn_play.setEnabled(False)
            self.btn_stop.setEnabled(True)

            self.observer = Observer(self.comm.get, delay=0.1)
            for i in range(22):
                self.observer.appendVariable("%.2d" % i, "#g%.2d;" % i, self.signal_update_values.emit)
            self.observer.setSavePath(folder)
            self.observer.start()


    def stop(self):

        """
        Sends a command to stop receive streaming data.
        """

        self.btn_play.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.save_data["save"] = False
        self.observer.stop()


    def updateDisplayValues(self, name: str, value: float):

        """
        Updates the display values.

        Params
        ------
        name    (str): name of the variable.
        value (float): value of the variable.
        """

        label_widget = self.findChild(QLabel, "lb_data_%.2d" % int(name))
        if label_widget is not None:
            label_widget.setText("%.2f" % value)
            if name not in self.plots_data.keys():
                self.plots_data[name] = [value]
            else:
                self.plots_data[name].append(value)


    def addPlot(self, parameters: list):

        """
        Adds a new plot to the application.
        
        Params
        ------
        parameters (list): list of parameters to be plotted.
        """

        plot = MatplotlibWidget(
            len_x=100,
            interval=50,
            params=parameters,
            get_fnc=self.observer.get
        )

        self.plots.append({
            "plot": plot,
            "params": parameters
        })

        self.plot_layout.addWidget(plot)
        self.plot_layout.setAlignment(Qt.AlignTop)
        self.plot_layout.setSpacing(0)
        self.plot_layout.setContentsMargins(0, 0, 0, 0)
        self.plot_area_widget.setLayout(self.plot_layout)
        self.scrollArea.setWidget(self.plot_area_widget)


if __name__ == "__main__":

    """
    Entry point of the application.
    """
    
    app = QApplication(sys.argv)
    app_window = App()
    app_window.show()
    sys.exit(app.exec_())