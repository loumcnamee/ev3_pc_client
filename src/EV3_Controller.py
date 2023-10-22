#!/usr/bin/env python3
# This program runs on host computer and connects to an RPyC server running on 
# the EV3 device

#  python -m venv .venv
#  .venv\Scripts\activate
#  python -m pip install --upgrade pip
#  pip install python-ev3dev2
# pip install paho-mqtt

import json
import logging
#import numpy as np
import paho.mqtt.client as mqtt
import occupancy_grid as grid


# d88888b db    db d8888b.  .o88b.  .d88b.  d8b   db d888888b d8888b.  .d88b.  db      
# 88'     88    88 VP  `8D d8P  Y8 .8P  Y8. 888o  88 `~~88~~' 88  `8D .8P  Y8. 88      
# 88ooooo Y8    8P   oooY' 8P      88    88 88V8o 88    88    88oobY' 88    88 88      
# 88~~~~~ `8b  d8'   ~~~b. 8b      88    88 88 V8o88    88    88`8b   88    88 88      
# 88.      `8bd8'  db   8D Y8b  d8 `8b  d8' 88  V888    88    88 `88. `8b  d8' 88booo. 
# Y88888P    YP    Y8888P'  `Y88P'  `Y88P'  VP   V8P    YP    88   YD  `Y88P'  Y88888P 

class EV3Supervisor:
    """Class containing superise an EV3 robot via a MQTT interface"""

    # map_grid = np.random.random([1024, 1024])

    def __init__(self):
        
        logging.basicConfig(filename='EV3Control.log', encoding='utf-8', level=logging.DEBUG, \
                            format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
        self.ultra_range = 0.0 # ultrasonic range sensor reading
        self.x = 256
        self.y = 256
        self.heading = 0.0
        self.map_grid = grid.Occupancy_Grid(8,8,0.01)
        self.connected = False
        self.heading_record = False
        self.heading_history = []

        # create and set up a MQTT client to communicate with the EV3
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        
        # client.on_message = on_message

        self.new_ultra_message = False
        self.new_heading_message = False

    def connect_mqtt(self):
        """Attempt connection to the MQTT server"""
        self.client.connect("localhost", 1883, 60)
        self.client.loop_start()


    # This is the Subscriber
    def on_connect(self, client, userdata, flags, rc):
        """Called when the client connects to the MQTT server
        Set up topic subscriptions and callbacks"""
        self.connected = True

        logging.info("Connected flags % s result code %s client1_id %s userdata %s", str(flags),\
                      str(rc), str(client), str(userdata))
        client.connected_flag=True
        print("Connected to MQTT Broker!")
        self.client.subscribe("ev3/sensor/ultra", 0)
        self.client.subscribe("ev3/sensor/accel", 0)
        self.client.subscribe("ev3/sensor/hdg", 0)

        self.client.message_callback_add("ev3/sensor/ultra", self.on_ultra_message)
        self.client.message_callback_add("ev3/sensor/accel", self.on_accel_message)
        self.client.message_callback_add("ev3/sensor/hdg", self.on_hdg_message)
        
        
        # client.subscribe("ev3/#")

    def disconnect_mqtt(self):
        """Terminate connection with the MQTT server"""
        self.client.loop_stop()
        self.connected = False

    def ultra_sample(self, hdg, data):
        """add a new range sample from the ultrasonic sensor"""
        self.ultra_range = data/100
        self.heading = hdg
        #x_occ = math.floor(self.x + self.ultra_range*math.cos(hdg*math.pi/180))
        #y_occ = math.floor(self.y + self.ultra_range*math.sin(hdg*math.pi/180))
        #self.map_grid[x_occ, y_occ] = (self.map_grid[x_occ, y_occ] + 1)/2
        self.map_grid.sensor_reading(256, 256, hdg, 10, 0.1, self.ultra_range, 2.55, 0.01)
        #print("map grid update:", x_occ, y_occ, self.map_grid[x_occ, y_occ])

    def get_ultra_range(self):
        """return the last report ultra sonic range in [cm]"""
        return self.ultra_range

    def heading_sample(self, data):
        """add a new heading sample from the compass sensor"""
        self.heading = data
        self.heading_history.append(data)

    def get_heading(self):
        """return the last report ultra sonic range in [cm]"""
        if self.new_heading_message == True:
            self.new_heading_message = False
        return self.heading

    def get_map_grid(self):
        """return the robot map occupancy grid geerated from sensor data"""
        return self.map_grid.get_map()

    def get_position(self):
        """Retrieve the world coordnates of the Robot"""
        return [self.x, self.y]

    def is_connected_to_mqtt(self):
        """Returns True if the MQTT client is connected"""
        return self.connected

    def on_ultra_message(self, the_client, user_data, msg):
        """Message handler for a ultrasonic message from the robot"""
        logging.debug(msg.topic, msg.payload.decode("utf-8"), the_client, user_data)

        if msg.topic == "ev3/sensor/ultra":
            decode_msg = msg.payload.decode("utf-8")
            u_msg = json.loads(decode_msg)
            self.ultra_sample(u_msg[1],u_msg[2])
            self.new_ultra_message = True
            # indicate update of data for GUI
            #draw_figure(window['-IMAGE-'], your_matplotlib_code(robot.get_map_grid()))

    def on_hdg_message(self, theClient, userdata, msg):
        print(msg.topic, msg.payload.decode())
        if msg.topic == "ev3/sensor/hdg":
            decode_msg = msg.payload.decode("utf-8")
            u_msg = json.loads(decode_msg)
            self.heading_sample(u_msg[1])
            self.new_heading_message = True

    def on_accel_message(self, theClient, userdata, msg):
        print(msg.topic, msg.payload.decode())

    def runAccelTest(self, duration=0):
        self.client.publish("ev3/control/accel_test", str(duration))
    
    def runUltraScan(self, duration=0):
        self.client.publish("ev3/control/ultra_test", str(duration))
    
    def stop_robot(self):
        self.client.publish("ev3/control/stop",str(0))

    def calibrate_compass(self):
        self.client.publish("ev3/control/cal_compass",str(0))

        

    # if msg.payload.decode() == "Hello world!":
    #            print("Yes!")
    #            theClient.disconnect()"""
