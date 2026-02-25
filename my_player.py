import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
import vlc  # เปลี่ยนมาใช้ vlc
import os

ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("blue")  

# ---------------------------------------------------------
# คลาสสำหรับหน้าต่าง Equalizer
# ---------------------------------------------------------
class EqualizerWindow(ctk.CTkToplevel):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master # อ้างอิงถึงหน้าต่างหลักเพื่อส่งค่าเสียง
        
        self.title("ตัวปรับแต่งเสียง (Equalizer)")
        self.geometry("600x450")
        self.resizable(False, False)
        self.configure(fg_color="#242424")

        # 1. Header 
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(20, 10))
        
        ctk.CTkLabel(header_frame, text="ตัวปรับแต่งเสียง", font=("Roboto", 20, "bold")).pack(side="left")
        
        self.eq_switch = ctk.CTkSwitch(header_frame, text="เปิด", progress_color="#f97316", 
                                       button_color="#ffffff", font=("Roboto", 14),
                                       command=self.master.toggle_eq) # ผูกฟังก์ชันเปิด/ปิด
        self.eq_switch.pack(side="right")
        
        # ตั้งค่าสวิตช์ตามสถานะปัจจุบัน
        if self.master.eq_enabled:
            self.eq_switch.select()
        else:
            self.eq_switch.deselect()

        # 2. Dropdown Presets
        preset_frame = ctk.CTkFrame(self, fg_color="transparent")
        preset_frame.pack(fill="x", padx=30, pady=(0, 20))
        
        ctk.CTkLabel(preset_frame, text="ค่าที่ตั้งไว้", font=("Roboto", 14)).pack(side="left", padx=(0, 10))
        self.preset_combo = ctk.CTkComboBox(preset_frame, values=["กำหนดเอง", "Pop", "Rock", "Bass Boost"], 
                                            width=120, fg_color="#333333", border_color="#333333",
                                            command=self.master.apply_preset)
        self.preset_combo.pack(side="left")

        # 3. Main EQ Sliders Area
        sliders_frame = ctk.CTkFrame(self, fg_color="transparent")
        sliders_frame.pack(fill="both", expand=True, padx=20)

        y_labels_frame = ctk.CTkFrame(sliders_frame, fg_color="transparent")
        y_labels_frame.pack(side="left", fill="y", pady=(10, 30))
        
        ctk.CTkLabel(y_labels_frame, text="+12 dB", font=("Roboto", 12)).pack(side="top")
        ctk.CTkLabel(y_labels_frame, text="+6 dB", font=("Roboto", 12)).pack(side="top", expand=True)
        ctk.CTkLabel(y_labels_frame, text="0 dB", font=("Roboto", 12)).pack(side="top", expand=True)
        ctk.CTkLabel(y_labels_frame, text="-6 dB", font=("Roboto", 12)).pack(side="top", expand=True)
        ctk.CTkLabel(y_labels_frame, text="-12 dB", font=("Roboto", 12)).pack(side="bottom")

        self.sliders = []
        frequencies = ["62 Hz", "125 Hz", "250 Hz", "500 Hz", "1 kHz", "2 kHz", "4 kHz", "8 kHz", "16 kHz"]
        
        eq_band_frame = ctk.CTkFrame(sliders_frame, fg_color="transparent")
        eq_band_frame.pack(side="left", fill="both", expand=True, padx=(10, 0))

        for i, freq in enumerate(frequencies):
            band_frame = ctk.CTkFrame(eq_band_frame, fg_color="transparent")
            band_frame.pack(side="left", fill="y", expand=True)
            
            # ส่งค่า Index (i) ไปพร้อมกับค่าความดังเสียง
            slider = ctk.CTkSlider(band_frame, from_=-12, to=12, orientation="vertical",
                                   progress_color="#555555", button_color="#f97316", 
                                   button_hover_color="#ea580c",
                                   command=lambda val, idx=i: self.master.change_eq_band(idx, val))
            
            # ดึงค่าเดิมของ EQ มาแสดงให้ตรงกันเมื่อเปิดหน้าต่างขึ้นมาใหม่
            vlc_band_index = i + 1 
            current_amp = self.master.equalizer.get_amp_at_index(vlc_band_index)
            slider.set(current_amp)
            
            slider.pack(pady=(15, 10), expand=True, fill="y")
            self.sliders.append(slider)
            
            ctk.CTkLabel(band_frame, text=freq, font=("Roboto", 12)).pack(side="bottom")

        # 4. Checkbox
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(fill="x", padx=30, pady=(10, 20))
        
        self.link_check = ctk.CTkCheckBox(bottom_frame, text="ย้ายแถบเลื่อนที่อยู่ใกล้เคียงไปด้วยกัน", 
                                          fg_color="#f97316", hover_color="#ea580c")
        self.link_check.pack(side="left")

        # 5. ปุ่ม ปิด (Close)
        close_btn = ctk.CTkButton(self, text="ปิด", command=self.destroy, fg_color="#333333", hover_color="#444444")
        close_btn.pack(side="bottom", pady=(0, 20))

    # ฟังก์ชันสำหรับอัปเดตหน้าตา Slider เมื่อเลือก Preset
    def update_sliders_from_preset(self):
        for i, slider in enumerate(self.sliders):
            vlc_band_index = i + 1
            current_amp = self.master.equalizer.get_amp_at_index(vlc_band_index)
            slider.set(current_amp)


