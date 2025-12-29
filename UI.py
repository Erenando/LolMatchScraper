import customtkinter as ctk
from tkinter import messagebox
from GoogleAPIConnector import parse_game
import threading
import multiprocessing  # Notwendig für den .exe Export

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("LoL Match Scraper")
        self.geometry("500x550")

        self.teams = self.load_teams()

        self.label_team = ctk.CTkLabel(self, text="Select Team for Stats Sheet:", font=("Arial", 14, "bold"))
        self.label_team.pack(pady=(30, 5))

        self.team_dropdown = ctk.CTkComboBox(self, values=list(self.teams.values()), width=300)
        self.team_dropdown.pack(pady=10)
        if list(self.teams.values()):
            self.team_dropdown.set(list(self.teams.values())[0])

        self.team_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.team_frame.pack(pady=10)

        self.blue_frame = ctk.CTkFrame(self.team_frame, fg_color="transparent")
        self.blue_frame.pack(side="left", padx=10)
        ctk.CTkLabel(self.blue_frame, text="Team Blue:", font=("Arial", 12, "bold")).pack()
        self.blue_entry = ctk.CTkEntry(self.blue_frame, placeholder_text="Name Blue", width=140)
        self.blue_entry.pack()

        self.red_frame = ctk.CTkFrame(self.team_frame, fg_color="transparent")
        self.red_frame.pack(side="left", padx=10)
        ctk.CTkLabel(self.red_frame, text="Team Red:", font=("Arial", 12, "bold")).pack()
        self.red_entry = ctk.CTkEntry(self.red_frame, placeholder_text="Name Red", width=140)
        self.red_entry.pack()

        self.label_game = ctk.CTkLabel(self, text="Enter Game ID:", font=("Arial", 14, "bold"))
        self.label_game.pack(pady=(20, 5))

        self.game_id_entry = ctk.CTkEntry(self, placeholder_text="e.g. 7557023906", width=300)
        self.game_id_entry.pack(pady=10)
        self.game_id_entry.bind("<KeyRelease>", self.check_inputs)

        self.start_button = ctk.CTkButton(
            self,
            text="Fetch Data",
            command=self.run_process,
            state="disabled"
        )
        self.start_button.pack(pady=30)

        self.status_label = ctk.CTkLabel(self, text="", font=("Arial", 12), wraplength=400)
        self.status_label.pack(pady=10, padx=20)

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
            return {"ERROR": "Teams not found"}

    def check_inputs(self, event=None):
        val = self.game_id_entry.get().strip()
        if val.isdigit() and 5 <= len(val) <= 13:
            self.start_button.configure(state="normal")
        else:
            self.start_button.configure(state="disabled")

    def run_process(self):
        worksheet_team = self.team_dropdown.get()
        blue_name = self.blue_entry.get().strip()
        red_name = self.red_entry.get().strip()
        game_id = self.game_id_entry.get().strip()

        if not blue_name or not red_name:
            messagebox.showwarning("Missing Input", "Please enter name for both teams!")
            return

        self.start_button.configure(state="disabled", text="Processing...")
        # Wir übergeben nun alle 4 Parameter an den Worker
        thread = threading.Thread(target=self.worker, args=(worksheet_team, blue_name, red_name, game_id), daemon=True)
        thread.start()

    def worker(self, worksheet_team, blue_name, red_name, game_id):
        try:
            parse_game(worksheet_team, blue_name, red_name, game_id)
            self.after(0, lambda: self.show_success(game_id))
        except Exception as e:
            error_text = str(e) if str(e) else f"Error ({type(e).__name__})"
            self.after(0, lambda: self.show_error(error_text))

    def show_success(self, game_id):
        self.status_label.configure(text=f"Success: Game {game_id} processed!", text_color="#44ff44")
        messagebox.showinfo("Erfolg", f"Data for Game {game_id} successfully inserted!.")
        self.game_id_entry.delete(0, 'end')
        self.start_button.configure(text="Fetch Data")
        self.check_inputs()

    def show_error(self, error_msg):
        self.status_label.configure(text=f"Error: {error_msg}", text_color="#ff4444")
        messagebox.showerror("Error", f"Process interrupted:\n{error_msg}")
        self.start_button.configure(state="normal", text="Fetch Data")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = App()
    app.mainloop()