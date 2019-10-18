# Printing picture on OT2
#### working with computer
- login to ccl computer (password taped to comp)
- double click generate_robot_script.sh (on desktop)
- click run in terminal
- follow script
    - how much art (1 - 9) -- (how many submissions u want to print)
    - this will give you a picece of art (frist in first out)
    - use correct slot for correct picture file
    - leave terminal open (dont press enter)
- open Opentrons.APPimage (on desktop) -- to find robot IP address
    - click robot (top left)
    - flip switch button icon to connect to robot through wifi
    - in pannel find connectivity setting 
    - find wireless ip addres ex:```100.64.66.219``` (dont grab numbers after /)
- open firefox
    - paste ip from opentron.appimage
    - add: ```:48888``` (this is port)
-follow jupyter notebook 
    - click ```upload``` (in top right corner)
    - grad picture you generated (cross check with terminal output)
    - press upload next to file (blue button)
    - click jupyter link --> new tab will open
- follow BioArt Artistic procedure
    - run jupyter cells: place cursor in cell and click shift enter (wait for number to finish)
    - cell 4 takes a long time (start getting labware together while 4 runs)
    - cell 5 actually runs procedure so wait for everything to be in place before running

#### Setting up opentron for printing
prep for biosafety hood
**before you enter cabinet!!!!**
- get one package of canvases plates (artbot poured plates) (agar rectgangle plates on artbot shelf)
- get one package of "palatte" plates (to hold liquid culture)
- get bacteria cultures
- sterilize and place needed material in hood

**when your in biosafety hood - (only use if trained)**
- take out as many plates as you need
- add 5ml liquid culture of bacteria to wells in "palatte" plate
- order: (START AT TOP LEFT CORNER) 
    - A1 = PINK, A2 = BLUE, A3 = TEAL
    - B1 = PEACH, B2 = FLOURESCENT

**ENTER OPENTRON**
- spray with alcohol 
- place sterile material from biosafety hood into opentron
- place "palette" into slot 11
- place canvases into correctly numbered slots
- check pipet tips in slot 1 -- **need pipet tips in left column!**
- take off all lids
- slowly close opentron door (preventing airflow)
- run cell 5 from jupyter notebook

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