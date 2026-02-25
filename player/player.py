import os
import logging
from typing import Optional

# ตั้งค่า Logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# --- ดักจับ Error ตั้งแต่ตอน Import Module ---
VLC_AVAILABLE = False
try:
    import vlc
    VLC_AVAILABLE = True
except (ImportError, FileNotFoundError, OSError) as e:
    logging.error(f"Cannot load VLC Engine: {e}")

class AudioPlayer:
    """Class สำหรับจัดการระบบเสียงด้วย VLC Engine"""
    
    def __init__(self) -> None:
        # เช็คสถานะตั้งแต่เริ่มสร้างคลาส
        if not VLC_AVAILABLE:
            raise RuntimeError(
                "ไม่พบเอนจินระบบเสียง (libvlc.dll) ในเครื่อง!\n\n"
                "แอปพลิเคชันนี้จำเป็นต้องใช้ VLC Media Player ในการทำงาน\n"
                "กรุณาดาวน์โหลดและติดตั้ง VLC (64-bit) จาก www.videolan.org"
            )

        self.vlc_instance: Optional['vlc.Instance'] = None
        self.player: Optional['vlc.MediaPlayer'] = None
        self.equalizer: Optional['vlc.AudioEqualizer'] = None
        
        self._initialize_vlc()

    def _initialize_vlc(self) -> None:
        try:
            self.vlc_instance = vlc.Instance()
            self.player = self.vlc_instance.media_player_new()
            self.equalizer = vlc.AudioEqualizer()
            self.player.set_equalizer(self.equalizer)
            logging.info("VLC Player initialized successfully.")
        except Exception as e:
            raise RuntimeError(f"เกิดข้อผิดพลาดในการรันระบบเสียง: {e}")

    def load_and_play(self, file_path: str) -> None:
        """โหลดไฟล์เพลงและเล่นทันที"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"ไม่พบไฟล์เพลง: {file_path}")
            
        try:
            media = self.vlc_instance.media_new(file_path)
            self.player.set_media(media)
            self.player.play()
            logging.info(f"Playing: {file_path}")
        except Exception as e:
            raise Exception(f"ไม่สามารถเล่นไฟล์นี้ได้: {e}")

    def pause(self) -> None:
        if self.player:
            self.player.pause()

    def stop(self) -> None:
        if self.player:
            self.player.stop()

    def set_volume(self, volume: int) -> None:
        if self.player:
            vol = max(0, min(100, volume))
            self.player.audio_set_volume(vol)