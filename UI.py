import customtkinter as ctk
from tkinter import messagebox
from GoogleAPIConnector import parse_game
import threading
import multiprocessing  # Notwendig für den .exe Export

# Design-Einstellungen
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Fenster-Konfiguration
        self.title("LoL Match Scraper")
        self.geometry("500x550")

        # Teams laden
        self.teams = self.load_teams()

        # --- UI Komponenten ---
        self.label_team = ctk.CTkLabel(self, text="Team auswählen:", font=("Arial", 14, "bold"))
        self.label_team.pack(pady=(30, 5))

        self.team_dropdown = ctk.CTkComboBox(self, values=list(self.teams.values()), width=300)
        self.team_dropdown.pack(pady=10)
        if list(self.teams.values()):
            self.team_dropdown.set(list(self.teams.values())[0])

        self.label_game = ctk.CTkLabel(self, text="Game ID eingeben:", font=("Arial", 14, "bold"))
        self.label_game.pack(pady=(20, 5))

        self.game_id_entry = ctk.CTkEntry(self, placeholder_text="z.B. 7557023906", width=300)
        self.game_id_entry.pack(pady=10)
        self.game_id_entry.bind("<KeyRelease>", self.check_inputs)

        self.start_button = ctk.CTkButton(
            self,
            text="Daten abrufen",
            command=self.run_process,
            state="disabled"
        )
        self.start_button.pack(pady=30)

        # Status Label für Text-Feedback
        self.status_label = ctk.CTkLabel(self, text="", font=("Arial", 12), wraplength=400)
        self.status_label.pack(pady=10, padx=20)

        # --- Copyright Sektion ---
        # Ein Frame, um den Text unten rechts zu platzieren
        self.footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.footer_frame.pack(side="bottom", fill="x", padx=10, pady=10)

        self.copyright_label = ctk.CTkLabel(
            self.footer_frame,
            text="© by Eren | Discord: Erenando",
            font=("Arial", 10),
            text_color="gray"
        )
        self.copyright_label.pack(side="right")

    def load_teams(self):
        teams = {}
        try:
            with open("teams.txt", encoding="utf-8") as file:
                for line in file:
                    name = line.strip().upper()
                    if name: teams[name] = name
            return teams
        except:
            return {"ERROR": "Teams nicht gefunden"}

    def check_inputs(self, event=None):
        val = self.game_id_entry.get().strip()
        if val.isdigit() and 8 <= len(val) <= 13:
            self.start_button.configure(state="normal")
        else:
            self.start_button.configure(state="disabled")

    def run_process(self):
        team_name = self.team_dropdown.get()
        game_id = self.game_id_entry.get().strip()

        self.start_button.configure(state="disabled", text="Verarbeite...")
        self.status_label.configure(text=f"Suche Game {game_id}...", text_color="gray")

        thread = threading.Thread(target=self.worker, args=(team_name, game_id), daemon=True)
        thread.start()

    def worker(self, team_name, game_id):
        try:
            parse_game(team_name, game_id)
            self.after(0, lambda: self.show_success(game_id))
        except Exception as e:
            error_text = str(e) if str(e) else f"Fehler ({type(e).__name__})"
            self.after(0, lambda: self.show_error(error_text))

    def show_success(self, game_id):
        self.status_label.configure(text=f"Erfolg: Game {game_id} verarbeitet!", text_color="#44ff44")
        messagebox.showinfo("Erfolg", f"Daten für Game {game_id} erfolgreich eingefügt.")
        self.game_id_entry.delete(0, 'end')
        self.start_button.configure(text="Daten abrufen")
        self.check_inputs()

    def show_error(self, error_msg):
        self.status_label.configure(text=f"Fehler: {error_msg}", text_color="#ff4444")
        messagebox.showerror("Fehler", f"Verarbeitung abgebrochen:\n{error_msg}")
        self.start_button.configure(state="normal", text="Daten abrufen")


if __name__ == "__main__":
    # WICHTIG für .exe Export mit Multiprocessing
    multiprocessing.freeze_support()
    app = App()
    app.mainloop()