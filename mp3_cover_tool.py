  #!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
import os
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error
from PIL import Image, ImageTk, ImageFilter, ImageEnhance
import io
import threading
import time

class RetroMP3CoverTool:
    def __init__(self, root):
        self.root = root
        self.root.title("🎵 MP3 COVER TOOL 🎵")
        self.root.geometry("800x700")
        self.root.configure(bg='#0a0a0a')
        self.root.resizable(True, True)
        
        # Değişkenler
        self.mp3_file = None
        self.image_file = None
        self.preview_image = None
        self.animation_running = False
        
        # Renkler (Cyberpunk/Retro palette)
        self.colors = {
            'bg': '#0a0a0a',
            'panel': '#1a1a2e',
            'accent': '#16213e',
            'neon_pink': '#ff006e',
            'neon_blue': '#00f5ff',
            'neon_green': '#39ff14',
            'neon_purple': '#8b00ff',
            'text': '#ffffff',
            'text_dim': '#a0a0a0',
            'success': '#00ff41',
            'warning': '#ffaa00',
            'error': '#ff0040'
        }
        
        self.setup_fonts()
        self.setup_ui()
        self.setup_drag_drop()
        self.start_background_animation()
        
    def setup_fonts(self):
        """Custom font ayarları"""
        self.fonts = {
            'title': ('Courier New', 20, 'bold'),
            'subtitle': ('Courier New', 14, 'bold'),
            'body': ('Courier New', 11),
            'small': ('Courier New', 9),
            'button': ('Courier New', 12, 'bold')
        }
        
    def setup_ui(self):
        """Modern retro arayüz oluştur"""
        # Ana container
        self.main_container = tk.Frame(self.root, bg=self.colors['bg'])
        self.main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Başlık bölümü
        self.create_header()
        
        # İçerik bölümü
        self.create_content()
        
        # Alt durum bölümü
        self.create_status_bar()
        
    def create_header(self):
        """Başlık bölümü"""
        header_frame = tk.Frame(self.main_container, bg=self.colors['bg'], height=100)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # Ana başlık
        title_label = tk.Label(header_frame, 
                              text="🎵 RETRO MP3 COVER TOOL 🎵",
                              font=self.fonts['title'],
                              fg=self.colors['neon_pink'],
                              bg=self.colors['bg'])
        title_label.pack(pady=(20, 5))
        
        # Alt başlık
        subtitle_label = tk.Label(header_frame, 
                                 text=">>> INJECT COVER ART INTO YOUR TRACKS <<<",
                                 font=self.fonts['small'],
                                 fg=self.colors['neon_blue'],
                                 bg=self.colors['bg'])
        subtitle_label.pack()
        
        # Animasyonlu separator
        self.separator_frame = tk.Frame(header_frame, bg=self.colors['neon_green'], height=2)
        self.separator_frame.pack(fill='x', pady=(10, 0))
        
    def create_content(self):
        """Ana içerik bölümü"""
        content_frame = tk.Frame(self.main_container, bg=self.colors['bg'])
        content_frame.pack(fill='both', expand=True)
        
        # Sol ve sağ panel
        left_panel = self.create_left_panel(content_frame)
        right_panel = self.create_right_panel(content_frame)
        
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        right_panel.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
    def create_left_panel(self, parent):
        """Sol panel - dosya seçimi"""
        panel = tk.Frame(parent, bg=self.colors['panel'], relief='raised', bd=2)
        
        # MP3 seçimi
        mp3_section = self.create_mp3_section(panel)
        mp3_section.pack(fill='x', padx=20, pady=(20, 10))
        
        # Resim seçimi
        image_section = self.create_image_section(panel)
        image_section.pack(fill='x', padx=20, pady=(10, 20))
        
        # İşlem butonu
        self.create_process_button(panel)
        
        return panel
        
    def create_right_panel(self, parent):
        """Sağ panel - önizleme"""
        panel = tk.Frame(parent, bg=self.colors['panel'], relief='raised', bd=2)
        
        # Önizleme başlığı
        preview_title = tk.Label(panel, 
                                text="[ PREVIEW ]",
                                font=self.fonts['subtitle'],
                                fg=self.colors['neon_purple'],
                                bg=self.colors['panel'])
        preview_title.pack(pady=(20, 10))
        
        # Önizleme alanı
        self.preview_container = tk.Frame(panel, bg=self.colors['accent'], 
                                         relief='sunken', bd=3)
        self.preview_container.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        self.preview_label = tk.Label(self.preview_container, 
                                     text="NO IMAGE SELECTED\n\n> Select an image to see preview <",
                                     font=self.fonts['body'],
                                     fg=self.colors['text_dim'],
                                     bg=self.colors['accent'],
                                     justify='center')
        self.preview_label.pack(expand=True)
        
        return panel
        
    def create_mp3_section(self, parent):
        """MP3 dosya seçimi bölümü"""
        section = tk.Frame(parent, bg=self.colors['panel'])
        
        # Başlık
        title = tk.Label(section, 
                        text="[ 01 ] SELECT MP3 FILE",
                        font=self.fonts['subtitle'],
                        fg=self.colors['neon_blue'],
                        bg=self.colors['panel'])
        title.pack(anchor='w', pady=(0, 10))
        
        # Drag & Drop alanı
        self.mp3_drop_area = tk.Frame(section, bg=self.colors['accent'], 
                                     relief='groove', bd=3, height=80)
        self.mp3_drop_area.pack(fill='x', pady=(0, 10))
        self.mp3_drop_area.pack_propagate(False)
        
        self.mp3_drop_label = tk.Label(self.mp3_drop_area, 
                                      text="DRAG & DROP MP3 FILE HERE\n>>> OR CLICK BUTTON BELOW <<<",
                                      font=self.fonts['body'],
                                      fg=self.colors['text_dim'],
                                      bg=self.colors['accent'],
                                      justify='center')
        self.mp3_drop_label.pack(expand=True)
        
        # Seçilen dosya bilgisi
        self.mp3_info_label = tk.Label(section, 
                                      text="STATUS: NO FILE SELECTED",
                                      font=self.fonts['small'],
                                      fg=self.colors['text_dim'],
                                      bg=self.colors['panel'])
        self.mp3_info_label.pack(anchor='w', pady=(0, 10))
        
        # Seçim butonu
        self.mp3_button = tk.Button(section, 
                                   text="[ SELECT MP3 ]",
                                   font=self.fonts['button'],
                                   fg=self.colors['bg'],
                                   bg=self.colors['neon_blue'],
                                   relief='raised',
                                   bd=2,
                                   command=self.select_mp3,
                                   cursor='hand2')
        self.mp3_button.pack(anchor='w')
        
        return section
        
    def create_image_section(self, parent):
        """Resim seçimi bölümü"""
        section = tk.Frame(parent, bg=self.colors['panel'])
        
        # Başlık
        title = tk.Label(section, 
                        text="[ 02 ] SELECT COVER IMAGE",
                        font=self.fonts['subtitle'],
                        fg=self.colors['neon_green'],
                        bg=self.colors['panel'])
        title.pack(anchor='w', pady=(0, 10))
        
        # Drag & Drop alanı
        self.image_drop_area = tk.Frame(section, bg=self.colors['accent'], 
                                       relief='groove', bd=3, height=80)
        self.image_drop_area.pack(fill='x', pady=(0, 10))
        self.image_drop_area.pack_propagate(False)
        
        self.image_drop_label = tk.Label(self.image_drop_area, 
                                        text="DRAG & DROP IMAGE FILE HERE\n>>> JPG, PNG, GIF, BMP <<<",
                                        font=self.fonts['body'],
                                        fg=self.colors['text_dim'],
                                        bg=self.colors['accent'],
                                        justify='center')
        self.image_drop_label.pack(expand=True)
        
        # Seçilen dosya bilgisi
        self.image_info_label = tk.Label(section, 
                                        text="STATUS: NO IMAGE SELECTED",
                                        font=self.fonts['small'],
                                        fg=self.colors['text_dim'],
                                        bg=self.colors['panel'])
        self.image_info_label.pack(anchor='w', pady=(0, 10))
        
        # Seçim butonu
        self.image_button = tk.Button(section, 
                                     text="[ SELECT IMAGE ]",
                                     font=self.fonts['button'],
                                     fg=self.colors['bg'],
                                     bg=self.colors['neon_green'],
                                     relief='raised',
                                     bd=2,
                                     command=self.select_image,
                                     cursor='hand2')
        self.image_button.pack(anchor='w')
        
        return section
        
    def create_process_button(self, parent):
        """İşlem butonu"""
        button_frame = tk.Frame(parent, bg=self.colors['panel'])
        button_frame.pack(fill='x', padx=20, pady=(20, 30))
        
        self.process_button = tk.Button(button_frame, 
                                       text=">>> INJECT COVER ART <<<",
                                       font=('Courier New', 14, 'bold'),
                                       fg=self.colors['bg'],
                                       bg=self.colors['neon_pink'],
                                       relief='raised',
                                       bd=3,
                                       height=2,
                                       command=self.add_cover_art,
                                       cursor='hand2',
                                       state='disabled')
        self.process_button.pack(fill='x')
        
    def create_status_bar(self):
        """Alt durum çubuğu"""
        status_frame = tk.Frame(self.main_container, bg=self.colors['accent'], 
                               relief='sunken', bd=2, height=40)
        status_frame.pack(fill='x', pady=(20, 0))
        status_frame.pack_propagate(False)
        
        self.status_var = tk.StringVar()
        self.status_var.set("SYSTEM READY >>> WAITING FOR INPUT")
        
        self.status_label = tk.Label(status_frame, 
                                    textvariable=self.status_var,
                                    font=self.fonts['small'],
                                    fg=self.colors['neon_green'],
                                    bg=self.colors['accent'])
        self.status_label.pack(pady=10)
        
    def setup_drag_drop(self):
        """Drag & drop ayarları"""
        # MP3 drag & drop
        self.mp3_drop_area.drop_target_register(DND_FILES)
        self.mp3_drop_area.dnd_bind('<<Drop>>', self.on_mp3_drop)
        self.mp3_drop_area.dnd_bind('<<DragEnter>>', self.on_mp3_drag_enter)
        self.mp3_drop_area.dnd_bind('<<DragLeave>>', self.on_mp3_drag_leave)
        
        # Image drag & drop
        self.image_drop_area.drop_target_register(DND_FILES)
        self.image_drop_area.dnd_bind('<<Drop>>', self.on_image_drop)
        self.image_drop_area.dnd_bind('<<DragEnter>>', self.on_image_drag_enter)
        self.image_drop_area.dnd_bind('<<DragLeave>>', self.on_image_drag_leave)
        
    def start_background_animation(self):
        """Arkaplan animasyonu başlat"""
        self.animation_running = True
        self.animate_separator()
        
    def animate_separator(self):
        """Separator animasyonu"""
        if not self.animation_running:
            return
            
        colors = [self.colors['neon_green'], self.colors['neon_blue'], 
                 self.colors['neon_purple'], self.colors['neon_pink']]
        
        def cycle_colors():
            for color in colors:
                if not self.animation_running:
                    break
                self.separator_frame.configure(bg=color)
                time.sleep(0.5)
                
        def run_animation():
            while self.animation_running:
                cycle_colors()
                
        thread = threading.Thread(target=run_animation, daemon=True)
        thread.start()
        
    def on_mp3_drag_enter(self, event):
        """MP3 drag enter"""
        self.mp3_drop_area.configure(bg=self.colors['neon_blue'])
        self.mp3_drop_label.configure(bg=self.colors['neon_blue'], 
                                     fg=self.colors['bg'],
                                     text=">>> DROP MP3 FILE NOW <<<")
        
    def on_mp3_drag_leave(self, event):
        """MP3 drag leave"""
        self.mp3_drop_area.configure(bg=self.colors['accent'])
        self.mp3_drop_label.configure(bg=self.colors['accent'], 
                                     fg=self.colors['text_dim'],
                                     text="DRAG & DROP MP3 FILE HERE\n>>> OR CLICK BUTTON BELOW <<<")
        
    def on_mp3_drop(self, event):
        """MP3 drop"""
        self.on_mp3_drag_leave(event)
        
        files = self.root.tk.splitlist(event.data)
        if files:
            file_path = files[0]
            if file_path.lower().endswith('.mp3'):
                self.mp3_file = file_path
                filename = os.path.basename(file_path)
                self.mp3_info_label.config(text=f"STATUS: {filename[:30]}...", 
                                         fg=self.colors['success'])
                self.update_status(f"MP3 LOADED: {filename}")
                self.check_ready()
            else:
                self.show_error("ERROR: NOT AN MP3 FILE!")
                
    def on_image_drag_enter(self, event):
        """Image drag enter"""
        self.image_drop_area.configure(bg=self.colors['neon_green'])
        self.image_drop_label.configure(bg=self.colors['neon_green'], 
                                       fg=self.colors['bg'],
                                       text=">>> DROP IMAGE NOW <<<")
        
    def on_image_drag_leave(self, event):
        """Image drag leave"""
        self.image_drop_area.configure(bg=self.colors['accent'])
        self.image_drop_label.configure(bg=self.colors['accent'], 
                                       fg=self.colors['text_dim'],
                                       text="DRAG & DROP IMAGE FILE HERE\n>>> JPG, PNG, GIF, BMP <<<")
        
    def on_image_drop(self, event):
        """Image drop"""
        self.on_image_drag_leave(event)
        
        files = self.root.tk.splitlist(event.data)
        if files:
            file_path = files[0]
            valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')
            if file_path.lower().endswith(valid_extensions):
                self.image_file = file_path
                filename = os.path.basename(file_path)
                self.image_info_label.config(text=f"STATUS: {filename[:30]}...", 
                                           fg=self.colors['success'])
                self.update_status(f"IMAGE LOADED: {filename}")
                self.show_preview()
                self.check_ready()
            else:
                self.show_error("ERROR: UNSUPPORTED IMAGE FORMAT!")
                
    def select_mp3(self):
        """MP3 seçimi"""
        file_path = filedialog.askopenfilename(
            title="SELECT MP3 FILE",
            filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")]
        )
        
        if file_path:
            self.mp3_file = file_path
            filename = os.path.basename(file_path)
            self.mp3_info_label.config(text=f"STATUS: {filename[:30]}...", 
                                     fg=self.colors['success'])
            self.update_status(f"MP3 SELECTED: {filename}")
            self.check_ready()
            
    def select_image(self):
        """Resim seçimi"""
        file_path = filedialog.askopenfilename(
            title="SELECT COVER IMAGE",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("PNG files", "*.png"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.image_file = file_path
            filename = os.path.basename(file_path)
            self.image_info_label.config(text=f"STATUS: {filename[:30]}...", 
                                       fg=self.colors['success'])
            self.update_status(f"IMAGE SELECTED: {filename}")
            self.show_preview()
            self.check_ready()
            
    def show_preview(self):
        """Önizleme göster"""
        try:
            # Resmi yükle
            image = Image.open(self.image_file)
            
            # Retro efekt uygula
            image = image.convert('RGB')
            
            # Boyutlandır
            image.thumbnail((300, 300), Image.Resampling.LANCZOS)
            
            # Retro border ekle
            border_size = 10
            border_color = (255, 0, 110)  # Neon pink
            bordered_image = Image.new('RGB', 
                                     (image.width + border_size*2, 
                                      image.height + border_size*2), 
                                     border_color)
            bordered_image.paste(image, (border_size, border_size))
            
            # Tkinter için hazırla
            self.preview_image = ImageTk.PhotoImage(bordered_image)
            self.preview_label.configure(image=self.preview_image, text="")
            
        except Exception as e:
            self.show_error(f"PREVIEW ERROR: {str(e)}")
            
    def check_ready(self):
        """Hazır durumu kontrol et"""
        if self.mp3_file and self.image_file:
            self.process_button.config(state='normal')
            self.update_status("READY TO INJECT >>> PRESS THE BUTTON!")
        else:
            self.process_button.config(state='disabled')
            
    def add_cover_art(self):
        """Cover art ekle"""
        try:
            self.update_status("PROCESSING >>> INJECTING COVER ART...")
            self.root.update()
            
            # MP3 yükle
            audio = MP3(self.mp3_file)
            
            if audio.tags is None:
                audio.add_tags()
            
            # Resmi oku
            with open(self.image_file, 'rb') as img_file:
                img_data = img_file.read()
            
            # MIME type
            img_extension = os.path.splitext(self.image_file)[1].lower()
            mime_type = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.bmp': 'image/bmp'
            }.get(img_extension, 'image/jpeg')
            
            # Mevcut cover art'ları temizle
            audio.tags.delall('APIC')
            
            # Yeni cover art ekle
            audio.tags.add(
                APIC(
                    encoding=3,
                    mime=mime_type,
                    type=3,
                    desc=u'Cover',
                    data=img_data
                )
            )
            
            # Kaydet
            audio.save()
            
            self.update_status("SUCCESS >>> COVER ART INJECTED!")
            self.show_success("MISSION ACCOMPLISHED!\nCover art successfully injected into MP3!")
            
        except Exception as e:
            self.show_error(f"INJECTION FAILED: {str(e)}")
            
    def update_status(self, message):
        """Durum güncelle"""
        self.status_var.set(f">>> {message} <<<")
        
    def show_error(self, message):
        """Hata mesajı"""
        self.update_status(f"ERROR: {message}")
        messagebox.showerror("ERROR", message)
        
    def show_success(self, message):
        """Başarı mesajı"""
        messagebox.showinfo("SUCCESS", message)
        
    def __del__(self):
        """Destructor"""
        self.animation_running = False

def main():
    """Ana fonksiyon"""
    try:
        from mutagen.mp3 import MP3
        from mutagen.id3 import ID3, APIC
        from PIL import Image
        from tkinterdnd2 import TkinterDnD
    except ImportError as e:
        print("MISSING DEPENDENCIES!")
        print("Please install: pip install mutagen pillow tkinterdnd2")
        return
    
    root = TkinterDnD.Tk()
    app = RetroMP3CoverTool(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        app.animation_running = False
        root.destroy()

if __name__ == "__main__":
    main()
