# Making robot procedures  

Web -> **Robot** -> Lab  

Assuming that you or someone else has already created some art using the web interface, this document describes how to 
turn that data into instructions that the Opentrons OT2 can use to draw that art on agar.

### Generating the procedure

First, you will set up your environment:
- Activate your virtual environment:```source path/to/venv/bin/activate```
- Set your database location:
    - The default is a local Sqlite database. This works if you're just running locally, and will happen automatically
    if you don't provide an alternative.
    - If you need to access a different database, provide the location with
    ```export DATABASE_URL=[your database location]```. On Windows, use```set``` instead of ```export```.

Then simply run the script: ```python3 run_procedure_generator.py```

The output of this script a Python file stored in _ARTBot/robot/procedures_
timestamped with the data and time it was generated.

#### Using a Jupyter Notebook
If you prefer to work in the interactive Jupyter Notbook environment with the robot, run
```python3 run_procedure_generator.py --notebook``` instead. Then your output will be a .ipynb file that you can upload
the OT2 Jupyter server.

### Upload

If this is your first time running a procedure generated this way on your robot, you will need to first upload the file
_custom_artbot_labware_, found in the _robot_ directory. This file defines a few unique pieces of labware that we will
use. You only need to do this once. See _lab_guide_ for more information. You may need to buy different labware, or
change the definition work with what you have.

The generated script is ready to upload directly to the OT2 using the [Opentrons app](www.opentrons.com).
Just follow the prompts on the app.

### Calibration

For the most part, you can calibrate as you normally would, but there is a trick to calibrating the
"canvas" labware - i.e. the tray holding the agar that the robot will draw on. Best practice we have found is:
1. When you are asked to move the pipette tip to position "A1" on this tray, position it about 10mm down from the top
edge and 15mm right of the left edge.
2. Leave the cover on the tray when calibrating and move the pipetter just that the tip just touches the top of the lid.