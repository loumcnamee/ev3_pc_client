#!/usr/bin/env python3
# This program runs on host computer and connects to an RPyC server running on 
# the EV3 device

#  python -m venv .venv
#  .venv\Scripts\activate
#  python -m pip install --upgrade pip
#  pip install python-ev3dev2
# pip install paho-mqtt


import io
import math
import time
import PySimpleGUI as sg

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasAgg
import EV3_Controller as ev3



def the_thread(window: sg.Window, map_data):
    """
    The thread that communicates with the application through the window's events.

    Because the figure creation time is greater than the GUI drawing time, it's safe
    to send a non-regulated stream of events without fear of overrunning the communication queue
    """
    while True:
        fig = your_matplotlib_code(map_data)
        buf = draw_figure(fig)
        window.write_event_value("-THREAD-", buf)  # Data sent is a tuple of thread name and counter

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


def draw_figure(figure):
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
        #element.update(data=buf.read())
        return buf
    else:
         return None

# .88b  d88.  .d8b.  d888888b d8b   db 
# 88'YbdP`88 d8' `8b   `88'   888o  88
# 88  88  88 88ooo88    88    88V8o 88
# 88  88  88 88~~~88    88    88 V8o88
# 88  88  88 88   88   .88.   88  V888
# YP  YP  YP YP   YP Y888888P VP   V8P

def main():
    """main"""
    robot = ev3.EV3Supervisor()

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
            justification="l",
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
        [name("Stats"), sg.Text("-", key="stat_text")]
    ]

    block_3 = [
        [sg.Text("Block 3", font="Any 20")],
        [sg.Input(), sg.Text("Some Text")],
        [sg.Button("Go"), sg.Button("Exit"), sg.Button("Plot"),sg.Button("AccelTEst")],
    ]

    block_2 = [
        [sg.Text("EV3 Status", font="Any 20")],
        [name("Heading [deg]"), sg.Text("-", key="hdg_text")],
        [name("Range [cm]"), sg.Text("-", key="range_text")],
        [name("Speed [m/sec]"), sg.Text("-", key="speed_text")]
    ]

    block_4 = [[sg.Text("Block 4", font="Any 20")], [sg.pin(sg.Image(key="-IMAGE-"))]]

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
                            size=(300, 150),
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
            [sg.Column(
                block_4,
                size=(1024, 1024),
                pad=BPAD_RIGHT,
                expand_x=True,
                expand_y=True,
                grab=True,
            ),
        ],
        [sg.Sizegrip(background_color=BORDER_COLOR)],
    ] ]


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



    #############
    # sg.theme('DarkAmber')

    # client.loop_forever()
    counter = start_time = delta = 0
    # Event Loop to process "events" and get the "values" of the inputs 
    window["-IMAGE-"].update(visible=True)
    start_time = time.time()
    window.start_thread(lambda: the_thread(window, robot.get_map_grid()), "-THEAD FINISHED-")

    while True:  # Event Loop
        event, values = window.read()
        print(event, values)
        if event == sg.WIN_CLOSED or event == "Exit":
            break
        sg.timer_start()
        if event == "-THREAD-":
            plt.close('all')  # close all plots... unclear if this is required
            window["-IMAGE-"].update(data=values[event].read())
            counter += 1
            seconds_elapsed = int(time.time() - start_time)
            fps = counter / seconds_elapsed if seconds_elapsed != 0 else 1.0
            window["stat_text"].update(f'Frame {counter} Write Time {delta} FPS = {fps:2.2} seconds = {seconds_elapsed}')
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
        elif event == 'AccelTest':
            duration = 1
            robot.runAccelTest(duration)
            
        elif event == "Edit Me":
            sg.execute_editor(__file__)
        elif event == "Version":
            sg.popup_scrolled(sg.get_versions(), keep_on_top=True)
        elif event == "File Location":
            sg.popup_scrolled("This Python file is:", __file__)
        delta = sg.timer_stop()
    
    
    window.close()
    #print(robot.get_map_grid())
    robot.close_comms()
    print('End Program')

if __name__ == "__main__":
    sg.Window.start_thread = sg.Window.perform_long_operation
    main()
