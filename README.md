## Project: CG2Sheets
### Import Matches to Google Sheets
A program that automatically imports your League of Legends match data into Google Sheets.

### Description
This program connects to the League of Legends client and retrieves match data from matches including official PrimeLeague games and custom games. 
It then formats this data into a readable table and uploads it to your selected Google Sheet. 
The program is designed to be user-friendly and requires minimal setup.

You can find following scripts in ./sheets/Scripts:

| file                    | what it does                                                                              |
|-------------------------|-------------------------------------------------------------------------------------------|
| LCUDriver.py            | Connects to your League of Legends Client in order to fetch the match data                |
| CustomGameJSONParser.py | Parses the data.json in a readable table and _also creates a csv to copy the data manually_ |
| GoogleAPIConnector.py   | Connects to your Google Sheet and pastes the data without overwriting existing data       |
| main.py                 | The program that has to be executed to start the app.                                     |
### How to run the program

1. Install Python if you haven't installed python yet.
   - Download the latest version of Python from the official website: [python.org](https://www.python.org/downloads/)
   - Follow the installation instructions for your operating system.
   - Make sure to check the box that says "Add Python to PATH" during installation.

2. Start the League of Legends client and log in to your account.

3. Download the newest [release](https://github.com/NamoPhoenix/LolMatchScraper/releases/tag/LolMatchScraper-1.0.0) and extract the folder onto your computer

4. For the script to automatically upload the match-table onto your personal Google Sheets follow this [tutorial](https://youtu.be/zCEJurLGFRk?si=d3y0o-ChmPQCt0Vu&t=115) until min 6:45
   - Insert the contents of the downloaded json from the tutorial at minute 5:11 into the file called `CGAPIkeys.json`.

5. Open the extracted folder and edit the file called `config.py`. Change the value for the key 'google_sheets_link' with your Google Sheets link. 
   - Make sure to keep the quotation marks around the link. 
   - The link should look something like this: `https://docs.google.com/spreadsheets/d/your_sheet_id/edit#gid=0`
   - Change the value for the key 'google_sheets_name' to the name of your page/sheet within your Document (not  the name of the whole spreadsheet at the top left but the name at the lower index tab)
   - you can also update the league of legends patch by changing the key 'patch_id' 


6. Run the `main.exe` file.
   
7. Copy the game ID from the League of Legends client and paste it into the terminal when prompted. 
   - The script will then fetch the match data and upload it to your Google Sheet.

   
### Author: NamoPhoenix and Sepia2023
