#!/usr/bin/env python3
# This program runs on host computer and connects to an RPyC server running on 
# the EV3 device


#  python -m venv .venv
#  .venv\Scripts\activate
#  python -m pip install --upgrade pip

#  Call the line below to generate python code from the Qt ui file
#  pyqt5-tools pyuic5 .\EV3_BaseStation.ui
import sys
import EV3_Controller as ev3
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtWidgets import QGridLayout

from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPalette
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QImage
from PyQt5 import QtCore
#from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QLineEdit
from PyQt5 import QtGui
import numpy as np
import matplotlib.pyplot as plt
import pyqtgraph as pg

COLORTABLE=[]
for i in range(256): COLORTABLE.append(QtGui.qRgb(int(i),int(i),int(i)))

MAP_WIDTH=800
MAP_HEIGHT=1000

a=np.random.random(MAP_HEIGHT*MAP_WIDTH)*255
a=np.reshape(a,(MAP_HEIGHT,MAP_WIDTH))
a=np.require(a, np.uint8, 'C')

class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #uic.loadUi("EV3_BaseStation.ui", self)

        self.robot = None

        self.setWindowTitle("EV3 Base")

        self.main_layout = QtWidgets.QHBoxLayout()
        
        self.left_column = QtWidgets.QVBoxLayout()
        self.left_column.setGeometry(QtCore.QRect(10, 10, 231, 711))
        
        self.right_column = QtWidgets.QVBoxLayout()

        self.status = QtWidgets.QFormLayout()
       
        # self.formLayout.setLabelAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        # self.formLayout.setObjectName("formLayout")
        # self.label_Heading = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.default_btn_width = 80
        
        self.text_heading = QLineEdit()
        self.text_heading.setText("0.0")
        self.text_heading.setMaximumHeight(24)
        self.text_heading.setMaximumWidth(120)
        self.status.addRow("Heading", self.text_heading)

        self.text_range = QLineEdit()
        self.text_range.setMaximumHeight(24)
        self.text_range.setMaximumWidth(120)
        self.text_range.setText("0.0")
        self.status.addRow("Range",self.text_range)

        self.text_position = QLineEdit()
        self.text_position.setMaximumHeight(24)
        self.text_position.setMaximumWidth(120)
        self.text_position.setText("-")
        self.status.addRow("Position",self.text_position)

        self.text_speed = QLineEdit()
        self.text_speed.setMaximumHeight(24)
        self.text_speed.setMaximumWidth(120)
        self.text_speed.setText("-")
        self.status.addRow("Speed",self.text_speed)
        

        self.num_button_columns = 4
        self.ControlsBox = QGroupBox("Controls")
        self.ControlsBox.setMaximumWidth(int(1.15*self.num_button_columns*self.default_btn_width))
        self.controls = QGridLayout()
        self.ControlsBox.setLayout(self.controls)

        self.btn_Scan = QtWidgets.QPushButton(self)
        self.btn_Scan.setText("Ultra Scan")
        self.btn_Scan.setMinimumWidth(self.default_btn_width)
        self.btn_Scan.setMinimumHeight(self.default_btn_width)
        self.btn_Scan.setMaximumWidth(self.default_btn_width)
        self.btn_Scan.setMaximumHeight(self.default_btn_width)
        self.controls.addWidget(self.btn_Scan,1,1)
        self.btn_Scan.clicked.connect(self.on_scan_btn_clicked)

        self.btn_StopMotors = QPushButton(self)
        self.btn_StopMotors.setText("Stop Robot")
        self.btn_StopMotors.setMinimumHeight(self.default_btn_width)
        self.btn_StopMotors.setMinimumHeight(self.default_btn_width)
        self.btn_StopMotors.setMaximumWidth(self.default_btn_width)
        self.controls.addWidget(self.btn_StopMotors,1,2)
        self.btn_StopMotors.clicked.connect(self.on_stop_btn_clicked)

        self.btn_MotionTest = QtWidgets.QPushButton(self)
        self.btn_MotionTest.setText("Motion Test")
        self.btn_MotionTest.setMaximumWidth(self.default_btn_width)
        self.btn_MotionTest.setMinimumHeight(self.default_btn_width)
        self.btn_MotionTest.setMinimumHeight(self.default_btn_width)
        self.controls.addWidget(self.btn_MotionTest,2,1)
        
        self.btn_MQTT = QtWidgets.QPushButton(self)
        self.btn_MQTT.setText("MQTT")
        self.btn_MQTT.setMinimumHeight(self.default_btn_width)
        self.btn_MQTT.setMinimumHeight(self.default_btn_width)
        self.btn_MQTT.setMaximumWidth(self.default_btn_width)
        self.controls.addWidget(self.btn_MQTT,1,3)
        self.btn_MQTT.clicked.connect(self.on_connect_btn_clicked)
        
        self.btn_plotmap = QtWidgets.QPushButton(self)
        self.btn_plotmap.setText("Plot Map")
        self.btn_plotmap.setMinimumHeight(self.default_btn_width)
        self.btn_plotmap.setMinimumHeight(self.default_btn_width)
        self.btn_plotmap.setMaximumWidth(self.default_btn_width)
        self.controls.addWidget(self.btn_plotmap,2,2)
        self.btn_plotmap.clicked.connect(self.plot_grid)

        self.btn_compass_cal = QtWidgets.QPushButton(self)
        self.btn_compass_cal.setText("Compass Cal")
        self.btn_compass_cal.setMinimumHeight(self.default_btn_width)
        self.btn_compass_cal.setMinimumHeight(self.default_btn_width)
        self.btn_compass_cal.setMaximumWidth(self.default_btn_width)
        self.controls.addWidget(self.btn_compass_cal,1,4)
        self.btn_compass_cal.clicked.connect(self.on_compass_cal_btn_clicked)
        
        # self.pushButton_2 = QtWidgets.QPushButton(self.verticalLayoutWidget)
        # self.pushButton_2.setObjectName("pushButton_2")
        # self.verticalLayout.addWidget(self.pushButton_2)
        # self.pushButton = QtWidgets.QPushButton(self.verticalLayoutWidget)
        # self.pushButton.setObjectName("pushButton")
        # self.verticalLayout.addWidget(self.pushButton)
        
        # self.btn_Scan.setObjectName("btn_Scan")
        # self.verticalLayout.addWidget(self.btn_Scan)
        # self.btn_StopMotors = QtWidgets.QPushButton(self.verticalLayoutWidget)
        # self.btn_StopMotors.setObjectName("btn_StopMotors")
        # self.verticalLayout.addWidget(self.btn_StopMotors)

        self.LogBox = QtWidgets.QGroupBox("Log")
        self.LogBox.setMaximumWidth(int(3.4*self.default_btn_width))
        self.LogLayout = QtWidgets.QVBoxLayout()
        self.logEdit = QTextEdit()
        self.LogLayout.addWidget(self.logEdit)
        self.LogBox.setLayout(self.LogLayout)
 
        self.left_column.addLayout(self.status)
        self.left_column.addWidget(self.ControlsBox)
        self.left_column.addWidget(self.LogBox)
        
        self.spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.left_column.addItem(self.spacerItem)

        #self.left_column.setGeometry(QtCore.QRect(0, 0, 60, 200))

        self.graphicsView = QtWidgets.QLabel(self)
        self.graphicsView.setGeometry(QtCore.QRect(0, 0, 600, 600))
        #graphicsView.setMinimumSize(800,800)
        self.graphicsView.setObjectName("graphicsView")
        self.graphicsView.setAlignment(Qt.AlignTop)

        self.headingPlot = pg.PlotWidget()
        self.headingPlot.setGeometry(QtCore.QRect(0, 0, 100, 600))
        self.headingPlot.showGrid(x=True, y=True)
       
        
        # self.qImg = QtGui.QImage(600, 600, QImage.Format_Indexed8)
        # self.graphicsView.setGeometry(QtCore.QRect(0,0,800,800))

        # map_img = np.random.randint(0,255, size=(800, 800))

        # QI=QtGui.QImage(map_img.data, 800, 800, QtGui.QImage.Format_Indexed8)
        # QI.setColorTable(COLORTABLE)
        # self.graphicsView.setPixmap(QtGui.QPixmap.fromImage(QI))

        self.main_layout.addLayout(self.left_column)
        self.main_layout.addLayout(self.right_column)
        
        self.right_column.addWidget(self.graphicsView)
        self.right_column.addWidget(self.headingPlot)

        time = list(range(300))
        heading = [np.sin(x/20)*180 for x in range(300)]
        self.heading_line = self.headingPlot.plot(time, heading)
        
        self.main_layout.setAlignment(Qt.AlignTop)
        
        widget = QtWidgets.QWidget()
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)

        self.counter = 0

        self.timer = QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_data)
        self.timer.start()

        self.setObjectName("MainWindow")
        self.resize(1200, 1000)
        self.setMinimumSize(QtCore.QSize(640, 480))
        
     
    def log(self, logText):
        self.logEdit.append(logText)

    def setRobot(self, bot):
        self.robot = bot

    def update_data(self):
        self.counter +=1
        if self.robot.new_ultra_message:
            self.text_range.setText(str(self.robot.get_ultra_range()))
            self.text_position.setText(str(self.robot.get_position()))
            self.text_heading.setText(str(self.robot.get_heading()))
            self.update_map()
        elif self.robot.new_heading_message: 
            self.text_heading.setText(str(self.robot.get_heading()))
        
        if self.robot.is_connected_to_mqtt():
            self.btn_MQTT.setStyleSheet("background-color: green")
        else:
            self.btn_MQTT.setStyleSheet("background-color: red")


    def update_map(self):    
        # global a
        # a=np.roll(a,-5)
        _grid_map = self.robot.get_map_grid()
        maxVal = np.max(_grid_map)
        norm_map= np.uint8(_grid_map*255/maxVal)
        self.graphicsView.setGeometry(QtCore.QRect(0,0,_grid_map.shape[0], _grid_map.shape[1]))
        QI = QImage(norm_map.data, _grid_map.shape[0], _grid_map.shape[1], QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(QI)
        #QI.setColorTable(COLORTABLE)
        self.graphicsView.setPixmap(pixmap)

    def on_scan_btn_clicked(self):
        self.robot.runUltraScan()
        self.log("Run Ultra Scan")

    def on_stop_btn_clicked(self):
        self.robot.stop_robot()
        self.log("Stop Robot")

    def on_connect_btn_clicked(self):
        try:
            self.robot.connect_mqtt()
            self.log("Connected to MQTT")
        except RuntimeError:
            self.log("Error connectting to MQTT")

    def on_compass_cal_btn_clicked(self):
        self.robot.calibrate_compass()

    def plot_grid(self):
        
        # Fixing random state for reproducibility
        #np.random.seed(19680801)
        #map_img = np.zeros((1024, 1024))
        # make data
        #X, Y = np.meshgrid(np.linspace(-3, 3, 256), np.linspace(-3, 3, 256))
        
        Z = self.robot.get_map_grid()*255
        fig, ax1 = plt.subplots()
        ax1.imshow(Z.T, cmap='bone', interpolation='none', aspect='equal', origin='lower')
        #Pxx, freqs, bins, im = ax2.specgram(x, NFFT=NFFT, Fs=Fs, noverlap=900)
        fig.show()
        return fig          


if __name__ == "__main__":
    app = QApplication(sys.argv)

    robot = ev3.EV3Supervisor()

    # Force the style to be the same on all OSs:
    app.setStyle("Fusion")

    # Now use a palette to switch to dark colors:
    # Now use a palette to switch to dark colors:
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.cyan)
    
    
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.cyan)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.cyan)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)

    app.setApplicationName("EV3 Base")

    app.setPalette(palette)
    
    window = MainWindow()
    window.setRobot(robot)
    window.show()
    window.update_map()
    app.exec_()