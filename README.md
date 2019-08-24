# ARTBot Robotic Artist
This repo holds code for CCL's ARTBot project. The project takes advantage of the open-source nature of
the [Opentrons OT2 robot](https://www.opentrons.com) - it converts a picture drawn in an online editor submitted
as a JSON into a protocol to draw that picture on an agar art tray.

## To run locally:
- ```python3 -m venv <path to new virtual env> ```
- ```source <path to new venv>/bin/activate```
- ```pip3 install -r requirements.txt```
- ```python3 web/run.py```
