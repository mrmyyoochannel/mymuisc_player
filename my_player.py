import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
import pygame
import os

# ตั้งค่าธีม (System, Dark, Light)
ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("blue")  

class ModernMusicPlayer(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ตั้งค่าหน้าต่างหลัก
        self.title("Modern Music Player")
        self.geometry("600x550") # เพิ่มความสูงนิดหน่อยเผื่อชื่อเพลงยาว 2 บรรทัด
        
        # เริ่มต้น Pygame Mixer
        pygame.mixer.init()
        
        # ตัวแปรเก็บ Playlist และสถานะ
        self.playlist = []
        self.current_song = ""
        self.paused = False
        
        # --- ส่วนของ GUI (จัด Layout ใหม่ ไม่ให้ทับกัน) ---
        
        # 1. Header Frame (แถบด้านบนสุด เก็บปุ่ม Open Folder)
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=(20, 10), padx=20, fill="x")
        
        # ปุ่มเลือกโฟลเดอร์ (ชิดซ้าย)
        folder_btn = ctk.CTkButton(header_frame, text="📂 Open Folder", command=self.load_folder, 
                                 fg_color="gray", hover_color="#4a4a4a", width=120)
        folder_btn.pack(side="left")

        # 2. ชื่อเพลง (อยู่บรรทัดถัดมา)
        # wraplength=550 คือถ้าชื่อยาวเกิน 550px ให้ปัดลงบรรทัดใหม่
        self.track_label = ctk.CTkLabel(self, text="Select Folder to Start", 
                                      font=("Roboto", 18, "bold"),
                                      text_color="#1f6aa5",
                                      wraplength=550) 
        self.track_label.pack(pady=10)
        
        # 3. กล่องรายการเพลง (Listbox)
        # ใช้ Frame หุ้ม Listbox อีกทีเพื่อให้จัดระยะสวย
        listbox_frame = ctk.CTkFrame(self, fg_color="transparent")
        listbox_frame.pack(pady=5, padx=20, fill="both", expand=True)

        self.playlist_box = tk.Listbox(listbox_frame, 
                                       bg="#2b2b2b",       
                                       fg="white",         
                                       selectbackground="#1f6aa5", 
                                       selectforeground="white",
                                       font=("Arial", 12),
                                       borderwidth=0,      
                                       highlightthickness=0)
        self.playlist_box.pack(fill="both", expand=True)
        
        # 4. ส่วนควบคุม (Buttons)
        control_frame = ctk.CTkFrame(self, fg_color="transparent") 
        control_frame.pack(pady=20)
        
        self.play_btn = ctk.CTkButton(control_frame, text="▶ Play", command=self.play_music, width=100, corner_radius=20)
        self.pause_btn = ctk.CTkButton(control_frame, text="⏸ Pause", command=self.pause_music, width=100, corner_radius=20, fg_color="#d68f00", hover_color="#b57900")
        self.stop_btn = ctk.CTkButton(control_frame, text="⏹ Stop", command=self.stop_music, width=100, corner_radius=20, fg_color="#c42b1c", hover_color="#9e2316")
        
        self.play_btn.grid(row=0, column=0, padx=10)
        self.pause_btn.grid(row=0, column=1, padx=10)
        self.stop_btn.grid(row=0, column=2, padx=10)
        
        # 5. Volume Slider
        volume_frame = ctk.CTkFrame(self, fg_color="transparent")
        volume_frame.pack(pady=(0, 20), fill="x", padx=50) # เว้นระยะล่าง 20
        
        vol_label = ctk.CTkLabel(volume_frame, text="Volume 🔊", font=("Arial", 12))
        vol_label.pack(side="left", padx=10)
        
        self.volume_slider = ctk.CTkSlider(volume_frame, from_=0, to=100, command=self.set_volume, width=200)
        self.volume_slider.set(50) 
        pygame.mixer.music.set_volume(0.5)
        self.volume_slider.pack(side="left", fill="x", expand=True)

    # --- ฟังก์ชันการทำงาน ---
    def load_folder(self):
        path = filedialog.askdirectory()
        if path:
            os.chdir(path)
            songs = os.listdir(path)
            self.playlist_box.delete(0, tk.END)
            self.playlist = []
            for song in songs:
                if song.endswith(".mp3"):
                    self.playlist.append(song)
                    self.playlist_box.insert(tk.END, song)

    def play_music(self):
        try:
            if self.paused:
                pygame.mixer.music.unpause()
                self.paused = False
                self.track_label.configure(text=f"Playing: {self.current_song}")
                return

            selected_song_index = self.playlist_box.curselection()
            selected_song = self.playlist_box.get(selected_song_index)
            self.current_song = selected_song
            
            pygame.mixer.music.load(selected_song)
            pygame.mixer.music.play(loops=0)
            
            self.track_label.configure(text=f"Playing: {selected_song}")
            self.paused = False
        except Exception:
            pass 

    def pause_music(self):
        pygame.mixer.music.pause()
        self.paused = True
        self.track_label.configure(text=f"Paused")

    def stop_music(self):
        pygame.mixer.music.stop()
        self.playlist_box.selection_clear(0, tk.END)
        self.track_label.configure(text="Music Stopped")
        self.paused = False

    def set_volume(self, val):
        volume = int(val) / 100 
        pygame.mixer.music.set_volume(volume)

if __name__ == "__main__":
    app = ModernMusicPlayer()
    app.mainloop()