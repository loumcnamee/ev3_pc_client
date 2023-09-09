#!/usr/bin/env python3
# This program runs on host computer and connects to an RPyC server running on 
# the EV3 device

#  python -m venv .venv
#  .venv\Scripts\activate
#  python -m pip install --upgrade pip
#  pip install python-ev3dev2
# pip install paho-mqtt

import json
import io
import math
import PySimpleGUI as sg
import paho.mqtt.client as mqtt
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasAgg
import occupancy_grid as grid


class RobotData:
    """Class containing Robot state and sensor data"""

    ultra_range = 0.0
    heading = 0.0
    x = 0.0
    y = 0.0
    map_grid = grid.Occupancy_Grid(6,6,0.01)
    # map_grid = np.random.random([1024, 1024])

    def __init__(self):
        self.ultra_range = [
            0.0,
            0.0,
        ]  # ultrasonic range sensor reading with timestamp
        self.x = 256
        self.y = 256

    def ultra_sample(self, hdg, data):
        """add a new range sample from the ultrasonic sensor"""
        self.ultra_range = data/100
        self.heading = hdg
        #x_occ = math.floor(self.x + self.ultra_range*math.cos(hdg*math.pi/180))
        #y_occ = math.floor(self.y + self.ultra_range*math.sin(hdg*math.pi/180))
        #self.map_grid[x_occ, y_occ] = (self.map_grid[x_occ, y_occ] + 1)/2
        self.map_grid.sensor_reading(300, 300, hdg, 10, 0.1, self.ultra_range, 2.55, 0.01)
        #print("map grid update:", x_occ, y_occ, self.map_grid[x_occ, y_occ])

    def get_ultra_range(self):
        "return the last report ultra sonic range in [cm]"
        return self.ultra_range
    

    def heading_sample(self, data):
        """add a new heading sample from the compass sensor"""
        self.heading = data

    def get_heading(self):
        """return the last report ultra sonic range in [cm]"""
        return self.heading

    def get_map_grid(self):
        """return the robot map occupancy grid geerated from sensor data"""
        return self.map_grid.get_map()


def your_matplotlib_code(map_data):
    # Fixing random state for reproducibility
    #np.random.seed(19680801)

    #map_img = np.zeros((1024, 1024))
    # make data
    #X, Y = np.meshgrid(np.linspace(-3, 3, 256), np.linspace(-3, 3, 256))
    Z = map_data
    fig, ax1 = plt.subplots()
    ax1.imshow(Z.T, cmap='bone', interpolation='none', aspect='equal', origin='lower')
    #Pxx, freqs, bins, im = ax2.specgram(x, NFFT=NFFT, Fs=Fs, noverlap=900)

    return fig


def draw_figure(element, figure):
    """
    Draws the previously created "figure" in the supplied Image Element

    :param element: an Image Element
    :param figure: a Matplotlib figure
    :return: The figure canvas
    """

    plt.close('all')  # erases previously drawn plots
    canv = FigureCanvasAgg(figure)
    buf = io.BytesIO()
    canv.print_figure(buf, format='png')
    if buf is not None:
        buf.seek(0)
        element.update(data=buf.read())
        return canv
    else:
        return None


