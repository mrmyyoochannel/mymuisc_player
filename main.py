import customtkinter as ctk
from ui.main_window import ModernMusicPlayer

def main() -> None:
    # ตั้งค่า ธีมหลักของแอป
    ctk.set_appearance_mode("Dark")  
    ctk.set_default_color_theme("blue")  
    
    # รันหน้าต่างหลัก
    app = ModernMusicPlayer()
    
    # ถ้า AudioPlayer เกิด Error ตอน init (เช่น ไม่มี VLC) app จะถูก destroy ทันที
    # เราจึงต้องเช็คก่อนสั่ง mainloop เพื่อไม่ให้เกิด Error ซ้อน
    if app.winfo_exists():
        app.mainloop()

if __name__ == "__main__":
    main()