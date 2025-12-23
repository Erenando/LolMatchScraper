import customtkinter as ctk
from tkinter import messagebox
from GoogleAPIConnector import parse_game
import threading
import multiprocessing

# Design-Einstellungen
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Fenster-Konfiguration
        self.title("LoL Match Scraper")
        self.geometry("500x500")

        # Teams aus Datei laden
        self.teams = self.load_teams()

        # --- UI Elemente ---

        # Überschrift Team
        self.label_team = ctk.CTkLabel(self, text="Team auswählen:", font=("Arial", 14, "bold"))
        self.label_team.pack(pady=(30, 5))

        # Dropdown für Teams
        self.team_dropdown = ctk.CTkComboBox(self, values=list(self.teams.values()), width=300)
        self.team_dropdown.pack(pady=10)
        if list(self.teams.values()):
            self.team_dropdown.set(list(self.teams.values())[0])

        # Überschrift Game ID
        self.label_game = ctk.CTkLabel(self, text="Game ID eingeben:", font=("Arial", 14, "bold"))
        self.label_game.pack(pady=(20, 5))

        # Eingabefeld für Game ID
        self.game_id_entry = ctk.CTkEntry(self, placeholder_text="z.B. 7557023906", width=300)
        self.game_id_entry.pack(pady=10)
        self.game_id_entry.bind("<KeyRelease>", self.check_inputs)

        # Start Button (standardmäßig deaktiviert)
        self.start_button = ctk.CTkButton(
            self,
            text="Daten abrufen",
            command=self.run_process,
            state="disabled",
            fg_color="#1f538d"
        )
        self.start_button.pack(pady=30)

        # Status Nachricht (Erfolg/Fehler Text unter dem Button)
        self.status_label = ctk.CTkLabel(self, text="", font=("Arial", 12))
        self.status_label.pack(pady=10, padx=20)

    def load_teams(self):
        """Liest die Teams aus der teams.txt ein."""
        teams = {}
        try:
            with open("teams.txt", encoding="utf-8") as file:
                for line in file:
                    name = line.strip().upper()
                    if name:
                        teams[name] = name
            return teams
        except Exception as e:
            messagebox.showerror("Fehler", f"teams.txt konnte nicht geladen werden: {e}")
            return {"FEHLER": "Keine Teams gefunden"}

    def check_inputs(self, event=None):
        """Prüft, ob die Game ID gültig ist und aktiviert/deaktiviert den Button."""
        val = self.game_id_entry.get().strip()
        # Button nur aktiv, wenn die ID nur aus Zahlen besteht und eine sinnvolle Länge hat
        if val.isdigit() and 8 <= len(val) <= 15:
            self.start_button.configure(state="normal")
        else:
            self.start_button.configure(state="disabled")

    def run_process(self):
        """Bereitet den Start des Scraping-Prozesses vor."""
        team_name = self.team_dropdown.get()
        game_id = self.game_id_entry.get().strip()

        # UI in den "Lade-Zustand" versetzen
        self.start_button.configure(state="disabled", text="Verarbeite...")
        self.status_label.configure(text="Rufe Daten ab, bitte warten...", text_color="gray")

        # Thread starten, damit die UI nicht einfriert
        thread = threading.Thread(target=self.worker, args=(team_name, game_id), daemon=True)
        thread.start()

    def worker(self, team_name, game_id):
        try:
            parse_game(team_name, game_id)
            self.after(0, lambda: self.show_success(game_id))
        except Exception as e:
            error_text = str(e) if str(e) else f"Unbekannter Fehler ({type(e).__name__})"
            self.after(0, lambda: self.show_error(error_text))

    def show_success(self, game_id):
        """Zeigt die Erfolgsmeldung an und setzt das Feld zurück."""
        self.status_label.configure(
            text=f"Erfolg: Game {game_id} wurde verarbeitet!",
            text_color="#44ff44"  # Hellgrün
        )
        messagebox.showinfo("Abgeschlossen", f"Daten für Game {game_id} wurden erfolgreich eingetragen.")

        # Feld leeren und Button zurücksetzen
        self.game_id_entry.delete(0, 'end')
        self.start_button.configure(text="Daten abrufen")
        self.check_inputs()  # Button wieder deaktivieren

    def show_error(self, error_msg):
        """Zeigt eine Fehlermeldung in Rot an."""
        self.status_label.configure(
            text=f"Fehler: {error_msg}",
            text_color="#ff4444"  # Hellrot
        )
        messagebox.showerror("Fehler beim Abruf", error_msg)
        self.start_button.configure(state="normal", text="Daten abrufen")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = App()
    app.mainloop()