def main():
    """main"""
    robot = RobotData()

    plt.style.use('_mpl-gallery-nogrid')
    plt.rcParams["figure.figsize"]=(8,8)

    theme_dict = {
        "BACKGROUND": "#111122",
        "TEXT": "#BBBBEE",
        "INPUT": "#000012",
        "TEXT_INPUT": "#8888FF",
        "SCROLL": "#F2EFE8",
        "BUTTON": ("#000000", "#CCCCFF"),
        "PROGRESS": ("#FFFFFF", "#111122"),
        "BORDER": 1,
        "SLIDER_DEPTH": 0,
        "PROGRESS_DEPTH": 0,
    }

    sg.theme_add_new("Dashboard", theme_dict)
    sg.theme("Dashboard")

    BORDER_COLOR = "#111122"
    DARK_HEADER_COLOR = "#111133"
    BPAD_TOP = ((20, 20), (20, 10))
    BPAD_LEFT = ((20, 10), (0, 0))
    BPAD_LEFT_INSIDE = (0, (5, 0))
    BPAD_RIGHT = ((10, 20), (10, 0))
    NAME_SIZE = 23

    def name(name):
        dots = NAME_SIZE - len(name) - 2
        return sg.Text(
            name + " " + "•" * dots,
            size=(NAME_SIZE, 1),
            justification="r",
            pad=(0, 0),
            font="Courier 10",
        )

    top_banner = [
        [
            sg.Text(
                "Dashboard",
                font="Any 20",
                background_color=DARK_HEADER_COLOR,
                enable_events=True,
                grab=False,
            ),
            sg.Push(background_color=DARK_HEADER_COLOR),
            sg.Text(
                "Wednesday 27 Oct 2021",
                font="Any 20",
                background_color=DARK_HEADER_COLOR,
            ),
        ],
    ]

    top = [
        [sg.Push(), sg.Text("EV3 Base Station", font="Any 20"), sg.Push()],
        [sg.T("This Frame has a relief while the others do not")]
    ]

    block_3 = [
        [sg.Text("Block 3", font="Any 20")],
        [sg.Input(), sg.Text("Some Text")],
        [sg.Button("Go"), sg.Button("Exit"), sg.Button("Plot")],
    ]

    block_2 = [
        [sg.Text("EV3 Status", font="Any 20")],
        [name("Heading [deg]"), sg.Text("-", key="hdg_text")],
        [name("Range [cm]"), sg.Text("-", key="range_text")],
        [name("Speed [m/sec]"), sg.Text("-", key="speed_text")],
    ]

    block_4 = [[sg.Text("Block 4", font="Any 20")], [sg.pin(sg.Image(key='-IMAGE-'))]]

    layout = [
        [
            sg.Frame(
                "",
                top_banner,
                pad=(0, 0),
                background_color=DARK_HEADER_COLOR,
                expand_x=True,
                border_width=0,
                grab=True,
            )
        ],
        [
            sg.Frame(
                "",
                top,
                size=(920, 100),
                pad=BPAD_TOP,
                expand_x=True,
                relief=sg.RELIEF_GROOVE,
                border_width=1,
            )
        ],
        [
            sg.Frame(
                "",
                [
                    [
                        sg.Frame(
                            "",
                            block_2,
                            size=(200, 150),
                            pad=BPAD_LEFT_INSIDE,
                            border_width=1,
                            expand_x=True,
                            expand_y=True,
                        )
                    ],
                    [
                        sg.Frame(
                            "",
                            block_3,
                            size=(200, 150),
                            pad=BPAD_LEFT_INSIDE,
                            border_width=1,
                            expand_x=True,
                            expand_y=True,
                            element_justification="c",
                        )
                    ],
                ],
                pad=BPAD_LEFT,
                background_color=BORDER_COLOR,
                border_width=0,
                expand_x=True,
                expand_y=True,
            ),
            sg.Column(
                block_4,
                size=(1024, 1024),
                pad=BPAD_RIGHT,
                expand_x=True,
                expand_y=True,
                grab=True,
            ),
        ],
        [sg.Sizegrip(background_color=BORDER_COLOR)],
    ]

    window = sg.Window(
        "EV3 Control Base Station",
        layout,
        margins=(0, 0),
        background_color=BORDER_COLOR,
        no_titlebar=True,
        resizable=True,
        finalize=True,
        right_click_menu=sg.MENU_RIGHT_CLICK_EDITME_VER_LOC_EXIT,
    )

    def on_ultra_message(the_client, user_data, msg):
        print(msg.topic, msg.payload.decode("utf-8"))

        if msg.topic == "ev3/sensor/ultra":
            decode_msg = msg.payload.decode("utf-8")
            u_msg = json.loads(decode_msg)
            robot.ultra_sample(u_msg[1],u_msg[2])
            #window.write_event_value("range_text", 0)
            #draw_figure(window['-IMAGE-'], your_matplotlib_code(robot.get_map_grid()))

    def on_hdg_message(theClient, userdata, msg):
        print(msg.topic, msg.payload.decode())
        if msg.topic == "ev3/sensor/hdg":
            decode_msg = msg.payload.decode("utf-8")
            u_msg = json.loads(decode_msg)
            robot.heading_sample(u_msg[1])
            window.write_event_value("hdg_text", 0)

    def on_accel_message(theClient, userdata, msg):
        print(msg.topic, msg.payload.decode())

    # This is the Subscriber
    def on_connect(client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        # client.subscribe("ev3/#")

    # if msg.payload.decode() == "Hello world!":
    #            print("Yes!")
    #            theClient.disconnect()"""

    # create and set up a MQTT client to communicate with the EV3
    client = mqtt.Client()
    client.on_connect = on_connect
    # client.on_message = on_message

    client.connect("localhost", 1883, 60)

    client.subscribe("ev3/sensor/ultra", 0)
    client.subscribe("ev3/sensor/accel", 0)
    client.subscribe("ev3/sensor/hdg", 0)

    client.message_callback_add("ev3/sensor/ultra", on_ultra_message)
    client.message_callback_add("ev3/sensor/accel", on_accel_message)
    client.message_callback_add("ev3/sensor/hdg", on_hdg_message)

    client.loop_start()

    #############
    # sg.theme('DarkAmber')

    # client.loop_forever()
    # Event Loop to process "events" and get the "values" of the inputs
    while True:  # Event Loop
        event, values = window.read()
        print(event, values)

        if event == sg.WIN_CLOSED or event == "Exit":
            break
        elif event == "range_text":
            val = robot.get_ultra_range()
            print("range_text:", val)
            window["range_text"].update(val)
            window["hdg_text"].update(robot.get_heading())
            #draw_figure(window['-IMAGE-'], your_matplotlib_code(robot.get_map_grid()))
            
            #window['-IMAGE-'].update(visible=True)
        elif event == "hdg_text":
            val = robot.get_heading()
            print("hdg_text:", val)
            window["hdg_text"].update(val)
        elif event == 'Go':
            draw_figure(window['-IMAGE-'], your_matplotlib_code(robot.get_map_grid()))
            window["hdg_text"].update(robot.get_heading())
            window["range_text"].update(robot.get_ultra_range())
            window['-IMAGE-'].update(visible=True)
        elif event == 'Plot':
            robot.map_grid.plot_grid()
        elif event == "Edit Me":
            sg.execute_editor(__file__)
        elif event == "Version":
            sg.popup_scrolled(sg.get_versions(), keep_on_top=True)
        elif event == "File Location":
            sg.popup_scrolled("This Python file is:", __file__)
    window.close()
    #print(robot.get_map_grid())
    print('End Program')

if __name__ == "__main__":
    main()
