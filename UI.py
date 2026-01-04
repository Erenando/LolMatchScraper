import customtkinter as ctk
from tkinter import messagebox
import threading
import multiprocessing
from PIL import Image, ImageTk

from CustomGameJSONParser import process_game
from GoogleAPIConnector import upload_to_sheets

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("LoL Match Scraper")
        self.geometry("600x650")

        self.teams = self.load_teams()

        # --- HEADER ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(pady=(20, 10))

        ctk.CTkLabel(self.header_frame, text="MATCH SCRAPER", font=("Impact", 28), text_color="#eeeeee").pack()
        ctk.CTkLabel(self.header_frame, text="DATA UPLOADER TOOL", font=("Arial", 10), text_color="gray").pack()

        # --- SECTION 1: SETTINGS ---
        self.settings_frame = ctk.CTkFrame(self, fg_color=("#2b2b2b", "#2b2b2b"), corner_radius=10)
        self.settings_frame.pack(pady=10, padx=20, fill="x")

        # Title for Section
        ctk.CTkLabel(self.settings_frame, text="CONFIGURATION", font=("Arial", 11, "bold"), text_color="gray").pack(
            pady=(10, 5), padx=15, anchor="w")

        # Row 1: Team Sheet Selection
        self.team_dropdown = ctk.CTkComboBox(self.settings_frame, values=list(self.teams.values()), width=400,
                                             height=35, font=("Arial", 14))
        self.team_dropdown.pack(pady=(0, 15), padx=20, fill="x")
        if list(self.teams.values()):
            self.team_dropdown.set(list(self.teams.values())[0])


        # --- SECTION 2: MATCHUP ---
        self.matchup_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.matchup_frame.pack(pady=10, padx=20, fill="x")

        # Blue Side
        self.blue_container = ctk.CTkFrame(self.matchup_frame, fg_color="transparent")
        self.blue_container.pack(side="left", expand=True, fill="x")
        ctk.CTkLabel(self.blue_container, text="TEAM BLUE", text_color="#3b82f6", font=("Arial", 12, "bold")).pack(
            anchor="w")

        self.blue_entry = ctk.CTkEntry(self.blue_container, placeholder_text="Name Blue", height=40,
                                       border_color="#3b82f6", border_width=2)
        self.blue_entry.pack(fill="x", pady=5)

        # --- CENTER: VS & SWAP BUTTON ---
        self.vs_frame = ctk.CTkFrame(self.matchup_frame, fg_color="transparent")
        self.vs_frame.pack(side="left", padx=10)

        # Kleines Label "VS"
        ctk.CTkLabel(self.vs_frame, text="VS", font=("Arial Black", 10), text_color="gray").pack(pady=(0, 2))

        # Swap Button
        self.swap_btn = ctk.CTkButton(
            self.vs_frame,
            text="↔",
            width=40,
            height=30,
            font=("Arial", 18),
            fg_color="#333333",
            hover_color="#444444",
            command=self.swap_teams
        )
        self.swap_btn.pack()

        # Red Side
        self.red_container = ctk.CTkFrame(self.matchup_frame, fg_color="transparent")
        self.red_container.pack(side="left", expand=True, fill="x")
        ctk.CTkLabel(self.red_container, text="TEAM RED", text_color="#ef4444", font=("Arial", 12, "bold")).pack(
            anchor="e")

        self.red_entry = ctk.CTkEntry(self.red_container, placeholder_text="Name Red", height=40,
                                      border_color="#ef4444", border_width=2,
                                      justify="right")
        self.red_entry.pack(fill="x", pady=5)

        # --- SECTION 3: GAME ID & ACTION ---
        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.pack(pady=20, padx=20, fill="x")

        ctk.CTkLabel(self.action_frame, text="GAME ID", font=("Arial", 12, "bold")).pack(anchor="w")
        self.game_id_entry = ctk.CTkEntry(self.action_frame, placeholder_text="e.g. 7557023906", height=45,
                                          font=("Arial", 16))
        self.game_id_entry.pack(fill="x", pady=(5, 20))
        self.game_id_entry.bind("<KeyRelease>", self.check_inputs)

        self.start_button = ctk.CTkButton(
            self.action_frame,
            text="FETCH & UPLOAD DATA",
            font=("Arial", 14, "bold"),
            height=50,
            corner_radius=8,
            fg_color="#10b981",
            hover_color="#059669",
            command=self.run_process,
            state="disabled"
        )
        self.start_button.pack(fill="x")

        self.status_label = ctk.CTkLabel(self, text="", font=("Arial", 12), wraplength=400)
        self.status_label.pack(pady=5)

        # --- FOOTER ---
        self.footer_frame = ctk.CTkFrame(self, fg_color="transparent", height=60)
        self.footer_frame.pack(side="bottom", fill="x", padx=15, pady=15)

        # Copyright
        self.copyright_label = ctk.CTkLabel(
            self.footer_frame,
            text="© by Eren | Discord: Erenando",
            font=("Arial", 15),
            text_color="gray"
        )
        self.copyright_label.place(relx=1.0, rely=0.5, anchor="e")

        # Logo Logic
        image_path = "img/NEKO_LOGO.png"
        try:
            img_open = Image.open(image_path)
            # Icon App
            icon_photo = ImageTk.PhotoImage(img_open)
            self.wm_iconphoto(True, icon_photo)

            # Logo Footer
            my_logo = ctk.CTkImage(light_image=img_open, dark_image=img_open, size=(50, 50))
            self.logo_label_corner = ctk.CTkLabel(self.footer_frame, image=my_logo, text="")
            self.logo_label_corner.place(relx=0.0, rely=0.5, anchor="w")

        except Exception:
            self.logo_label_corner = ctk.CTkLabel(self.footer_frame, text="ACE", font=("Impact", 20))
            self.logo_label_corner.place(relx=0.0, rely=0.5, anchor="w")

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

    def swap_teams(self):
        blue_val = self.blue_entry.get()
        red_val = self.red_entry.get()

        self.blue_entry.delete(0, "end")
        self.red_entry.delete(0, "end")

        self.blue_entry.insert(0, red_val)
        self.red_entry.insert(0, blue_val)

    def check_inputs(self, event=None):
        val = self.game_id_entry.get().strip()
        if val.isdigit() and 5 <= len(val) <= 13:
            self.start_button.configure(state="normal", fg_color="#10b981")
        else:
            self.start_button.configure(state="disabled", fg_color="#333333")

    def run_process(self):
        worksheet_team = self.team_dropdown.get()
        blue_name = self.blue_entry.get().strip()
        red_name = self.red_entry.get().strip()
        game_id = self.game_id_entry.get().strip()

        if not blue_name or not red_name:
            messagebox.showwarning("Missing Input", "Please enter name for both teams!")
            return

        # UI Update
        self.start_button.configure(state="disabled", text="PROCESSING...", fg_color="#eab308")
        self.status_label.configure(text="Fetching Data...", text_color="white")

        thread = threading.Thread(
            target=self.worker,
            args=(worksheet_team, blue_name, red_name, game_id),
            daemon=True
        )
        thread.start()

    def worker(self, worksheet_team, blue_name, red_name, game_id):
        try:
            # 1. fetch data
            parsed_data, raw_data, source = process_game(game_id, blue_name, red_name)

            # 2. Google Sheets Upload
            self.status_label.configure(text="Uploading to Google Sheets...", text_color="#60a5fa")
            upload_to_sheets(parsed_data, worksheet_team)

            self.after(0, lambda: self.show_success(game_id))

        except Exception as e:
            error_text = str(e) if str(e) else f"Error ({type(e).__name__})"
            print(f"WORKER ERROR: {error_text}")
            self.after(0, lambda: self.show_error(error_text))

    def show_success(self, game_id):
        self.status_label.configure(text=f"Success: Game {game_id} done!", text_color="#4ade80")
        messagebox.showinfo("Success", f"Data for Game {game_id} successfully processed!")

        self.game_id_entry.delete(0, 'end')

        self.start_button.configure(text="FETCH & UPLOAD DATA")
        self.check_inputs()

    def show_error(self, error_msg):
        self.status_label.configure(text=f"Error: {error_msg}", text_color="#f87171")
        messagebox.showerror("Error", f"Process interrupted:\n{error_msg}")
        self.start_button.configure(state="normal", text="FETCH & UPLOAD DATA", fg_color="#10b981")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = App()
    app.mainloop()