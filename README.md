## Project: CG2Sheets
### CustomGames to Google Sheets 
A bunch of scipts that helps you logging your Scrim data onto your GoogleSheets

in ./sheets/Scripts you can find: <br>
|file| what it does|
|---------------|-------------------------------------------------------------------------------------------|
|LCUDriver.py  | connects to your league of legends Client in order to fetch the private-CustomGame data|
|CGFormater.py | parses the data.json in a readable table and also creates a csv to copy the data manualy|
|CGAPI.py      |connects to your googleSheets and pastes the data without overwriting existing data|
|CGAPIkeys.json|https://youtu.be/zCEJurLGFRk?si=d3y0o-ChmPQCt0Vu&t=115 follow the tutorial until min6:45|
### how to execute 
1.
  follow the [tutorial](https://youtu.be/zCEJurLGFRk?si=d3y0o-ChmPQCt0Vu&t=115) until min 6:45

2.
```
pip install lcu-driver requests google-api-python-client google-auth-httplib2 google-auth-oauthlib gspread
```
3.
```
python CGAPI.py
```
4. 
  copy the gameid from your custom game inside your leagueclient (top middle) and taddaaa



### author: namophoenix
