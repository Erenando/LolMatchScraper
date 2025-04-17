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
| CustomGameJSONParser.py | Parses the data.json in a readable table and also creates a csv to copy the data manually |
| GoogleAPIConnector.py   | Connects to your Google Sheet and pastes the data without overwriting existing data       |
| main.py                 | The program that has to be executed to start the app.                                     |
### how to execute 

1. Install Python if you haven't installed python yet.
   - Download the latest version of Python from the official website: [python.org](https://www.python.org/downloads/)
   - Follow the installation instructions for your operating system.
   - Make sure to check the box that says "Add Python to PATH" during installation.

2. for the script to automatically upload the match-table onto your personal Google Sheets follow this [tutorial](https://youtu.be/zCEJurLGFRk?si=d3y0o-ChmPQCt0Vu&t=115) until min 6:45

3. start the League of Legends client and log in to your account.

4. open a terminal or command prompt and navigate to the directory where the script is located. 
   - You can do this by using the `cd` command followed by the path to the directory. For example:
     ```bash
     cd path/to/your/script
     ```



python CGAPI.py
```
5.
  copy the gameid from your custom game inside your leagueclient (top middle) and taddaaa



### author: gemini xD


| CGAPIkeys.json          | https://youtu.be/zCEJurLGFRk?si=d3y0o-ChmPQCt0Vu&t=115 follow this tutorial until minute 6:45 |
| config.json             | please link your Google Sheets link in this file and also                                     |