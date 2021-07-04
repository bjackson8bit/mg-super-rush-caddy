# Mario Golf Super Rush Caddy - Multiplayer Score Parser
## Installation
1. Update OBS. Ensure you are running a more recent release
2. Install [OBS Virtual Cam](https://github.com/Fenrirthviti/obs-virtual-cam/releases)
3. When prompted, install at least 1 virtual camera
4. Install [Python 3.6+](https://www.python.org/downloads/)
5. Head into the project root directory and run the following command.
```
pip install -r requirements.txt
```

## Setup
This program uses CV2 VideoCapture. Your computer's webcams and virtual cameras are accessed using an index. If you have a built-in webcam, it is typically index **0**. In general, the index of your first installed virtual camera is **1**, but this may differ between systems. Follow the below instructions to configure your virtual camera.

9. Set up your overhead spectator camera in Splatoon 2. For best results, disable screen burn-in reduction (the screen dimming after 5 minutes) and all notifications in Switch system settings. Don't move the camera or change perspectives while parsing.


11. You may see some logs related to 'true_divide', or 'misaligned data'. These errors can be ignored. As long as the script continues running, it will work. Yay coding :)

12. Results will be output in the project root directory under the **/events/** folder.

13. Click `Done Parsing` to exit the program.


## Understanding the Output

### Example Output (Abridged for simplicity)