# ---------------------------------------------------------
# คลาสเครื่องเล่นเพลงหลัก
# ---------------------------------------------------------
class ModernMusicPlayer(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Modern Music Player")
        self.geometry("600x550") 
        
        # --- เริ่มต้น VLC ---
        self.vlc_instance = vlc.Instance()
        self.player = self.vlc_instance.media_player_new()
        
        # --- เริ่มต้นระบบ Equalizer ---
        self.equalizer = vlc.AudioEqualizer()
        self.eq_enabled = True
        self.player.set_equalizer(self.equalizer) # นำ EQ ใส่ใน Player
        
        self.current_folder = ""
        self.playlist = []
        self.current_song = ""
        self.eq_window = None 
        
        # --- ส่วนของ GUI ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=(20, 10), padx=20, fill="x")
        
        folder_btn = ctk.CTkButton(header_frame, text="📂 Open Folder", command=self.load_folder, 
                                   fg_color="gray", hover_color="#4a4a4a", width=120)
        folder_btn.pack(side="left")

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
        self.player.audio_set_volume(50) # เซ็ตวอลลุ่มเริ่มต้น VLC เป็น 50
        self.volume_slider.pack(side="left", fill="x", expand=True)

    # --- ฟังก์ชันควบคุม EQ ---
    def open_equalizer(self):
        if self.eq_window is None or not self.eq_window.winfo_exists():
            self.eq_window = EqualizerWindow(self) 
            self.eq_window.focus()
        else:
            self.eq_window.focus()

    def change_eq_band(self, ui_index, value):
        # VLC มี 10 bands (เริ่มที่ 31.25Hz) แต่ UI ของเรามี 9 bands (เริ่มที่ 62Hz)
        # ดังนั้นต้องบวก 1 เพื่อให้ตรงย่านความถี่กัน
        vlc_band_index = ui_index + 1
        amp = float(value) 
        self.equalizer.set_amp_at_index(amp, vlc_band_index)
        
        # อัปเดตไปยัง player ถ้าระบบ EQ เปิดอยู่
        if self.eq_enabled:
            self.player.set_equalizer(self.equalizer)

    def toggle_eq(self):
        if self.eq_window and self.eq_window.winfo_exists():
            self.eq_enabled = self.eq_window.eq_switch.get() == 1
            if self.eq_enabled:
                self.player.set_equalizer(self.equalizer) # เปิด
            else:
                self.player.set_equalizer(None) # ปิด

    def apply_preset(self, choice):
        # สร้าง Preset จำลอง
        presets = {
            "กำหนดเอง": [0, 0, 0, 0, 0, 0, 0, 0, 0],
            "Pop": [-1.5, 3.0, 4.5, 4.5, 2.0, -1.5, -2.0, -2.0, -1.5],
            "Rock": [5.0, 4.0, 3.0, 1.5, -1.0, -1.5, 0.5, 2.5, 4.0],
            "Bass Boost": [8.0, 6.0, 4.0, 0, 0, 0, 0, 0, 0]
        }
        
        if choice in presets:
            values = presets[choice]
            for i, val in enumerate(values):
                self.change_eq_band(i, val)
                
            # อัปเดตหน้าตา Slider ถ้ายกหน้าต่างอยู่
            if self.eq_window and self.eq_window.winfo_exists():
                self.eq_window.update_sliders_from_preset()

    # --- ฟังก์ชันการทำงานของเครื่องเล่น (ปรับเปลี่ยนเป็น VLC) ---
    def load_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.current_folder = path
            songs = os.listdir(path)
            self.playlist_box.delete(0, tk.END)
            self.playlist = []
            for song in songs:
                if song.endswith((".mp3", ".wav", ".flac", ".ogg")): # VLC รองรับหลายไฟล์
                    self.playlist.append(song)
                    self.playlist_box.insert(tk.END, song)

    def play_music(self):
        try:
            # ตรวจสอบว่ามีเพลงกำลัง Pause อยู่หรือไม่
            if self.player.get_state() == vlc.State.Paused:
                self.player.play()
                self.track_label.configure(text=f"Playing: {self.current_song}")
                return

            selected_song_index = self.playlist_box.curselection()
            if not selected_song_index: # ถ้าไม่ได้เลือกเพลง ให้ไม่เกิดอะไรขึ้น
                return
                
            selected_song = self.playlist_box.get(selected_song_index)
            self.current_song = selected_song
            
            # โหลดไฟล์เพลง (ต้องใช้ Path เต็ม)
            full_path = os.path.join(self.current_folder, selected_song)
            media = self.vlc_instance.media_new(full_path)
            self.player.set_media(media)
            self.player.play()
            
            self.track_label.configure(text=f"Playing: {selected_song}")
        except Exception as e:
            print(f"Error: {e}")

    def pause_music(self):
        self.player.pause()
        self.track_label.configure(text=f"Paused")

    def stop_music(self):
        self.player.stop()
        self.playlist_box.selection_clear(0, tk.END)
        self.track_label.configure(text="Music Stopped")

    def set_volume(self, val):
        volume = int(val) # VLC ใช้ระดับเสียง 0-100 พอดี
        self.player.audio_set_volume(volume)

if __name__ == "__main__":
    app = ModernMusicPlayer()
    app.mainloop()
