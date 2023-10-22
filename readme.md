# Base station for an EV3 mobile robot

This is a Python application which communicates with a Lego EV3 mobile via MQTT


[![Influenced by the Robotics Toolbox](https://raw.githubusercontent.com/petercorke/robotics-toolbox-python/master/.github/svg/rtb_powered.min.svg)](https://github.com/petercorke/robotics-toolbox-python)

[![Powered by the EV3Dev2](https://github.com/petercorke/spatialmath-python/raw/master/.github/svg/sm_powered.min.svg)](https://github.com/petercorke/spatialmath-python)

[![Powered by the PyQtGraph] (https://github.com/pyqtgraph) ] 

[![Powered by the Spatial Math Toolbox](https://github.com/petercorke/spatialmath-python/raw/master/.github/svg/sm_powered.min.svg)](https://github.com/petercorke/spatialmath-python)

[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)


### Task List
1. Separate data updates and commands into separate threads [Done] 
- Acoomplished this by splitting robot control functionality into EV3_COntroller and refactoring the UI using PyQt5
- set up UI update at 1 sec rate using QTimer 
- UI update and control messages executed in main thread
- response messages processed in secondary thread created by MQTT
2. Add command infrastructure [Done]
3. Ultrasound experiemnt [Done]
- build up occupancy grid while robot rotates in place
4. Acclerometer experiment 

## References
### Key References
- https://eclipse.dev/paho/index.php?page=clients/python/docs/index.php
- https://github.com/ev3dev/ev3dev-lang-python
- https://doc.qt.io/qtforpython-5/index.html
- https://ev3dev-lang.readthedocs.io/projects/python-ev3dev/en/stable/index.html

### Misc References
- https://www.pythonguis.com/tutorials/plotting-pyqtgraph/
- https://peps.python.org/pep-0008/
- https://google.github.io/styleguide/pyguide.html