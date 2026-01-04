# LoL Match Scraper

## Projekt-Übersicht
Ein Tool zum automatischen Importieren von League of Legends Match-Daten in Google Sheets. Ideal für PrimeLeague-Teams, Scrims und Custom Games.

## Beschreibung
Dieses Programm ruft Match-Daten entweder direkt über den League Client (LCU) oder via Riot API (Fallback) ab. Die Daten werden formatiert und automatisch in ein Google Spreadsheet hochgeladen, ohne bestehende Daten zu überschreiben.

### System-Komponenten

| Datei | Funktion |
|:--- |:--- |
| `main.py` | Der Haupteinstiegspunkt, der die grafische Benutzeroberfläche (UI) startet. |
| `UI.py` | Die Benutzeroberfläche (CustomTkinter) für Team-Auswahl und Match-ID Eingabe. |
| `LCUDriver.py` | Verbindet sich mit dem LCU (Local Client) oder nutzt die Riot API als Fallback. |
| `CustomGameJSONParser.py` | Verarbeitet die Rohdaten in ein tabellarisches Format für Google Sheets. |
| `GoogleAPIConnector.py` | Verwaltet die Authentifizierung und das Schreiben der Daten in das Sheet. |

---

## Einrichtung

### 1. Google API Vorbereitung
* Folge diesem [Tutorial](https://youtu.be/zCEJurLGFRk?si=d3y0o-ChmPQCt0Vu&t=115) bis Minute 6:45, um ein Service-Konto zu erstellen.
* Benenne die heruntergeladene JSON-Datei in `CGAPIkeys.json` um und lege sie in den Projektordner.

### 2. Konfiguration (`config.json`)
Passe die Datei wie folgt an:
```json
{
  "google_sheets_link": "DEIN_GOOGLE_SHEET_LINK",
  "google_sheets_name": "Stats_",
  "riot_patch_id": "14.24.1",
  "riot_api_key": "DEIN_RIOT_API_KEY",
  "riot_routing_region": "europe"
}
```
* **google_sheets_name**: Der Prefix deiner Tabellenblätter (das Programm hängt den Namen aus der `teams.txt` an).
* **riot_api_key**: Erstelle einen Key auf [developer.riotgames.com](https://developer.riotgames.com/). 
    * **Hinweis:** Um einen permanenten Key zu erhalten, musst du unter "My Software" ein neues **Produkt registrieren** (Personal Project), da der Standard-Key alle 24 Stunden abläuft.

### 3. Teams verwalten (`teams.txt`)
* Schreibe pro Zeile einen Teamnamen in die Datei. Diese erscheinen im Dropdown-Menü der UI, um das Ziel-Tabellenblatt im Google Sheet zu bestimmen.

---

## Nutzung des Programms

1. **Voraussetzung:** Falls du den LCU-Modus nutzt, starte den League of Legends Client und logge dich ein.
2. **Start:** Führe die `LoLMatchScraper.exe` aus.
3. **Eingabe in der UI:**
    * **Team auswählen:** Bestimmt das Ziel-Tabellenblatt im Google Sheet.
    * **Team Blau / Team Rot:** Gib die Namen der beiden Teams ein.
    * **Game ID:** Kopiere die Match-ID aus deinem LoL-Client (Match-Historie) und füge sie ein.
4. **Abschluss:** Klicke auf **"Daten abrufen"**. Das Programm gibt Feedback im Status-Label, sobald der Upload abgeschlossen ist.

---

### Erstellung der Executable (EXE)
Falls du das Projekt selbst als EXE bauen möchtest, verwende diesen Befehl im Terminal:
```bash
pyinstaller --noconsole --onefile --name "LolMatchScraper" --add-data "img;img" --icon "img/ACE_Logo.iso" UI.py
```

### Autor
**Eren** | Discord: **Erenando**