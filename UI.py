import customtkinter as ctk
from tkinter import messagebox
import threading
import multiprocessing
import re
import json
import os
import webbrowser
from PIL import Image, ImageTk
from CustomGameJSONParser import process_game
from GoogleAPIConnector import upload_to_sheets

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("LoL Match Scraper")
        self.geometry("680x860")

        self.teams = self.load_teams()
        self.own_team_name = self.teams[0] if self.teams else "OWN_TEAM_NOT_FOUND"
        self.target_sheet_link = self.load_target_sheet_link()

        self.gametype_vars = ["Scrim", "Official", "Tournament"]

        # --- HEADER ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(pady=(20, 10))
        ctk.CTkLabel(self.header_frame, text="MATCH SCRAPER", font=("Impact", 28), text_color="#eeeeee").pack()
        ctk.CTkLabel(
            self.header_frame,
            text="Insert LoL MatchData in Google Sheets",
            font=("Arial", 11),
            text_color="gray",
        ).pack()

        # --- SECTION 1: CONFIGURATION ---
        self.settings_frame = ctk.CTkFrame(self, fg_color=("#2b2b2b", "#2b2b2b"), corner_radius=10)
        self.settings_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(self.settings_frame, text="CONFIGURATION", font=("Arial", 11, "bold"), text_color="gray").pack(
            pady=(10, 6), padx=15, anchor="w"
        )

        self.config_row = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.config_row.pack(pady=(0, 12), padx=20, fill="x")

        self.config_game_type = ctk.CTkFrame(self.config_row, fg_color="transparent")
        self.config_game_type.pack(side="left", fill="x", padx=(0, 10))
        ctk.CTkLabel(self.config_game_type, text="Game Type", font=("Arial", 11, "bold"), text_color="gray", anchor="w").pack(
            fill="x", pady=(0, 2)
        )
        self.gametype_dropdown = ctk.CTkComboBox(
            self.config_game_type, values=self.gametype_vars, height=35, width=170, state="readonly", command=self.check_inputs
        )
        self.gametype_dropdown.set("Scrim")
        self.gametype_dropdown.pack(fill="x")

        self.config_own_team = ctk.CTkFrame(self.config_row, fg_color="transparent")
        self.config_own_team.pack(side="left", fill="x", padx=(0, 10))
        ctk.CTkLabel(self.config_own_team, text="Own Team", font=("Arial", 11, "bold"), text_color="gray", anchor="w").pack(
            fill="x", pady=(0, 2)
        )
        self.own_team_label = ctk.CTkLabel(
            self.config_own_team,
            text=self.own_team_name,
            font=("Arial", 13, "bold"),
            text_color="#e5e7eb",
            fg_color="#1f2937",
            corner_radius=8,
            height=35,
            width=170,
            anchor="w"
        )
        self.own_team_label.pack(fill="x")

        self.config_enemy_team = ctk.CTkFrame(self.config_row, fg_color="transparent")
        self.config_enemy_team.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(self.config_enemy_team, text="Enemy Team", font=("Arial", 11, "bold"), text_color="gray", anchor="w").pack(
            fill="x", pady=(0, 2)
        )
        self.enemy_team_entry = ctk.CTkEntry(
            self.config_enemy_team,
            placeholder_text="Enemy Team Name",
            height=38,
            font=("Arial", 14)
        )
        self.enemy_team_entry.pack(fill="x")
        self.enemy_team_entry.bind("<KeyRelease>", self.check_inputs)

        # --- SECTION 2: MATCH LINES ---
        self.matches_frame = ctk.CTkFrame(self, fg_color=("#2b2b2b", "#2b2b2b"), corner_radius=10)
        self.matches_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(self.matches_frame, text="MATCH INPUT", font=("Arial", 11, "bold"), text_color="gray").pack(
            pady=(10, 6), padx=15, anchor="w"
        )
        header_frame = ctk.CTkFrame(self.matches_frame, fg_color="#1f2937", corner_radius=6)
        header_frame.pack(fill="x", padx=20, pady=(0, 10))
        ctk.CTkLabel(header_frame, text="Match Nr.", width=70, anchor="w", font=("Arial", 11, "bold")).pack(side="left", padx=(10, 0), pady=6)
        ctk.CTkLabel(header_frame, text="Match ID", anchor="w", font=("Arial", 11, "bold")).pack(side="left", fill="x", expand=True, padx=(12, 0), pady=6)
        ctk.CTkLabel(header_frame, text="Own Team Side", width=140, anchor="w", font=("Arial", 11, "bold")).pack(side="left", padx=(12, 8), pady=6)

        self.match_rows_container = ctk.CTkScrollableFrame(
            self.matches_frame,
            fg_color="transparent",
            height=150
        )
        self.match_rows_container.pack(fill="x", padx=20, pady=(0, 8))

        self.match_rows = []
        self.add_match_btn = ctk.CTkButton(
            self.matches_frame,
            text="+ ADD MATCH ROW",
            height=32,
            font=("Arial", 11, "bold"),
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            command=self.add_match_row
        )
        self.add_match_btn.pack(fill="x", padx=20, pady=(0, 8))

        for _ in range(3):
            self.add_match_row()

        self.match_feedback = ctk.CTkLabel(
            self.matches_frame,
            text="No match IDs entered yet.",
            font=("Arial", 11),
            text_color="gray",
            anchor="w"
        )
        self.match_feedback.pack(fill="x", padx=20, pady=(0, 10))

        # --- SECTION 3: ACTION ---
        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.pack(pady=8, padx=20, fill="x")

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

        self.open_sheet_button = ctk.CTkButton(
            self.action_frame,
            text="OPEN GOOGLE SHEET",
            font=("Arial", 12, "bold"),
            height=38,
            fg_color="#1f2937",
            hover_color="#374151",
            command=self.open_target_sheet,
            state="normal" if self.target_sheet_link else "disabled"
        )
        self.open_sheet_button.pack(fill="x", pady=(8, 0))

        self.progress_bar = ctk.CTkProgressBar(self, mode="indeterminate")
        self.progress_bar.pack(padx=20, pady=(8, 2), fill="x")
        self.progress_bar.stop()
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(self, text="Fill in all fields and start the process.", font=("Arial", 12), wraplength=560)
        self.status_label.pack(pady=5)

        self.watermark_label = ctk.CTkLabel(
            self,
            text="@by Eren | Discord: Erenando",
            font=("Arial", 14),
            text_color="gray"
        )
        self.watermark_label.place(relx=1.0, rely=1.0, anchor="se", x=-14, y=-10)
        self.watermark_label.lift()

        image_path = "img/icon.png"
        try:
            img_open = Image.open(image_path)
            icon_photo = ImageTk.PhotoImage(img_open)
            self.wm_iconphoto(True, icon_photo)
        except Exception:
            pass

        self.check_inputs()

    def load_teams(self):
        teams = []
        try:
            with open("teams.txt", encoding="utf-8") as file:
                for line in file:
                    name = line.strip().upper()
                    if name:
                        teams.append(name)
            return teams
        except OSError:
            return []

    def load_target_sheet_link(self):
        try:
            with open("config.json", encoding="utf-8") as config_file:
                config = json.load(config_file)
            return str(config.get("google_sheets_link", "")).strip()
        except OSError:
            return ""
        except json.JSONDecodeError:
            return ""

    def _normalize_game_id(self, value: str) -> str:
        raw = value.strip()
        if raw.isdigit() and 5 <= len(raw) <= 13:
            return raw

        match = re.search(r"(?:[A-Z0-9]+_)?(\d{5,13})", raw, re.IGNORECASE)
        if match:
            return match.group(1)
        return ""

    def _set_controls_enabled(self, enabled: bool) -> None:
        entry_state = "normal" if enabled else "disabled"
        combo_state = "readonly" if enabled else "disabled"
        self.gametype_dropdown.configure(state=combo_state)
        self.enemy_team_entry.configure(state=entry_state)
        self.add_match_btn.configure(state=entry_state)
        for row in self.match_rows:
            row["id_entry"].configure(state=entry_state)
            row["side_dropdown"].configure(state=combo_state)
            row["remove_btn"].configure(state=entry_state)

    def _reindex_match_rows(self) -> None:
        for index, row in enumerate(self.match_rows, start=1):
            row["row_index"] = index
            row["match_label"].configure(text=str(index))

    def add_match_row(self):
        row_frame = ctk.CTkFrame(self.match_rows_container, fg_color="transparent")
        row_frame.pack(fill="x", pady=(0, 8))

        match_label = ctk.CTkLabel(row_frame, text=str(len(self.match_rows) + 1), width=70, anchor="w")
        match_label.pack(side="left", padx=(10, 0))

        id_entry = ctk.CTkEntry(
            row_frame,
            placeholder_text="7557023906 or EUW1_7557023906",
            height=34,
            font=("Arial", 13)
        )
        id_entry.pack(side="left", fill="x", expand=True, padx=(8, 10))
        id_entry.bind("<KeyRelease>", self.check_inputs)

        side_dropdown = ctk.CTkComboBox(
            row_frame,
            values=["Blue", "Red"],
            width=130,
            height=34,
            state="readonly",
            fg_color="#1f2937",
            button_color="#2563eb",
            button_hover_color="#1d4ed8"
        )
        side_dropdown.set("Blue")
        side_dropdown.configure(command=self.check_inputs)
        side_dropdown.pack(side="left", padx=(2, 0))

        remove_btn = ctk.CTkButton(
            row_frame,
            text="✕",
            width=34,
            height=34,
            fg_color="#7f1d1d",
            hover_color="#991b1b",
            command=lambda rf=row_frame: self.remove_match_row(rf)
        )
        remove_btn.pack(side="left", padx=(8, 0))

        self.match_rows.append(
            {
                "row_index": len(self.match_rows) + 1,
                "frame": row_frame,
                "match_label": match_label,
                "id_entry": id_entry,
                "side_dropdown": side_dropdown,
                "remove_btn": remove_btn,
            }
        )
        self._reindex_match_rows()
        if hasattr(self, "match_feedback"):
            self.check_inputs()

    def remove_match_row(self, row_frame):
        if len(self.match_rows) == 1:
            self.match_rows[0]["id_entry"].delete(0, "end")
            self.match_rows[0]["side_dropdown"].set("Blue")
            self.check_inputs()
            return

        for index, row in enumerate(self.match_rows):
            if row["frame"] == row_frame:
                row["frame"].destroy()
                self.match_rows.pop(index)
                break

        self._reindex_match_rows()
        self.check_inputs()

    def _collect_match_jobs(self):
        enemy_team = self.enemy_team_entry.get().strip()
        jobs = []
        invalid_rows = []

        for row in self.match_rows:
            row_index = row["row_index"]
            raw_game_id = row["id_entry"].get().strip()
            if not raw_game_id:
                continue

            normalized_game_id = self._normalize_game_id(raw_game_id)
            if not normalized_game_id:
                invalid_rows.append(row_index)
                continue

            side = row["side_dropdown"].get()
            if side not in ("Blue", "Red"):
                invalid_rows.append(row_index)
                continue

            if side == "Blue":
                blue_name = self.own_team_name
                red_name = enemy_team
            else:
                blue_name = enemy_team
                red_name = self.own_team_name

            jobs.append(
                {
                    "row_index": row_index,
                    "game_id": normalized_game_id,
                    "match_number": str(row_index),
                    "blue_name": blue_name,
                    "red_name": red_name,
                    "line_text": f"Match {row_index}: {normalized_game_id} ({side})"
                }
            )

        return jobs, invalid_rows

    def check_inputs(self, event=None):
        enemy_team = self.enemy_team_entry.get().strip()
        jobs, invalid_rows = self._collect_match_jobs()
        has_game_type = self.gametype_dropdown.get() in self.gametype_vars
        has_enemy = bool(enemy_team)
        has_valid_jobs = bool(jobs) and not bool(invalid_rows)
        own_team_ok = self.own_team_name != "OWN_TEAM_NOT_FOUND"

        if not own_team_ok:
            self.match_feedback.configure(text="teams.txt is empty or missing.", text_color="#f87171")
        elif invalid_rows:
            rows_text = ", ".join([str(i) for i in invalid_rows])
            self.match_feedback.configure(text=f"Invalid Match ID in row(s): {rows_text}", text_color="#f87171")
        elif jobs:
            self.match_feedback.configure(text=f"{len(jobs)} valid match line(s) ready.", text_color="#4ade80")
        else:
            self.match_feedback.configure(text="No match IDs entered yet.", text_color="gray")

        if has_game_type and has_enemy and has_valid_jobs and own_team_ok:
            self.start_button.configure(state="normal", fg_color="#10b981")
        else:
            self.start_button.configure(state="disabled", fg_color="#333333")

    def run_process(self):
        worksheet_team = self.own_team_name
        enemy_team = self.enemy_team_entry.get().strip()
        game_type = self.gametype_dropdown.get()
        jobs, invalid_rows = self._collect_match_jobs()

        if self.own_team_name == "OWN_TEAM_NOT_FOUND":
            messagebox.showwarning("Missing input", "Please add your own team as the first line in teams.txt.")
            return

        if not enemy_team:
            messagebox.showwarning("Missing input", "Please enter the enemy team name.")
            return

        if game_type not in self.gametype_vars:
            messagebox.showwarning("Missing input", "Please select a game type.")
            return

        if invalid_rows:
            rows_text = ", ".join([str(i) for i in invalid_rows])
            messagebox.showwarning("Invalid input", f"Invalid Match ID in row(s): {rows_text}")
            return

        if not jobs:
            messagebox.showwarning("Missing input", "Please enter at least one valid Match ID.")
            return

        self._set_controls_enabled(False)
        self.start_button.configure(state="disabled", text="PROCESSING...", fg_color="#eab308")
        self.status_label.configure(text=f"Batch mode active: processing {len(jobs)} match(es)...", text_color="white")
        self.progress_bar.start()

        thread = threading.Thread(
            target=self.worker,
            args=(worksheet_team, jobs, game_type),
            daemon=True
        )
        thread.start()

    def worker(self, worksheet_team, jobs, game_type):
        try:
            total = len(jobs)
            successful_jobs = []
            failed_jobs = []

            for index, job in enumerate(jobs, start=1):
                game_id = job["game_id"]
                self.after(
                    0,
                    lambda i=index, t=total, g=game_id: self.status_label.configure(
                        text=f"Fetching match {i}/{t}: {g}",
                        text_color="white"
                    )
                )

                try:
                    parsed_data, _, _ = process_game(
                        game_id,
                        job["blue_name"],
                        job["red_name"],
                        game_type,
                        job["match_number"],
                    )
                    self.after(
                        0,
                        lambda i=index, t=total: self.status_label.configure(
                            text=f"Uploading match {i}/{t} to Google Sheets...",
                            text_color="#60a5fa"
                        )
                    )
                    upload_to_sheets(parsed_data, worksheet_team)
                    successful_jobs.append(job)
                except Exception as per_game_error:
                    failed_jobs.append((job, str(per_game_error) if str(per_game_error) else type(per_game_error).__name__))

            self.after(0, lambda: self.show_batch_result(successful_jobs, failed_jobs))

        except Exception as e:
            error_text = str(e) if str(e) else f"Error ({type(e).__name__})"
            print(f"WORKER ERROR: {error_text}")
            self.after(0, lambda: self.show_error(error_text))

    def show_batch_result(self, successful_jobs, failed_jobs):
        self.progress_bar.stop()
        self.progress_bar.set(1 if successful_jobs else 0)

        success_count = len(successful_jobs)
        failed_count = len(failed_jobs)
        total_count = success_count + failed_count

        if failed_count == 0:
            self.status_label.configure(
                text=f"Success: {success_count}/{total_count} matches uploaded.",
                text_color="#4ade80"
            )
            messagebox.showinfo("Success", f"Uploaded {success_count} match(es) successfully.")
            for row in self.match_rows:
                row["id_entry"].delete(0, "end")
            if self.target_sheet_link:
                self.open_sheet_button.configure(state="normal")
        elif success_count == 0:
            self.status_label.configure(
                text=f"Error: 0/{total_count} matches uploaded.",
                text_color="#f87171"
            )
            failed_details = "\n".join([f"{job['line_text']}: {error}" for job, error in failed_jobs])
            messagebox.showerror("Batch failed", f"No matches were uploaded.\n\n{failed_details}")
        else:
            self.status_label.configure(
                text=f"Partial success: {success_count}/{total_count} matches uploaded.",
                text_color="#fbbf24"
            )
            failed_details = "\n".join([f"{job['line_text']}: {error}" for job, error in failed_jobs])
            messagebox.showwarning(
                "Batch partially completed",
                f"Uploaded {success_count} of {total_count} matches.\n\nFailed:\n{failed_details}"
            )
            if self.target_sheet_link:
                self.open_sheet_button.configure(state="normal")

        if failed_jobs:
            failed_rows = {job["row_index"] for job, _ in failed_jobs}
            for row in self.match_rows:
                if row["row_index"] not in failed_rows:
                    row["id_entry"].delete(0, "end")

        self._set_controls_enabled(True)
        self.start_button.configure(text="FETCH & UPLOAD DATA", fg_color="#10b981")
        self.check_inputs()

    def show_error(self, error_msg):
        self.progress_bar.stop()
        self.progress_bar.set(0)
        self.status_label.configure(text=f"Error: {error_msg}", text_color="#f87171")
        messagebox.showerror("Error", f"Process failed:\n{error_msg}")
        self._set_controls_enabled(True)
        self.start_button.configure(text="FETCH & UPLOAD DATA", fg_color="#10b981")
        self.check_inputs()

    def open_target_sheet(self):
        self.target_sheet_link = self.load_target_sheet_link()
        if not self.target_sheet_link:
            messagebox.showwarning("Missing link", "No Google Sheets link found in config.json.")
            return

        link = self.target_sheet_link.strip()
        if not re.match(r"^https?://", link, re.IGNORECASE):
            link = f"https://{link}"

        try:
            opened = webbrowser.open_new_tab(link)
            if not opened:
                os.startfile(link)
        except Exception as exc:
            messagebox.showerror("Open failed", f"Could not open Google Sheet:\n{exc}")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = App()
    app.mainloop()
