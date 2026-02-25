import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import os
from player.player import AudioPlayer

class ModernMusicPlayer(ctk.CTk):
    """หน้าต่างหลักของโปรแกรมเล่นเพลง"""
    
    def __init__(self) -> None:
        super().__init__()
        
        self.title("Modern Music Player")
        self.geometry("600x550")
        
        # 1. ลองสร้าง AudioPlayer (นี่คือส่วน Error Handling สำคัญ)
        try:
            self.audio_player = AudioPlayer()
        except RuntimeError as e:
            # ถ้าเกิด Error (เช่น ไม่มี VLC) ให้เด้งเตือนแล้วปิดโปรแกรม
            messagebox.showerror("Critical Error", str(e))
            self.destroy()
            return # หยุดการทำงานทันที

        # ตัวแปรสถานะ
        self.current_folder: str = ""
        self.current_song: str = ""
        self.playlist: list[str] = []
        
        self._setup_ui()

    def _setup_ui(self) -> None:
        """แยกส่วนการสร้าง UI ออกมาเพื่อให้โค้ดอ่านง่าย"""
        # Header Frame
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=(20, 10), padx=20, fill="x")
        
        ctk.CTkButton(header_frame, text="📂 Open Folder", command=self.load_folder, 
                      fg_color="gray", hover_color="#4a4a4a", width=120).pack(side="left")

        self.track_label = ctk.CTkLabel(self, text="Select Folder to Start", 
                                        font=("Roboto", 18, "bold"), text_color="#1f6aa5") 
        self.track_label.pack(pady=10)
        
        # Playlist Box
        listbox_frame = ctk.CTkFrame(self, fg_color="transparent")
        listbox_frame.pack(pady=5, padx=20, fill="both", expand=True)

        self.playlist_box = tk.Listbox(listbox_frame, bg="#2b2b2b", fg="white", 
                                       selectbackground="#1f6aa5", font=("Arial", 12), borderwidth=0)
        self.playlist_box.pack(fill="both", expand=True)
        
        # Controls
        control_frame = ctk.CTkFrame(self, fg_color="transparent") 
        control_frame.pack(pady=20)
        
        ctk.CTkButton(control_frame, text="▶ Play", command=self.play_music, width=100).grid(row=0, column=0, padx=10)
        ctk.CTkButton(control_frame, text="⏸ Pause", command=self.pause_music, width=100, fg_color="#d68f00").grid(row=0, column=1, padx=10)
        ctk.CTkButton(control_frame, text="⏹ Stop", command=self.stop_music, width=100, fg_color="#c42b1c").grid(row=0, column=2, padx=10)
        
        # Volume
        volume_frame = ctk.CTkFrame(self, fg_color="transparent")
        volume_frame.pack(pady=(0, 20), fill="x", padx=50)
        ctk.CTkLabel(volume_frame, text="Volume 🔊").pack(side="left", padx=10)
        
        self.volume_slider = ctk.CTkSlider(volume_frame, from_=0, to=100, command=self.set_volume)
        self.volume_slider.set(50) 
        self.audio_player.set_volume(50)
        self.volume_slider.pack(side="left", fill="x", expand=True)

    def load_folder(self) -> None:
        """เลือกโฟลเดอร์และโหลดไฟล์เพลงลง Playlist"""
        path: str = filedialog.askdirectory()
        if not path:
            return
            
        self.current_folder = path
        self.playlist_box.delete(0, tk.END)
        self.playlist.clear()
        
        try:
            for song in os.listdir(path):
                if song.lower().endswith((".mp3", ".wav", ".flac", ".ogg")):
                    self.playlist.append(song)
                    self.playlist_box.insert(tk.END, song)
        except PermissionError:
            messagebox.showerror("Error", "ไม่มีสิทธิ์เข้าถึงโฟลเดอร์นี้ครับ")

    def play_music(self) -> None:
        """เล่นเพลงที่เลือก พร้อมดักจับ Error หากไฟล์เสีย"""
        selected_index = self.playlist_box.curselection()
        if not selected_index:
            return
            
        selected_song = self.playlist_box.get(selected_index)
        full_path = os.path.join(self.current_folder, selected_song)
        
        try:
            self.audio_player.load_and_play(full_path)
            self.current_song = selected_song
            self.track_label.configure(text=f"Playing: {selected_song}")
        except FileNotFoundError as e:
            messagebox.showerror("File Error", str(e))
        except Exception as e:
            messagebox.showerror("Playback Error", f"ไม่สามารถเล่นเพลงนี้ได้:\n{e}")

    def pause_music(self) -> None:
        self.audio_player.pause()
        self.track_label.configure(text="Paused")

    def stop_music(self) -> None:
        self.audio_player.stop()
        self.track_label.configure(text="Music Stopped")

    def set_volume(self, val: float) -> None:
        self.audio_player.set_volume(int(val))