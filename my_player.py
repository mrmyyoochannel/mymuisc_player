import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
import pygame
import os

# ตั้งค่าธีม
ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("blue")  

# ---------------------------------------------------------
# คลาสสำหรับหน้าต่าง Equalizer
# ---------------------------------------------------------
class EqualizerWindow(ctk.CTkToplevel):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.title("ตัวปรับแต่งเสียง (Equalizer)")
        self.geometry("600x450")
        self.resizable(False, False)
        # ปรับสีพื้นหลังให้เป็นสีเทาเข้มแบบในรูป
        self.configure(fg_color="#242424")

        # 1. Header (ชื่อและสวิตช์เปิด/ปิด)
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(20, 10))
        
        ctk.CTkLabel(header_frame, text="ตัวปรับแต่งเสียง", font=("Roboto", 20, "bold")).pack(side="left")
        
        self.eq_switch = ctk.CTkSwitch(header_frame, text="เปิด", progress_color="#f97316", button_color="#ffffff", font=("Roboto", 14))
        self.eq_switch.pack(side="right")
        self.eq_switch.select() # เปิดไว้เป็นค่าเริ่มต้น

        # 2. Dropdown (ค่าที่ตั้งไว้ / Presets)
        preset_frame = ctk.CTkFrame(self, fg_color="transparent")
        preset_frame.pack(fill="x", padx=30, pady=(0, 20))
        
        ctk.CTkLabel(preset_frame, text="ค่าที่ตั้งไว้", font=("Roboto", 14)).pack(side="left", padx=(0, 10))
        self.preset_combo = ctk.CTkComboBox(preset_frame, values=["กำหนดเอง", "Pop", "Rock", "Jazz", "Classical"], 
                                            width=120, fg_color="#333333", border_color="#333333")
        self.preset_combo.pack(side="left")

        # 3. Main EQ Sliders Area
        sliders_frame = ctk.CTkFrame(self, fg_color="transparent")
        sliders_frame.pack(fill="both", expand=True, padx=20)

        # แถบ dB ซ้ายมือ (Y-Axis Labels)
        y_labels_frame = ctk.CTkFrame(sliders_frame, fg_color="transparent")
        y_labels_frame.pack(side="left", fill="y", pady=(10, 30))
        
        ctk.CTkLabel(y_labels_frame, text="+12 dB", font=("Roboto", 12)).pack(side="top")
        ctk.CTkLabel(y_labels_frame, text="+6 dB", font=("Roboto", 12)).pack(side="top", expand=True)
        ctk.CTkLabel(y_labels_frame, text="0 dB", font=("Roboto", 12)).pack(side="top", expand=True)
        ctk.CTkLabel(y_labels_frame, text="-6 dB", font=("Roboto", 12)).pack(side="top", expand=True)
        ctk.CTkLabel(y_labels_frame, text="-12 dB", font=("Roboto", 12)).pack(side="bottom")

        # สร้าง Slider ตามย่านความถี่ (X-Axis)
        self.sliders = []
        frequencies = ["62 Hz", "125 Hz", "250 Hz", "500 Hz", "1 kHz", "2 kHz", "4 kHz", "8 kHz", "16 kHz"]
        
        eq_band_frame = ctk.CTkFrame(sliders_frame, fg_color="transparent")
        eq_band_frame.pack(side="left", fill="both", expand=True, padx=(10, 0))

        for freq in frequencies:
            band_frame = ctk.CTkFrame(eq_band_frame, fg_color="transparent")
            band_frame.pack(side="left", fill="y", expand=True)
            
            # Slider แนวตั้ง (ตั้งค่าสีส้มแบบในรูป)
            slider = ctk.CTkSlider(band_frame, from_=-12, to=12, orientation="vertical",
                                   progress_color="#555555", button_color="#f97316", 
                                   button_hover_color="#ea580c")
            slider.set(0) # ตั้งค่าเริ่มต้นที่ 0 dB
            slider.pack(pady=(15, 10), expand=True, fill="y")
            self.sliders.append(slider)
            
            # ป้ายความถี่ด้านล่าง
            ctk.CTkLabel(band_frame, text=freq, font=("Roboto", 12)).pack(side="bottom")

        # 4. Checkbox เชื่อมแถบใกล้เคียง
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(fill="x", padx=30, pady=(10, 20))
        
        self.link_check = ctk.CTkCheckBox(bottom_frame, text="ย้ายแถบเลื่อนที่อยู่ใกล้เคียงไปด้วยกัน", 
                                          fg_color="#f97316", hover_color="#ea580c")
        self.link_check.pack(side="left")

        # 5. ปุ่ม ปิด (Close)
        close_btn = ctk.CTkButton(self, text="ปิด", command=self.destroy, fg_color="#333333", hover_color="#444444")
        close_btn.pack(side="bottom", pady=(0, 20))


