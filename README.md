# ARTBot Robotic Artist from Counter Culture Labs
This project provides an interface for users to draw and submit pixel art via a web app, and then converts that submission into instructions for an [Opentrons OT2 robot](https://www.opentrons.com) to reproduce that drawing by distributing colorful micobes onto an agar plate. As the microbes grow, the picture comes into focus, resulting in living art. It's very neat.

The code breaks into three sections, each of which can be run independently:
- Web app to create drawings
- Translation code to produce instructions for the robot
- Lab protocols to grow color-producing microbes

## Web

### To run locally:
- Create a virtual environment: ```python3 -m venv <path to new virtual env> ```
- Activate the virtual environment: ```source <path to new venv>/bin/activate```
- Install the Python packages to the virtual environment: ```pip3 install -r requirements.txt```
- Set up the database: ```flask db upgrade```
- Run the server: ```python3 run_webserver.py```
- Go to ```127.0.0.1:5000``` in your browser.

#### If you contribute code:
- Add your virtual environment to the gitignore before you push (and your SQLlite file if you have one).
- Run ```export FLASK_APP=web``` (or ```set FLASK_APP=web``` on Windows), folowed by ```flask db migrate``` if you have made any changes to the data models. This will create a script in migrations/versions. Type ```git add [new_file_name]``` to include this in your commit.

### Screenshot
![ARTBot Screenshot](/ARTBotScreenShot.png?raw=true "ARTBot Screenshot")

## Robot

### To run:
- Use same virtual environment as listed above in *Web*
- ARTBot.db SQLite file should be in your ARTBot folder
- Run the script ```python3 art_processor.py```
- Generated procedure will be timestamped and saved in _procedures_ folder

### To upload generated procedure to robot:
- Download official Opentrons app
- First time only: upload _custom_artbot_labware.py_ using OT app
- Upload generated procedure (this will take awhile)
	- Use this time to gather materials for the procedure - see "Lab" section below
- Callibrate as normal, but when calibrating "Canvas" labware, calibrate to top of lid, approximately 10mm from the upper edge and 15mm from the left edge
	- This provides a margin for the microbial growth to spread out a little

If everything works correctly, the pipette tip will _just_ pierce the agar for each pixel it places. This is done on purpose - since it's hard to get precise volume for each agar plate, we just overestimate.

### Troubleshooting
If the pipette tip misses your agar, it's easiest to troubleshoot using the [Jupyter Notebook server](LINK) that the OT2 runs to interact with the robot. In fact, you can generate the template in a Jupyter Notebook instead with ```python3 art_processor.py --notebook```. Once you know the correct distance between the top of the lid and the agar, change it in ART_TEMPLATE.txt

## Lab

### Materials:
- Opentrons OT2 Liquid Handling Robot
- 6-well 15mL tissue culture plates for liquid culture 'palette'
- Omni-tray plates for canvases - one per artpiece
- Standard 200ul tiprack

### Procedure in brief:
- In a sterile environment:
	- Pour LB agar with into omni-tray plates
	- Transfer 5-10 mL of liquid color-producing e. coli culture into a 6-well plate
- Follow instructions in OT app upon upload of procedure
