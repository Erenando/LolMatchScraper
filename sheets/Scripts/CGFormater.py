import json
import csv # Importiert das Modul zum Arbeiten mit CSV-Dateien
import os  # Importiert das os Modul für Dateipfad-Operationen

# --- Konfiguration ---
# Name der JSON-Datei, die die Spieldaten enthält
input_file_path = 'message.txt'
# Name der CSV-Datei, in die die Ergebnisse gespeichert werden sollen
output_file_path = 'game_stats_all_players.csv'
# Trennzeichen für die CSV-Datei (Semikolon, wie in der vorherigen Anfrage)
# Ändere dies zu ',' wenn du ein Standard-Komma-getrenntes CSV möchtest.
csv_delimiter = ';'

# --- Daten laden ---
try:
    # Öffnet die Eingabedatei im Lesemodus ('r') mit UTF-8-Kodierung
    with open(input_file_path, 'r', encoding='utf-8') as f:
        # Lädt die JSON-Daten aus der Datei
        data = json.load(f)
        print(f"Daten erfolgreich aus '{input_file_path}' geladen.")
except FileNotFoundError:
    # Fehlermeldung, wenn die Datei nicht gefunden wird
    print(f"Fehler: Die Datei '{input_file_path}' wurde nicht gefunden.")
    print(f"Stelle sicher, dass die Datei im selben Verzeichnis wie das Skript liegt oder gib den korrekten Pfad an.")
    exit() # Beendet das Skript
except json.JSONDecodeError:
    # Fehlermeldung, wenn die Datei kein gültiges JSON enthält
    print(f"Fehler: Die Datei '{input_file_path}' enthält kein gültiges JSON-Format.")
    exit() # Beendet das Skript
except Exception as e:
    # Fängt alle anderen möglichen Fehler beim Laden ab
    print(f"Ein unerwarteter Fehler ist beim Laden der Datei aufgetreten: {e}")
    exit() # Beendet das Skript

# --- Spieler-Namen-Lookup erstellen ---
# Erstellt ein Dictionary, um participantId zu gameName zuzuordnen
player_names = {}
# Durchläuft die Liste 'participantIdentities'
for identity in data.get('participantIdentities', []):
    # Holt die participantId
    participant_id = identity.get('participantId')
    # Holt den gameName aus dem 'player'-Objekt
    game_name = identity.get('player', {}).get('gameName', 'UnknownPlayer') # Standardwert falls Name fehlt
    # Fügt die Zuordnung zum Dictionary hinzu, wenn die ID gültig ist
    if participant_id is not None:
        player_names[participant_id] = game_name

print(f"{len(player_names)} Spieleridentitäten gefunden.")

# --- Daten extrahieren und in CSV schreiben ---
# Definiert die Kopfzeile für die CSV-Datei (mit GameName als erster Spalte)
header = [
    "GameName","Win/loss", "Side", "Champion", "K", "D", "A", "DMG Dealt", "DMG Taken",
    "Wards Placed", "Wards Destroyed", "Control Wards", "Gold Earned",
    "CS", "Kill Count", "Game Duration"
]

# Berechne die Spieldauer in Minuten einmalig
game_duration_seconds = data.get('gameDuration', 0)
game_duration_minutes = game_duration_seconds / 60.0 if game_duration_seconds > 0 else 0

try:
    # Öffnet die CSV-Datei im Schreibmodus ('w')
    # newline='' verhindert leere Zeilen zwischen den Datenzeilen in der CSV
    # encoding='utf-8' stellt sicher, dass Sonderzeichen korrekt gespeichert werden
    with open(output_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        # Erstellt ein csv.writer-Objekt mit dem definierten Trennzeichen
        csv_writer = csv.writer(csvfile, delimiter=csv_delimiter)
        data_table = []
        # Schreibt die Kopfzeile in die CSV-Datei
        csv_writer.writerow(header)
        print(f"Schreibe Daten in '{output_file_path}'...")

        # Durchläuft die Liste 'participants'
        for participant in data.get('participants', []):
            # Holt die participantId für den aktuellen Teilnehmer
            participant_id = participant.get('participantId')
            # Holt das 'stats'-Objekt
            stats = participant.get('stats')
            # Holt die 'championId'
            champion_id = participant.get('championId')

            # Wenn keine ID oder keine Stats vorhanden sind, überspringe diesen Teilnehmer
            if participant_id is None or stats is None:
                print(f"Warnung: Überspringe Teilnehmer ohne ID oder Stats.")
                continue

            # Hole den Spielernamen aus dem Lookup-Dictionary
            game_name = player_names.get(participant_id, f'UnknownPlayerID_{participant_id}')

            # Extrahiere die Statistiken (mit Standardwerten bei fehlenden Daten)
            champion = champion_id if champion_id is not None else 'N/A'
            k = stats.get('kills', 0)
            d = stats.get('deaths', 0)
            a = stats.get('assists', 0)
            dmg_dealt = stats.get('totalDamageDealtToChampions', 0) # Schaden an Champions
            dmg_taken = stats.get('totalDamageTaken', 0)
            wards_placed = stats.get('wardsPlaced', 0)
            wards_destroyed = stats.get('wardsKilled', 0) # Feld heißt 'wardsKilled'
            control_wards = stats.get('visionWardsBoughtInGame', 0) # Gekaufte Kontrollwards
            gold_earned = stats.get('goldEarned', 0)
            # CS = Vasallen + neutrale Monster
            cs = stats.get('totalMinionsKilled', 0) + stats.get('neutralMinionsKilled', 0)
            kill_count = k # 'Kill Count' ist dasselbe wie 'Kills'

            # Team Statistiken
            wl = 'W' if stats.get('win', False) else 'L' # Gewonnen oder verloren
            side_nr = participant.get('teamId', '000') # Team-ID (1 oder 2)
            side = 'Blue' if side_nr == 100 else 'Red' if side_nr == 200 else 'Unknown'
            cspm = round(cs / game_duration_minutes, 2) if game_duration_minutes > 0 else 0.0
            # Erstellt die Datenzeile als Liste in der Reihenfolge der Kopfzeile
            data_row = [
                game_name,wl, side, champion, k, d, a, dmg_dealt, dmg_taken,
                wards_placed, wards_destroyed, control_wards, gold_earned,
                cs, kill_count, game_duration_minutes
            ]

            # Schreibt die Datenzeile in die CSV-Datei
            csv_writer.writerow(data_row)
            data_table.append(data_row)

        print(f"CSV-Datei '{output_file_path}' erfolgreich erstellt.")

except IOError:
    # Fehlermeldung, wenn die CSV-Datei nicht geschrieben werden kann (z.B. keine Berechtigung)
    print(f"Fehler: Konnte nicht in die Datei '{output_file_path}' schreiben.")
except Exception as e:
    # Fängt alle anderen möglichen Fehler beim Schreiben ab
    print(f"Ein unerwarteter Fehler ist beim Schreiben der CSV-Datei aufgetreten: {e}")

def get_data_table():
    return data_table
