import pytesseract
from PIL import Image
import cv2
import pandas as pd
import os

# Pfad zur Tesseract-Installation (nur falls notwendig)
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Funktion zum Extrahieren von Text aus Bild
def extract_text_from_image(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Optional: Bild verbessern für bessere OCR-Erkennung
    gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]
    text = pytesseract.image_to_string(gray)
    return text

# Beispielhafte Parsing-Logik (vereinfachte Annahmen)
def parse_match_data(text):
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    matches = []

    for line in lines:
        # Beispielhafte Extraktion (Champion, Ergebnis, K/D/A)
        if any(kw in line.lower() for kw in ['victory', 'defeat']):
            parts = line.split()
            # Annahme: Format z. B. "Ahri Victory 7/2/5"
            champion = parts[0]
            result = parts[1]
            kda = next((p for p in parts if '/' in p), "0/0/0")
            kills, deaths, assists = map(int, kda.split('/'))
            matches.append({
                'Champion': champion,
                'Result': result.capitalize(),
                'Kills': kills,
                'Deaths': deaths,
                'Assists': assists
            })

    return pd.DataFrame(matches)

# Hauptfunktion
def process_matchhistory_screenshot(image_path):
    print(f"📸 Verarbeite Screenshot: {image_path}")
    text = extract_text_from_image(image_path)
    df = parse_match_data(text)
    print("\n📊 Extrahierte Matchdaten:")
    print(df)
    return df

# Beispiel-Nutzung
if __name__ == "__main__":
    image_path = "matchhistory_screenshot.png"  # Passe hier deinen Screenshot-Pfad an
    df = process_matchhistory_screenshot(image_path)

    # Optional: Speichern (nur wenn du willst)
    # df.to_csv("matchhistory.csv", index=False)
    # df.to_excel("matchhistory.xlsx", index=False)
    # df.to_json("matchhistory.json", orient="records")
