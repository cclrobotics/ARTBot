http://www.bioartbot.org/

# BioArtBot Robotic Artist from Counter Culture Labs
This project provides an interface for users to draw and submit pixel art via a web app, and then converts that submission into instructions for an [Opentrons OT2 robot](https://www.opentrons.com) to reproduce that drawing by distributing colorful micobes onto an agar plate. As the microbes grow, the picture comes into focus, resulting in living art. It's very neat.

The code breaks into three sections, each of which can be run independently:
- Web app to create drawings
- Translation code to produce instructions for the robot
- Lab protocols to grow color-producing microbes

## Web

### prerequisites
- Install [Docker compose](https://docs.docker.com/compose/install/)

### to run locally
```bash
docker-compose up -d --build                                       # build and spin up containers
docker-compose exec artbot flask db upgrade                                 # setup database
```
### to inspect the database
```bash
docker-compose exec artbot-db psql -U postgres -d artbot_dev
```
### to access the application
- go to `localhost:5001` for the web interface
- go to `localhost:1080` for the mail-dev client (inspect outgoing e-mails)

#### if you contribute code
Changes to the data models must be accompanied by a migration script which you can generate by running:
```bash
docker-compose exec artbot flask db migrate -m "short description"
```

The script will be created in migrations/versions. Please inspect the file, change it if required, and test it by running:
```bash
docker-compose exec artbot flask db upgrade
docker-compose exec artbot flask db downgrade                   # check backward compatibility
```
Use the logs to check for any errors during the migration:
```bash
docker-compose logs arbot
```

### Troubleshooting
#### Trouble generating the migration script
Might require updating the `migrations/versions` folder permissions, to give Docker write access
```bash
chown :1024 migrations/versions                 # set group permissions to gid shared with docker
```

### Screenshot
![ARTBot Screenshot](/ARTBotScreenShot.png?raw=true "ARTBot Screenshot")

## Robot

### To run:
With the web containers running, execute these commands:
```bash
mkdir robot/procedures
chown :1024 robot/procedures
docker-compose exec artbot python run_procedure_generator.py
```
The generated procedure will be timestamped and saved in _procedures_ folder

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
