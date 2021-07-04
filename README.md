# Mario Golf Super Rush Caddy - Multiplayer Score Parser
## Installation/Pre Setup
1. Update OBS. Ensure you are running a more recent release
2. Install [OBS Virtual Cam](https://github.com/Fenrirthviti/obs-virtual-cam/releases). (This is slightly different from the built in Virtual Cam)
3. When prompted, install at least 1 virtual camera.

## Google Sheets Output Setup

1. Follow this guide to create a [Google Cloud Platform project + Enable the Google Sheets API](https://developers.google.com/workspace/guides/create-project)

2. Go back to the APIs & Services page. On the lefthand bar, select Credentials.
Click 'Create Credentials' and select OAuth client ID. Select Desktop app as the Application type. Enter `mario-golf-super-rush-caddy` as the name.

3. Once you've created the credentials, you can download them as a JSON file. You will use this file for authenticating via the application.
Keep these credentials secret and do not upload them anywhere. They will have read and write access to your Google Sheets documents.


## Usage
This program uses CV2 VideoCapture. Your computer's webcams and virtual cameras are accessed using an index. If you have a built-in webcam, it is typically index **0**. In general, the index of your first installed virtual camera is **1**, but this may differ between systems. 

1. For best results, disable screen burn-in reduction (the screen dimming after 5 minutes) and notifications in Switch system settings. 

2. Enable the OBS virtual camera for your desired scene. There are two ways to do this:
    - To broadcast the currently active scene, go to the top bar and under Tools, select VirtualCam. Select your desired target camera and press Start.
    - To broadcast a non-active scene, right click the desired scene, and go to Filters. Add the filter VirtualCam, select your desired target camera, and press start.
    
3. Don't edit any scene you are currently parsing.

4. Run `parse_superrush_multiplayer.exe`

5. Preview your Virtual Cam output by selecting a VCam index and clicking `Preview VCam`. Ensure you can see your screen capture. Press ESC to exit the preview.

6. Select an output type:
    - Text File outputs player data as a CSV to the folder `/mgsr-events/` with rows in the format `Score,Hole`
    - Google Sheets outputs rows to the configured Google Sheet with rows in the format `Score,Hole`. You may have to allow OAuth access via the pop up window the first time you do this.

7. Select your OBS Output Resolution. This should be the same as the `Output (Scaled) Resolution` in the `Video` tab of OBS Settings.

8. `Start Parsing`! You may see some logs related to 'true_divide', or 'misaligned data'. These warnings can be ignored.

9. Click `Done Parsing` to exit the program. If finishing a parsing session, this updates all players' last played hole to 'F'.