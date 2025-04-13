import time
from LCUDriver import fetch_game_data, get_content

if __name__ == "__main__":
    print("Drücke 'q' zum Beenden.")

    while True:
        gid = input("Welche gameId möchtest du abrufen? ")

        if gid.lower() == "q":
            print("Beende das Programm.")
            break

        fetch_game_data(gid)

        # Warten bis Daten geladen sind
        while get_content() is None:
            print("Warte auf Daten ...")
            time.sleep(1)

        print("Match-Daten:")
        print(get_content())

        # Optional: Zurücksetzen, damit bei nächster Eingabe wieder gewartet wird
        # Nur nötig, wenn `get_content()` nicht in `LCUDriver` zurückgesetzt wird
        # z.B.:
        # LCUDriver.game_content = None
