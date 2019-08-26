# ARTBot Robotic Artist
This repo holds code for CCL's ARTBot project. The project takes advantage of the open-source nature of
the [Opentrons OT2 robot](https://www.opentrons.com) - it converts a picture drawn in an online editor submitted
as a JSON into a protocol to draw that picture on an agar art tray.

## To run locally:
- Create a virtual environment: ```python3 -m venv <path to new virtual env> ```
- Activate the virtual environment: ```source <path to new venv>/bin/activate```
- Install the Python packages to the virtual environment: ```pip3 install -r requirements.txt```
- Run the server: ```python3 web/run.py```
- Go to ```127.0.0.1:5000``` in your browser.
Note: don't forget to add your virtual environment to the gitignore before you push.

## Screenshot
![ARTBot Screenshot](/ARTBotScreenShot.png?raw=true "ARTBot Screenshot")