# ---------------------------------------------------------
# คลาสเครื่องเล่นเพลงหลัก (เพิ่มปุ่มเปิด EQ)
# ---------------------------------------------------------
class ModernMusicPlayer(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Modern Music Player")
        self.geometry("600x550") 
        
        pygame.mixer.init()
        self.playlist = []
        self.current_song = ""
        self.paused = False
        self.eq_window = None # ตัวแปรเก็บสถานะหน้าต่าง EQ
        
        # --- GUI แบบเดิมของคุณ ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=(20, 10), padx=20, fill="x")
        
        folder_btn = ctk.CTkButton(header_frame, text="📂 Open Folder", command=self.load_folder, 
                                   fg_color="gray", hover_color="#4a4a4a", width=120)
        folder_btn.pack(side="left")

        # เพิ่มปุ่มสำหรับเปิดหน้าต่าง Equalizer
        eq_btn = ctk.CTkButton(header_frame, text="🎛️ Equalizer", command=self.open_equalizer, 
                               fg_color="#f97316", hover_color="#ea580c", width=100)
        eq_btn.pack(side="right")

        self.track_label = ctk.CTkLabel(self, text="Select Folder to Start", 
                                        font=("Roboto", 18, "bold"), text_color="#1f6aa5", wraplength=550) 
        self.track_label.pack(pady=10)
        
        listbox_frame = ctk.CTkFrame(self, fg_color="transparent")
        listbox_frame.pack(pady=5, padx=20, fill="both", expand=True)

        self.playlist_box = tk.Listbox(listbox_frame, bg="#2b2b2b", fg="white", 
                                       selectbackground="#1f6aa5", selectforeground="white",
                                       font=("Arial", 12), borderwidth=0, highlightthickness=0)
        self.playlist_box.pack(fill="both", expand=True)
        
        control_frame = ctk.CTkFrame(self, fg_color="transparent") 
        control_frame.pack(pady=20)
        
        self.play_btn = ctk.CTkButton(control_frame, text="▶ Play", command=self.play_music, width=100, corner_radius=20)
        self.pause_btn = ctk.CTkButton(control_frame, text="⏸ Pause", command=self.pause_music, width=100, corner_radius=20, fg_color="#d68f00", hover_color="#b57900")
        self.stop_btn = ctk.CTkButton(control_frame, text="⏹ Stop", command=self.stop_music, width=100, corner_radius=20, fg_color="#c42b1c", hover_color="#9e2316")
        
        self.play_btn.grid(row=0, column=0, padx=10)
        self.pause_btn.grid(row=0, column=1, padx=10)
        self.stop_btn.grid(row=0, column=2, padx=10)
        
        volume_frame = ctk.CTkFrame(self, fg_color="transparent")
        volume_frame.pack(pady=(0, 20), fill="x", padx=50)
        
        vol_label = ctk.CTkLabel(volume_frame, text="Volume 🔊", font=("Arial", 12))
        vol_label.pack(side="left", padx=10)
        
        self.volume_slider = ctk.CTkSlider(volume_frame, from_=0, to=100, command=self.set_volume, width=200)
        self.volume_slider.set(50) 
        pygame.mixer.music.set_volume(0.5)
        self.volume_slider.pack(side="left", fill="x", expand=True)

    # --- ฟังก์ชันใหม่: เปิดหน้าต่าง EQ ---
    def open_equalizer(self):
        if self.eq_window is None or not self.eq_window.winfo_exists():
            self.eq_window = EqualizerWindow(self)  # สร้างหน้าต่างใหม่
            self.eq_window.focus()
        else:
            self.eq_window.focus()  # ถ้ามีอยู่แล้วให้ดึงขึ้นมาด้านหน้า

    # --- ฟังก์ชันการทำงานเดิม ---
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
