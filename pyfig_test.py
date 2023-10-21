#!/usr/bin/env python3
# This program runs on host computer and connects to an RPyC server running on 
# the EV3 device


#  python -m venv .venv
#  .venv\Scripts\activate
#  python -m pip install --upgrade pip

from pyfiglet import Figlet
f = Figlet(font='basic')
print(f.renderText('EV3 CONTROLLER'))

print(Figlet.getFonts)