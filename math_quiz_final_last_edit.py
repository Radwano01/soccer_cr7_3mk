import pygame
import sys
import json
import os
import random
import time
import math 
import subprocess
from typing import List, Dict, Optional, Tuple

# --------------------
# 1. KONFIGÜRASYON VE SABİTLER
# --------------------
pygame.init()
pygame.joystick.init()  # Joystick desteği için
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512) # Ses modülünü başlatır

# Ekran Ayarları
WIDTH, HEIGHT = 1920, 1080 # <<< FULL HD ÇÖZÜNÜRLÜK
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Matematik Dehası - Final V7.5 (İki Kişilik Mod)")
CLOCK = pygame.time.Clock()

# Modern Renk Paleti
COLORS = {
    "BG": (245, 245, 245),      # Yumuşak Beyaz
    "DARK": (30, 41, 59),       # Derin Kömür Mavi
    "BLUE": (37, 99, 235),      # Elektrik Mavisi
    "BLUE_HOVER": (29, 78, 216),# Koyu Elektrik Mavisi
    "GREEN": (16, 185, 129),    # Zümrüt Yeşili
    "RED": (244, 63, 94),       # Vişne Kırmızısı
    "YELLOW": (251, 191, 36),   # Altın Sarısı
    "PURPLE": (124, 58, 237),   # Lavanta Moru
    "PURPLE_HOVER": (109, 40, 217),
    "WHITE": (255, 255, 255),
    "GRAY": (148, 163, 184),    # Soğuk Orta Gri
    "TEXT": (51, 65, 85),       # Koyu Mavi Gri
    "PANEL": (255, 255, 255),
    "P1": (249, 115, 22),       # Koyu Somon Turuncusu
    "P2": (6, 182, 212)         # Deniz Köpüğü Turkuaz
}

# Font Yönetimi (Yeni çözünürlüğe göre büyütüldü)
def get_font(size, bold=False):
    fonts = ["segoeui", "arial", "helvetica", "dejavusans", "freesansbold"]
    return pygame.font.SysFont(fonts, size, bold=bold)

FONTS = {
    "small": get_font(30),      
    "medium": get_font(40),     
    "large": get_font(60, bold=True),   
    "title": get_font(100, bold=True),  
    "round_btn": get_font(36, bold=True),
    "quiz_large": get_font(80, bold=True) # İki kişilik mod için büyük font
}

# Dosya Yolları
FILES = {
    "questions": "data/questions.json",
    "highscore": "data/highscore.json",
    "sounds": "data/music1.mp3.mp3"  # Arka plan müziği dosyası
}

# Varsayılan Ayarlar
DEFAULT_SETTINGS = {
    "music": True,
    "sfx": True,
    "fullscreen": False,
    "time_per_question": 30,
    "mode": "MCQ" # Bu tek kişilik mod için
}

# --------------------
# 2. YARDIMCI SINIFLAR
# --------------------

class DataManager:
    @staticmethod
    def init_files():
        if not os.path.exists(FILES["questions"]):
            DataManager.save_json(FILES["questions"])
        if not os.path.exists(FILES["highscore"]):
            DataManager.save_json(FILES["highscore"], {"kolay": 0, "orta": 0, "zor": 0})

    @staticmethod
    def load_json(path, default=None):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return default if default is not None else {}

    @staticmethod
    def save_json(path, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

class SoundManager:
    
    def __init__(self, bgm_file="background_music.mp3", sfx_volume=0.7, bgm_volume=0.3):
        self.sounds = {}
        self.sfx_volume = sfx_volume
        self.bgm_volume = bgm_volume
        # BGM (Background Music) için yeni özellik
        # FILES["sounds"] artık klasör yolunu tutuyor.
        self.bgm_path = os.path.join(FILES["sounds"], "music1.mp3")  
        self.bgm_volume = 0.3
        
        self.load_sfx()

    def load_sfx(self):
        """Ses efektlerini (SFX) klasörden yükler."""
        if not os.path.isdir(FILES["sounds"]):
            print(f"UYARI: Ses klasörü bulunamadı: {FILES['sounds']}")
            return

        for fname in os.listdir(FILES["sounds"]):
            if fname.lower().endswith(('.wav', '.ogg', '.mp3')):
                key = os.path.splitext(fname)[0]
                full_path = os.path.join(FILES["sounds"], fname)
                try:
                    sound = pygame.mixer.Sound(full_path)
                    sound.set_volume(self.sfx_volume) # Varsayılan SFX sesi ayarla
                    self.sounds[key] = sound
                except pygame.error as e:
                    print(f"HATA: '{key}' sesi yüklenemedi: {e}")

    # ... (Diğer play, load_bgm, play_bgm, set_bgm_volume metotları aynı kalır) ...
    # play_bgm metodundaki `load_bgm` çağrısı artık doğru çalışacaktır.
    
    def play(self, key, enabled):
        if enabled and key in self.sounds:
            try:
                self.sounds[key].play()
            except: pass
            
    def load_bgm(self):
        """Arka plan müziği dosyasının yolunu kontrol eder."""
        if not os.path.exists(self.bgm_path):
            print(f"UYARI: BGM dosyası bulunamadı: {self.bgm_path}")
            return False
        return True

    def play_bgm(self, enabled, volume=None):
        """Arka plan müziğini başlatır veya durdurur."""
        
        # Eğer BGM kapalıysa durdur
        if not enabled:
            pygame.mixer.music.stop()
            return

        # Müziği başlat
        if not pygame.mixer.music.get_busy():
            if self.load_bgm():
                try:
                    pygame.mixer.music.load(self.bgm_path)
                    # -1 döngü anlamına gelir, müzik sürekli çalar.
                    pygame.mixer.music.play(-1) 
                    
                    # Sesi ayarla (Eğer volume ayarı verilmişse)
                    if volume is not None:
                         self.set_bgm_volume(volume)
                    else:
                         self.set_bgm_volume(self.bgm_volume) # Varsayılan ayarı kullan
                         
                except pygame.error as e:
                    print(f"HATA: BGM çalınamadı. Dosya formatı hatası olabilir: {e}")

    def set_bgm_volume(self, volume: float):
        """Arka plan müziğinin ses seviyesini ayarlar."""
        self.bgm_volume = max(0.0, min(1.0, volume)) # Sesi 0.0-1.0 arasına kısıtla
        pygame.mixer.music.set_volume(self.bgm_volume)

    def play(self, key, enabled):
        if enabled and key in self.sounds:
            try:
                self.sounds[key].play()
            except: pass

class Utils:
    @staticmethod
    def wrap_text(text, font, max_width):
        words = text.split(' ')
        lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        lines.append(' '.join(current_line))
        return lines

    @staticmethod
    def normalize_answer(s: str) -> str:
        if not s: return ""
        s = s.strip().lower().replace(" ", "")
        s = s.replace("²", "^2").replace("³", "^3").replace("⁴", "^4")
        return s

    @staticmethod
    def generate_mcq_options(correct: str) -> List[str]:
        # Basitçe 4 seçenek üretme mantığı
        options = [correct]
        try:
            val = float(correct)
            for i in [-1, 1, 2, -2]:
                cand = str(int(val + i)) if (val+i).is_integer() else f"{val+i:.1f}"
                if cand not in options: options.append(cand)
        except:
            suffixes = [" + C", " - 1", "²", "/2", " + 1", "x"]
            for s in suffixes:
                cand = correct + s
                if cand not in options: options.append(cand)
        
        while len(options) < 4:
            options.append(f"{correct} ({len(options)})")
        
        final_opts = options[:4]
        random.shuffle(final_opts)
        
        if correct not in final_opts:
            final_opts[0] = correct
            random.shuffle(final_opts)
            
        return final_opts

# --------------------
# 3. UI BİLEŞENLERİ & EFEKTLER
# --------------------

class MathBackgroundEffect:
    """Arka planda kayan matematik sembolleri efekti"""
    def __init__(self, count=150): 
        self.particles = []
        self.symbols = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", 
                       "+", "-", "x", "÷", "=", "π", "∑", "√", "∫", "%"]
        self.font = get_font(30, bold=True) 
        
        for _ in range(count):
            self.particles.append(self.create_particle(random_y=True))

    def create_particle(self, random_y=False):
        return {
            "x": random.randint(0, WIDTH),
            "y": random.randint(0, HEIGHT) if random_y else random.randint(-200, -10),
            "speed": random.uniform(2.0, 5.0), 
            "char": random.choice(self.symbols),
            "alpha": random.randint(70, 180),
            "size": random.randint(25, 40)
        }

    def update(self):
        for p in self.particles:
            p["y"] += p["speed"]
            if p["y"] > HEIGHT:
                new_p = self.create_particle()
                p["x"] = new_p["x"]
                p["y"] = new_p["y"]
                p["char"] = new_p["char"]
                p["speed"] = new_p["speed"]
                

    def draw(self, surface):
        for p in self.particles:
            text_surf = self.font.render(p["char"], True, (180, 190, 200)) 
            text_surf.set_alpha(p["alpha"])
            surface.blit(text_surf, (p["x"], p["y"]))

class Button:
    # Mevcut dikdörtgen buton sınıfı
    def __init__(self, x, y, w, h, text, color=COLORS["BLUE"], hover_color=COLORS["BLUE_HOVER"], text_color=COLORS["WHITE"], action=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.action = action
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        # Gölge
        pygame.draw.rect(surface, (0, 0, 0, 30), (self.rect.x+4, self.rect.y+8, self.rect.w, self.rect.h), border_radius=15)
        # Buton
        pygame.draw.rect(surface, color, self.rect, border_radius=15)
        if self.color == COLORS["PANEL"]:
            pygame.draw.rect(surface, COLORS["GRAY"], self.rect, 3, border_radius=15)
        
        txt_surf = FONTS["medium"].render(self.text, True, self.text_color)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

    def update(self, pos, clicked):
        self.is_hovered = self.rect.collidepoint(pos)
        if self.is_hovered and clicked:
            if self.action: self.action()
            return True
        return False

# Yuvarlak Buton Sınıfı
class CircularButton:
    def __init__(self, center_x, center_y, radius, text, color=COLORS["PURPLE"], hover_color=COLORS["PURPLE_HOVER"], text_color=COLORS["WHITE"], action=None):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.text = text if text else ""
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.action = action
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        # Buton gölgesi
        pygame.draw.circle(surface, (0, 0, 0, 30), (self.center_x + 4, self.center_y + 8), self.radius)
        # Buton kendisi
        pygame.draw.circle(surface, color, (self.center_x, self.center_y), self.radius)
        
        # Sadece self.text doluysa metin çizilir
        if self.text:
            txt_surf = FONTS["round_btn"].render(self.text, True, self.text_color)
            txt_rect = txt_surf.get_rect(center=(self.center_x, self.center_y))
            surface.blit(txt_surf, txt_rect)

    def update(self, pos, clicked):
        # Fare pozisyonunun butona uzaklığını kontrol et (Karekök formülü)
        distance = math.sqrt((pos[0] - self.center_x)**2 + (pos[1] - self.center_y)**2)
        self.is_hovered = distance <= self.radius
        
        if self.is_hovered and clicked:
            if self.action: self.action()
            return True
        return False

class InputBox:
    def __init__(self, x, y, w, h, text='', player_color=COLORS["GRAY"]):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.active = False # Başlangıçta inaktif
        self.base_color = player_color
        self.color = player_color

    def handle_event(self, event, submit_key=pygame.K_RETURN, skip_mouse=False):
        # Skip mouse handling if it's being handled externally (for two-player mode)
        if not skip_mouse and event.type == pygame.MOUSEBUTTONDOWN:
            # Kutunun aktif olup olmaması, Game sınıfı tarafından yönetilir (check_two_player_answer)
            if self.rect.collidepoint(event.pos):
                self.active = True
                self.color = COLORS["BLUE"]
            else:
                self.active = False
                self.color = self.base_color
        
        # Process keyboard events if input is active
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == submit_key:
                val = self.text
                return val
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if event.key not in [pygame.K_ESCAPE, pygame.K_F1, pygame.K_F2, pygame.K_F3, pygame.K_TAB]:
                    if len(event.unicode) > 0 and event.unicode.isprintable():
                        self.text += event.unicode
        return None

    def draw(self, surface):
        # ... (Önceki çizim mantığı aynı) ...
        pygame.draw.rect(surface, COLORS["WHITE"], self.rect, border_radius=10)
        pygame.draw.rect(surface, self.color, self.rect, 4, border_radius=10)
        txt_surf = FONTS["medium"].render(self.text, True, COLORS["TEXT"])
        
        # Metni input kutusunun içine dikey olarak ortalamak için
        text_x = self.rect.x + 20
        text_y = self.rect.y + (self.rect.height - txt_surf.get_height()) // 2
        
        surface.blit(txt_surf, (text_x, text_y))

# --------------------
# 4. OYUN YÖNETİCİSİ
# --------------------

class Game:
    def __init__(self):
        DataManager.init_files()
        self.settings = DEFAULT_SETTINGS.copy()
        self.highscores = DataManager.load_json(FILES["highscore"])
        self.sound_manager = SoundManager()
        self.state = "MENU"
        self.current_level = "kolay"
        self.quiz_data = []
        self.current_q_index = 0
        self.score = 0
        self.start_time = 0
        self.powerups = {"extra": 1, "skip": 1, "hint": 1}
        self.feedback = {"msg": "", "color": COLORS["TEXT"], "time": 0}
        self.sound_manager.play_bgm(enabled=self.settings.get("music", True), volume=0.3)
        self.bg_effect = MathBackgroundEffect(count=150)
        self.sound_manager = SoundManager()
        self.state = "MENU"
        self.sound_manager.play_bgm(enabled=self.settings.get("music", True), volume=0.3) 
        self.bg_effect = MathBackgroundEffect(count=150)


        # UI Boyutları ve Konumları (1920x1080'e göre ayarlandı)
        self.BTN_W, self.BTN_H = 300, 80
        self.GAP_Y = 30
        self.CX, self.CY = WIDTH // 2, HEIGHT // 2
        
        # TEK OYUNCULU Giriş Kutusu (Quiz'de kullanılacak)
        self.input_box = InputBox(
            self.CX - 400, 
            HEIGHT * 0.75, 
            800, 
            70 
        )
        self.mcq_buttons = []
        self.buttons = {}
        
        # İKİ OYUNCULU MOD DEĞİŞKENLERİ
        self.p1_score = 0
        self.p2_score = 0
        self.p1_input = InputBox(WIDTH * 0.25 - 200, HEIGHT * 0.75, 400, 70, player_color=COLORS["P1"])
        self.p2_input = InputBox(WIDTH * 0.75 - 200, HEIGHT * 0.75, 400, 70, player_color=COLORS["P2"])
        # Quiz durumunu yönetecek değişkenler
        self.two_player_q_answered = {"p1": False, "p2": False}
        self.two_player_q_correct = {"p1": None, "p2": None}  # Track correctness for penalty detection
        self.two_player_quiz_length = 10 # Varsayılan 10 soru
        self.winner = None
        self.two_player_mode = "Classic"  # İki kişilik mod için MCQ/Classic seçimi
        self.p1_mcq_buttons = []  # P1 için MCQ butonları
        self.p2_mcq_buttons = []  # P2 için MCQ butonları
        
        # Penalty shootout variables
        self.penalty_active = False
        self.penalty_goalkeeper = None  # "p1" or "p2"
        self.penalty_attacker = None  # "p1" or "p2"
        self.penalty_handled = False  # Flag to ensure penalty is only handled once
        self.penalty_start_time = None  # Time when penalty started (to pause timer)
        self.time_remaining_before_penalty = None  # Time remaining when penalty started
        
        # JOYSTICK DEĞİŞKENLERİ
        self.joysticks = []  # Bağlı joystick'ler
        self.init_joysticks()
        self.mcq_selected_index = 0  # Tek kişilik MCQ için seçili seçenek
        self.p1_mcq_selected_index = 0  # P1 için seçili seçenek
        self.p2_mcq_selected_index = 0  # P2 için seçili seçenek
        self.joystick_cooldown = 0  # Joystick girişi için bekleme süresi

        # Mod değiştirme (dikdörtgen) butonu (EN ALT konumu)
        self.mode_toggle_button = Button(
            self.CX - 150, HEIGHT - 120, 300, 60, "Mod Değiştir", 
            COLORS["BLUE_HOVER"], text_color=COLORS["WHITE"], 
            action=self.toggle_mode
        )

        # Admin Paneli UI Öğeleri (Önceki koddan)
        admin_input_w, admin_input_h = 1000, 70
        admin_y_start = HEIGHT * 0.45 
        
        self.admin_current_level = "kolay"
        
        # Admin Input Kutuları (Merkezlenmiş)
        self.admin_question_input = InputBox(
            self.CX - admin_input_w // 2, 
            admin_y_start, 
            admin_input_w, 
            admin_input_h, 
            text="Soru metni buraya...", player_color=COLORS["GRAY"]
        )
        self.admin_answer_input = InputBox(
            self.CX - admin_input_w // 2, 
            admin_y_start + 100, 
            admin_input_w, 
            admin_input_h, 
            text="Cevap (Kesin Değer)", player_color=COLORS["GRAY"]
        )
        # ... diğer admin butonları ...
        self.admin_buttons = {
            "save": Button(self.CX - 150 - 200, HEIGHT * 0.85, 300, 80, "Soru KAYDET", color=COLORS["GREEN"], action=self.save_new_question),
            "delete_last": Button(self.CX - 150 + 200, HEIGHT * 0.85, 300, 80, "Son Soruyu SİL", color=COLORS["RED"], action=self.delete_last_question),
            
            "level_kolay": Button(self.CX - 450, HEIGHT * 0.2, 200, 60, "KOLAY", color=COLORS["GREEN"], action=lambda: self.set_admin_level("kolay")),
            "level_orta": Button(self.CX - 100, HEIGHT * 0.2, 200, 60, "ORTA", color=COLORS["YELLOW"], action=lambda: self.set_admin_level("orta")),
            "level_zor": Button(self.CX + 250, HEIGHT * 0.2, 200, 60, "ZOR", color=COLORS["RED"], action=lambda: self.set_admin_level("zor")),
        }
        
        self.init_menu_buttons()
        
        # Yuvarlak butonu en altta, Mod Değiştir'in yukarısında.
        self.gamemodes_button = CircularButton(
            center_x=self.CX, 
            center_y=HEIGHT - 210, 
            radius=70, 
            text="MODLAR", 
            action=lambda: self.set_state("MODES_MENU")
        )

    def toggle_mode(self):
        """MCQ ve Klasik mod arasında geçiş yapar."""
        self.settings["mode"] = "Classic" if self.settings["mode"] == "MCQ" else "MCQ"
        self.sound_manager.play("correct", self.settings["sfx"])

    def init_joysticks(self):
        """Bağlı joystick'leri başlatır, hatalı cihazları atlar."""
        self.joysticks = []
        
        print(f"\n🔍 Joystick taraması başlatılıyor... (Algılanan: {pygame.joystick.get_count()})")
        
        # Kaç joystick varsa o kadar döngü kurar
        for i in range(pygame.joystick.get_count()): 
            try:
                joy = pygame.joystick.Joystick(i)
                joy.init()
                self.joysticks.append(joy)
                
                # Detaylı bilgi göster
                num_buttons = joy.get_numbuttons()
                num_axes = joy.get_numaxes()
                num_hats = joy.get_numhats()
                
                print(f"  ✅ Joystick {i}: {joy.get_name()}")
                print(f"     - Butonlar: {num_buttons}, Eksenler: {num_axes}, HAT (D-pad): {num_hats}")
                
            except pygame.error as e:
                # Eğer bir cihaz başlatılamazsa, onu atla
                print(f"  ❌ HATA: Joystick {i} başlatılamadı: {e}. Atlanıyor.")
                
        if self.joysticks:
            print(f"\n✅ Toplam {len(self.joysticks)} aktif joystick bağlandı.")
            print("💡 İPUCU: Butonları test etmek için herhangi bir butona basın (konsolda göreceksiniz)\n")
        else:
            print("\n⚠️ Hiçbir joystick algılanmadı.\n")

    def handle_joystick_mcq_navigation(self, joy_id, direction):
        """
        Joystick ile MCQ seçenekleri arasında gezinme.
        direction: 'up' veya 'down'
        """
        if self.state == "QUIZ" and self.settings["mode"] == "MCQ":
            # Tek kişilik mod - herhangi bir joystick kullanabilir
            if self.mcq_buttons:  # Check if buttons exist
                if direction == "up":
                    self.mcq_selected_index = (self.mcq_selected_index - 1) % len(self.mcq_buttons)
                elif direction == "down":
                    self.mcq_selected_index = (self.mcq_selected_index + 1) % len(self.mcq_buttons)
                self.sound_manager.play("click", self.settings["sfx"])
            
        elif self.state == "TWO_PLAYER_QUIZ" and self.two_player_mode == "MCQ":
            # İki kişilik mod - joystick 0 = P1, joystick 1 = P2
            if joy_id == 0 and not self.two_player_q_answered["p1"]:
                if self.p1_mcq_buttons:  # Check if buttons exist
                    if direction == "up":
                        self.p1_mcq_selected_index = (self.p1_mcq_selected_index - 1) % len(self.p1_mcq_buttons)
                    elif direction == "down":
                        self.p1_mcq_selected_index = (self.p1_mcq_selected_index + 1) % len(self.p1_mcq_buttons)
                    self.sound_manager.play("click", self.settings["sfx"])
            elif joy_id == 1 and not self.two_player_q_answered["p2"]:
                if self.p2_mcq_buttons:  # Check if buttons exist
                    if direction == "up":
                        self.p2_mcq_selected_index = (self.p2_mcq_selected_index - 1) % len(self.p2_mcq_buttons)
                    elif direction == "down":
                        self.p2_mcq_selected_index = (self.p2_mcq_selected_index + 1) % len(self.p2_mcq_buttons)
                    self.sound_manager.play("click", self.settings["sfx"])

    def handle_joystick_mcq_select(self, joy_id):
        """
        Joystick butonu ile MCQ seçeneğini onaylama.
        """
        if self.state == "QUIZ" and self.settings["mode"] == "MCQ":
            if self.mcq_buttons and 0 <= self.mcq_selected_index < len(self.mcq_buttons):
                btn, val = self.mcq_buttons[self.mcq_selected_index]
                self.check_answer(val)
                
        elif self.state == "TWO_PLAYER_QUIZ" and self.two_player_mode == "MCQ":
            if joy_id == 0 and not self.two_player_q_answered["p1"]:
                if self.p1_mcq_buttons and 0 <= self.p1_mcq_selected_index < len(self.p1_mcq_buttons):
                    btn, val = self.p1_mcq_buttons[self.p1_mcq_selected_index]
                    self.check_two_player_answer("p1", val)
            elif joy_id == 1 and not self.two_player_q_answered["p2"]:
                if self.p2_mcq_buttons and 0 <= self.p2_mcq_selected_index < len(self.p2_mcq_buttons):
                    btn, val = self.p2_mcq_buttons[self.p2_mcq_selected_index]
                    self.check_two_player_answer("p2", val)
    
    def handle_joystick_button_press(self, joy_id, button_id):
        """
        Joystick butonu basıldığında genel işleme.
        Tüm menüler ve modlar için çalışır.
        """
        # Debug: Print button press info (always visible)
        if self.joysticks and joy_id < len(self.joysticks):
            joy_name = self.joysticks[joy_id].get_name()
            print(f"🎮 Joystick {joy_id} ({joy_name}): Button {button_id} pressed | State: {self.state}")
        else:
            print(f"🎮 Joystick {joy_id}: Button {button_id} pressed | State: {self.state} (⚠️ Joystick not found in list)")
        
        # MCQ Quiz mode - select answer
        if self.state == "QUIZ" and self.settings["mode"] == "MCQ":
            print(f"   → Handling MCQ select in QUIZ mode")
            self.handle_joystick_mcq_select(joy_id)
            return
        
        # Two Player MCQ Quiz mode
        if self.state == "TWO_PLAYER_QUIZ" and self.two_player_mode == "MCQ":
            print(f"   → Handling MCQ select in TWO_PLAYER_QUIZ mode")
            self.handle_joystick_mcq_select(joy_id)
            return
        
        # Menu navigation - simulate click at center for main menu buttons
        if self.state == "MENU":
            print(f"   → Handling button press in MENU")
            # Simulate click on center to activate buttons
            mouse_pos = pygame.mouse.get_pos()
            handled = False
            for btn in self.buttons["menu"]:
                if btn.update(mouse_pos, True):
                    handled = True
                    print(f"   → Menu button clicked: {btn.text}")
                    break
            if not handled:
                if self.mode_toggle_button.update(mouse_pos, True):
                    print(f"   → Mode toggle button clicked")
                elif self.gamemodes_button.update(mouse_pos, True):
                    print(f"   → Gamemodes button clicked")
            return
        
        # Modes menu
        if self.state == "MODES_MENU":
            print(f"   → Handling button press in MODES_MENU")
            mouse_pos = pygame.mouse.get_pos()
            for btn in self.buttons["modes_menu"]:
                if btn.update(mouse_pos, True):
                    print(f"   → Modes menu button clicked: {btn.text}")
                    return
            if self.buttons["back"].update(mouse_pos, True):
                print(f"   → Back button clicked")
            return
        
        # Two player setup
        if self.state == "TWO_PLAYER_SETUP":
            print(f"   → Handling button press in TWO_PLAYER_SETUP")
            mouse_pos = pygame.mouse.get_pos()
            for btn in self.buttons["two_player_setup"]:
                if btn.update(mouse_pos, True):
                    print(f"   → Two player setup button clicked: {btn.text}")
                    return
            if self.buttons["back_to_modes"].update(mouse_pos, True):
                print(f"   → Back to modes button clicked")
            elif self.two_player_mode_toggle_button.update(mouse_pos, True):
                print(f"   → Two player mode toggle clicked")
            return
        
        # Game over screens - go back to menu
        if self.state in ["GAMEOVER", "TWO_PLAYER_GAMEOVER"]:
            print(f"   → Returning to menu from {self.state}")
            self.set_state("MENU")
            return
        
        # Settings, Highscore, Admin - go back to menu
        if self.state in ["SETTINGS", "HIGHSCORE", "ADMIN"]:
            print(f"   → Handling button press in {self.state}")
            mouse_pos = (self.CX, self.CY)
            if self.buttons["back"].update(mouse_pos, True):
                print(f"   → Back button clicked")
            return
        
        # If we reach here, button was pressed but no action was taken
        print(f"   ⚠️ Button press not handled for state: {self.state}")

    def toggle_two_player_mode(self):
        """İki kişilik mod için MCQ ve Klasik mod arasında geçiş yapar."""
        self.two_player_mode = "Classic" if self.two_player_mode == "MCQ" else "MCQ"
        self.sound_manager.play("correct", self.settings["sfx"])

    def init_menu_buttons(self):
        # ... (Önceki menü butonları hesaplamaları) ...
        y_start = self.CY - 120 
        w_main, h_main = 300, 80
        w_sub, h_sub = 250, 70
        gap_y = h_main + 25
        gap_x = 50
        x_center = self.CX - w_main/2
        x1 = x_center - w_main - gap_x
        x2 = x_center
        x3 = x_center + w_main + gap_x
        y_sub = y_start + gap_y
        total_width = (3 * w_sub) + (2 * gap_x) 
        x_start_sub = self.CX - (total_width / 2)
        x1_sub = x_start_sub 
        x2_sub = x1_sub + w_sub + gap_x 
        x3_sub = x2_sub + w_sub + gap_x 

        self.buttons["menu"] = [
            Button(x1, y_start, w_main, h_main, "KOLAY", color=COLORS["GREEN"], action=lambda: self.start_quiz("kolay")),
            Button(x2, y_start, w_main, h_main, "ORTA", color=COLORS["YELLOW"], action=lambda: self.start_quiz("orta")),
            Button(x3, y_start, w_main, h_main, "ZOR", color=COLORS["RED"], action=lambda: self.start_quiz("zor")),
            
            Button(x1_sub, y_sub, w_sub, h_sub, "Ayarlar", color=COLORS["GRAY"], action=lambda: self.set_state("SETTINGS")),
            Button(x2_sub, y_sub, w_sub, h_sub, "Skorlar", color=COLORS["GRAY"], action=lambda: self.set_state("HIGHSCORE")),
            Button(x3_sub, y_sub, w_sub, h_sub, "Admin Panel", color=COLORS["DARK"], action=lambda: self.set_state("ADMIN")),
            
            Button(self.CX - 150, y_sub + h_sub + 40, 300, 70, "Çıkış", color=COLORS["RED"], action=lambda: sys.exit())
        ]
        
        # MODLAR MENÜSÜ BUTONLARI
        modes_y_start = self.CY - 150
        modes_gap = 120
        self.buttons["modes_menu"] = [
            Button(self.CX - 350, modes_y_start, 700, 80, "Tek Kişilik (Classic/MCQ)", color=COLORS["BLUE"], action=lambda: self.set_state("MENU")),
            Button(self.CX - 350, modes_y_start + modes_gap, 700, 80, "İKİ KİŞİLİK YARIŞ", color=COLORS["P1"], action=lambda: self.set_state("TWO_PLAYER_SETUP"))
            # Buraya gelecekte Zamana Karşı, vs. modları eklenebilir.
        ]
        
        # İKİ KİŞİLİK ZORLUK SEÇİM BUTONLARI
        two_player_y = self.CY + 50
        self.buttons["two_player_setup"] = [
            Button(self.CX - 450, two_player_y, 250, 70, "KOLAY", color=COLORS["GREEN"], action=lambda: self.start_two_player_quiz("kolay")),
            Button(self.CX - 125, two_player_y, 250, 70, "ORTA", color=COLORS["YELLOW"], action=lambda: self.start_two_player_quiz("orta")),
            Button(self.CX + 200, two_player_y, 250, 70, "ZOR", color=COLORS["RED"], action=lambda: self.start_two_player_quiz("zor")),
        ]
        
        # İki kişilik mod değiştirme butonu
        self.two_player_mode_toggle_button = Button(
            self.CX - 150, two_player_y + 120, 300, 60, "Mod Değiştir",
            COLORS["BLUE_HOVER"], text_color=COLORS["WHITE"],
            action=self.toggle_two_player_mode
        )
        
        # Geri Butonu
        self.buttons["back"] = Button(30, 30, 150, 60, "← Geri", color=COLORS["GRAY"], action=lambda: self.set_state("MENU"))
        self.buttons["back_to_modes"] = Button(30, 30, 150, 60, "← Geri", color=COLORS["GRAY"], action=lambda: self.set_state("MODES_MENU"))


    def set_state(self, new_state):
        self.state = new_state
        # İki kişilik quiz bittiğinde skorları sıfırlayalım
        if new_state == "MENU":
            self.p1_score = 0
            self.p2_score = 0
            self.winner = None
        time.sleep(0.1)

    # ---------------- TEK KİŞİLİK QUIZ MANTIKLARI ----------------
    
    def start_quiz(self, level):
        all_q = DataManager.load_json(FILES["questions"])
        self.quiz_data = all_q.get(level, [])
        # ... (MCQ ve shuffle mantığı) ...
        for q in self.quiz_data:
            if self.settings["mode"] == "MCQ":
                q["mcq_opts"] = Utils.generate_mcq_options(q["a"])
        
        if self.quiz_data:
            random.shuffle(self.quiz_data)
        
        self.current_level = level
        self.current_q_index = 0
        self.score = 0
        self.powerups = {"extra": 1, "skip": 1, "hint": 1}
        self.start_turn()
        self.set_state("QUIZ")
        
        if self.settings["mode"] == "Classic":
            self.input_box.text = ""
            self.input_box.active = False
            self.input_box.color = COLORS["GRAY"]
            
    # Diğer tek kişilik metotlar (check_answer, next_question, end_game, use_powerup) değişmedi

    def start_turn(self):
        self.start_time = time.time()
        self.feedback = {"msg": "", "time": 0}
        self.input_box.text = ""
        self.mcq_selected_index = 0  # Joystick seçimini sıfırla
        # ... (MCQ butonları yerleştirme mantığı) ...
        
        if self.settings["mode"] == "MCQ" and self.current_q_index < len(self.quiz_data):
            opts = self.quiz_data[self.current_q_index].get("mcq_opts", [])
            self.mcq_buttons = []
            
            mcq_btn_w = 900
            mcq_x = self.CX - mcq_btn_w // 2
            mcq_y_start = HEIGHT * 0.45 
            mcq_gap = 100 
            
            for i, opt in enumerate(opts):
                btn = Button(
                    mcq_x, 
                    mcq_y_start + i * mcq_gap, 
                    mcq_btn_w, 
                    70, 
                    f"{opt}", 
                    color=COLORS["PANEL"], 
                    hover_color=COLORS["BLUE"], 
                    text_color=COLORS["DARK"]
                ) 
                self.mcq_buttons.append((btn, opt))

    def check_answer(self, user_ans):
        correct_ans = self.quiz_data[self.current_q_index]["a"]
        if Utils.normalize_answer(str(user_ans)) == Utils.normalize_answer(str(correct_ans)):
            self.score += 10
            self.show_feedback("Doğru! (+10 Puan)", COLORS["GREEN"])
            self.sound_manager.play("correct", self.settings["sfx"])
        else:
            self.score = max(0, self.score - 5) 
            self.show_feedback(f"Yanlış! Cevap: {correct_ans}", COLORS["RED"])
            self.sound_manager.play("wrong", self.settings["sfx"])
        
        self.next_question()

    def show_feedback(self, msg, color):
        self.feedback = {"msg": msg, "color": color, "time": time.time()}
        self.draw()
        pygame.display.flip()
        time.sleep(1.2)

    def next_question(self):
        self.current_q_index += 1
        if self.current_q_index >= len(self.quiz_data):
            self.end_game()
        else:
            self.start_turn()

    def end_game(self):
        if self.score > self.highscores.get(self.current_level, 0):
            self.highscores[self.current_level] = self.score
            DataManager.save_json(FILES["highscore"], self.highscores)
        self.set_state("GAMEOVER")

    def use_powerup(self, p_type):
        if self.powerups.get(p_type, 0) > 0:
            self.powerups[p_type] -= 1
            self.sound_manager.play("powerup", self.settings["sfx"])
            
            if p_type == "extra":
                self.start_time += 15 
                self.feedback = {"msg": "+15 Saniye Eklendi!", "color": COLORS["GREEN"], "time": time.time()}
            
            elif p_type == "skip":
                self.show_feedback("Soru Atlandı!", COLORS["YELLOW"])
                self.next_question()
            
            elif p_type == "hint":
                ans = self.quiz_data[self.current_q_index]["a"]
                hint = ans[:3] + "..." if len(ans) > 3 else "İpucu: " + ans
                self.feedback = {"msg": f"İpucu: {hint}", "color": COLORS["BLUE"], "time": time.time()}
        else:
            self.feedback = {"msg": "Hakkın kalmadı!", "color": COLORS["GRAY"], "time": time.time()}
            
    # ---------------- İKİ KİŞİLİK MOD MANTIKLARI ----------------
    
    def start_two_player_quiz(self, level):
        all_q = DataManager.load_json(FILES["questions"])
        self.quiz_data = all_q.get(level, [])
        
        if len(self.quiz_data) < self.two_player_quiz_length:
             self.show_feedback(f"'{level.upper()}' seviyesinde {self.two_player_quiz_length} soru yok!", COLORS["RED"])
             return

        # MCQ modunda seçenekleri oluştur
        for q in self.quiz_data:
            if self.two_player_mode == "MCQ":
                q["mcq_opts"] = Utils.generate_mcq_options(q["a"])

        random.shuffle(self.quiz_data)
        self.quiz_data = self.quiz_data[:self.two_player_quiz_length] # Sadece 10 soru kullan
        
        self.current_level = level
        self.current_q_index = 0
        self.p1_score = 0
        self.p2_score = 0
        self.winner = None
        self.start_two_player_turn()
        self.set_state("TWO_PLAYER_QUIZ")
        
    def start_two_player_turn(self):
        self.start_time = time.time()
        self.two_player_q_answered = {"p1": False, "p2": False}
        self.two_player_q_correct = {"p1": None, "p2": None}  # Reset correctness tracking
        self.p1_input.text = ""
        self.p2_input.text = ""
        self.p1_input.active = True
        self.p2_input.active = True
        self.p1_mcq_selected_index = 0  # P1 joystick seçimini sıfırla
        self.p2_mcq_selected_index = 0  # P2 joystick seçimini sıfırla
        self.penalty_active = False  # Reset penalty state
        self.penalty_goalkeeper = None
        self.penalty_attacker = None
        self.penalty_handled = False  # Reset penalty handled flag
        
        # MCQ modunda butonları oluştur
        if self.two_player_mode == "MCQ" and self.current_q_index < len(self.quiz_data):
            opts = self.quiz_data[self.current_q_index].get("mcq_opts", [])
            self.p1_mcq_buttons = []
            self.p2_mcq_buttons = []
            
            mcq_btn_w = 350
            mcq_btn_h = 60
            mcq_gap = 75
            mcq_y_start = HEIGHT * 0.48  # Moved down from 0.40 to avoid overlapping with "Puan"
            
            # P1 butonları (sol taraf)
            p1_x = WIDTH * 0.25 - mcq_btn_w // 2
            for i, opt in enumerate(opts):
                btn = Button(
                    p1_x, mcq_y_start + i * mcq_gap,
                    mcq_btn_w, mcq_btn_h,
                    f"{opt}",
                    color=COLORS["PANEL"],
                    hover_color=COLORS["P1"],
                    text_color=COLORS["DARK"]
                )
                self.p1_mcq_buttons.append((btn, opt))
            
            # P2 butonları (sağ taraf)
            p2_x = WIDTH * 0.75 - mcq_btn_w // 2
            for i, opt in enumerate(opts):
                btn = Button(
                    p2_x, mcq_y_start + i * mcq_gap,
                    mcq_btn_w, mcq_btn_h,
                    f"{opt}",
                    color=COLORS["PANEL"],
                    hover_color=COLORS["P2"],
                    text_color=COLORS["DARK"]
                )
                self.p2_mcq_buttons.append((btn, opt))

    def check_two_player_answer(self, player, user_ans):
        if self.two_player_q_answered[player]: return # Zaten cevapladıysa tekrar puan vermez
        
        correct_ans = self.quiz_data[self.current_q_index]["a"]
        
        score_diff = 10 # Her soru 10 puan değerinde
        is_correct = Utils.normalize_answer(str(user_ans)) == Utils.normalize_answer(str(correct_ans))
        
        self.two_player_q_answered[player] = True
        self.two_player_q_correct[player] = is_correct
        
        if is_correct:
            self.sound_manager.play("correct", self.settings["sfx"])
            # Do NOT award points immediately - wait for other player and penalty shootout
            # Deactivate input box (for Classic mode) or mark as answered (for MCQ mode)
            if player == "p1": 
                self.p1_input.active = False 
            else: 
                self.p2_input.active = False
        else:
            self.sound_manager.play("wrong", self.settings["sfx"])
            # Deactivate input box (for Classic mode) or mark as answered (for MCQ mode)
            if player == "p1": 
                self.p1_input.active = False
            else: 
                self.p2_input.active = False

        # Her iki oyuncu da cevapladıysa kontrol et
        # In MCQ mode, we rely on two_player_q_answered; in Classic mode, we also check input.active
        both_answered = (self.two_player_q_answered["p1"] and self.two_player_q_answered["p2"])
        
        if both_answered:
            # Check for penalty condition: one correct, one incorrect
            p1_correct = self.two_player_q_correct["p1"]
            p2_correct = self.two_player_q_correct["p2"]
            
            # Penalty condition: one is correct, other is incorrect
            if p1_correct is not None and p2_correct is not None:
                if (p1_correct and not p2_correct) or (not p1_correct and p2_correct):
                    # Trigger penalty shootout
                    if p1_correct:
                        self.penalty_goalkeeper = "p1"
                        self.penalty_attacker = "p2"
                    else:
                        self.penalty_goalkeeper = "p2"
                        self.penalty_attacker = "p1"
                    
                    self.penalty_active = True
                    self.set_state("PENALTY_SHOOTOUT")
                    return
            
            # No penalty condition, proceed to next question normally
            self.next_two_player_question()
    def next_two_player_question(self):
        self.current_q_index += 1
        
        if self.current_q_index >= self.two_player_quiz_length:
            self.end_two_player_game()
        else:
            # Geri bildirim göster ve ardından yeni turu başlat
            feedback_msg = f"Cevap: {self.quiz_data[self.current_q_index-1]['a']}"
            self.feedback = {"msg": feedback_msg, "color": COLORS["DARK"], "time": time.time()}
            self.draw()
            pygame.display.flip()
            time.sleep(1.5)
            self.start_two_player_turn()

    def handle_penalty_shootout(self):
        """Handle the penalty shootout mini-game"""
        if not self.penalty_active or not self.penalty_goalkeeper or not self.penalty_attacker:
            return
        
        # Only handle once
        if self.penalty_handled:
            return
        
        self.penalty_handled = True
        
        # PAUSE TIMER: Store current time remaining and when penalty started
        if self.state == "TWO_PLAYER_QUIZ":
            elapsed = time.time() - self.start_time
            self.time_remaining_before_penalty = max(0, self.settings["time_per_question"] - elapsed)
            self.penalty_start_time = time.time()
            print(f"⏸️ Timer paused. Time remaining: {self.time_remaining_before_penalty:.2f}s")
        
        # Show penalty screen briefly
        self.draw()
        pygame.display.flip()
        time.sleep(2.0)  # Show penalty screen for 2 seconds
        
        # Call the penalty shootout game as a separate process
        try:
            # Get player names for display
            goalkeeper_name = "Player 1" if self.penalty_goalkeeper == "p1" else "Player 2"
            attacker_name = "Player 1" if self.penalty_attacker == "p1" else "Player 2"
            
            # Get the absolute path to soccer.py
            # Try multiple methods to get the correct path
            current_dir = os.path.dirname(os.path.abspath(__file__))
            soccer_path = os.path.join(current_dir, "soccer.py")
            
            # Convert to absolute path and normalize
            soccer_path = os.path.abspath(soccer_path)
            
            # Fallback: Use the exact path provided by user if relative path doesn't exist
            if not os.path.exists(soccer_path):
                fallback_path = r"D:\coding\pythonuni\math project (2)\math_final-main\math_final-main\soccer.py"
                if os.path.exists(fallback_path):
                    soccer_path = fallback_path
                    print(f"Using fallback path: {soccer_path}")
                else:
                    raise FileNotFoundError(f"soccer.py not found at: {soccer_path} or {fallback_path}")
            
            # Run soccer.py as a subprocess
            # Exit code 0 = saved (True), exit code 1 = goal scored (False)
            print(f"Running penalty shootout: {soccer_path}")
            print(f"Python executable: {sys.executable}")
            
            # Run the subprocess
            result = subprocess.run(
                [sys.executable, soccer_path], 
                capture_output=False,  # Don't capture, let it display
                cwd=current_dir,
                check=False  # Don't raise exception on non-zero exit
            )
            
            print(f"Penalty shootout finished with exit code: {result.returncode}")
            
            # Get result from exit code: 0 = saved (True), 1 = goal (False)
            keeper_saved = (result.returncode == 0)
            
            # Restore main game screen (soccer.py might have changed display mode)
            try:
                pygame.display.set_mode((WIDTH, HEIGHT))
            except:
                pass  # If screen restoration fails, continue anyway
            
            # Process result
            # Only count score if Player 1 answered correctly AND saved as goalkeeper
            if self.penalty_goalkeeper == "p1" and keeper_saved:
                # Player 1 answered correctly and saved the ball - award points
                self.p1_score += 10
                self.feedback = {
                    "msg": f"{goalkeeper_name} saved! +10 points to Player 1!",
                    "color": COLORS["GREEN"],
                    "time": time.time()
                }
                self.sound_manager.play("correct", self.settings["sfx"])
            else:
                # No points awarded in any other case
                if keeper_saved:
                    self.feedback = {
                        "msg": f"{goalkeeper_name} saved! No points awarded.",
                        "color": COLORS["BLUE"],
                        "time": time.time()
                    }
                else:
                    self.feedback = {
                        "msg": f"{attacker_name} scored! No points awarded.",
                        "color": COLORS["YELLOW"],
                        "time": time.time()
                    }
                self.sound_manager.play("wrong", self.settings["sfx"])
            
            # RESUME TIMER: Adjust start_time to account for paused time
            if self.state == "TWO_PLAYER_QUIZ" and self.penalty_start_time is not None:
                penalty_duration = time.time() - self.penalty_start_time
                # Adjust start_time so that remaining time is preserved
                # New start_time should be: current_time - (original_elapsed_time)
                # But we want remaining time to be the same as before penalty
                if self.time_remaining_before_penalty is not None:
                    # Calculate what start_time should be to preserve remaining time
                    # remaining = time_per_question - (current_time - start_time)
                    # So: start_time = current_time - (time_per_question - remaining)
                    self.start_time = time.time() - (self.settings["time_per_question"] - self.time_remaining_before_penalty)
                    print(f"▶️ Timer resumed. Time remaining: {self.time_remaining_before_penalty:.2f}s (penalty took {penalty_duration:.2f}s)")
                self.penalty_start_time = None
                self.time_remaining_before_penalty = None
            
            # Show result briefly
            self.draw()
            pygame.display.flip()
            time.sleep(2.0)
            
        except Exception as e:
            print(f"Error in penalty shootout: {e}")
            import traceback
            traceback.print_exc()
            
            # RESUME TIMER even on error
            if self.state == "TWO_PLAYER_QUIZ" and self.penalty_start_time is not None:
                penalty_duration = time.time() - self.penalty_start_time
                if self.time_remaining_before_penalty is not None:
                    self.start_time = time.time() - (self.settings["time_per_question"] - self.time_remaining_before_penalty)
                    print(f"▶️ Timer resumed after error. Time remaining: {self.time_remaining_before_penalty:.2f}s")
                self.penalty_start_time = None
                self.time_remaining_before_penalty = None
            
            self.feedback = {
                "msg": "Penalty shootout error. Continuing...",
                "color": COLORS["RED"],
                "time": time.time()
            }
            # Default to goal scored if there's an error
            keeper_saved = False
        
        # Reset penalty state (but keep timer pause info until after next question starts)
        self.penalty_active = False
        self.penalty_goalkeeper = None
        self.penalty_attacker = None
        self.penalty_handled = False
        
        # Return to questions page (TWO_PLAYER_QUIZ state)
        self.set_state("TWO_PLAYER_QUIZ")
        
        # Continue to next question (this will reset the timer with start_two_player_turn)
        self.next_two_player_question()
        
        # Clear timer pause info after next question starts (timer is reset anyway)
        self.penalty_start_time = None
        self.time_remaining_before_penalty = None
    
    def end_two_player_game(self):
        if self.p1_score > self.p2_score:
            self.winner = "Player 1 (Sol)"
        elif self.p2_score > self.p1_score:
            self.winner = "Player 2 (Sağ)"
        else:
            self.winner = "Berabere"
        
        self.set_state("TWO_PLAYER_GAMEOVER")

        # ---------------- ADMIN PANEL MANTIKLARI ----------------
    
    def set_admin_level(self, level):
        """Admin panelinde aktif seviyeyi ayarlar."""
        self.admin_current_level = level
        self.feedback = {"msg": f"Aktif Kayıt Seviyesi: {level.upper()}", "color": COLORS["BLUE"], "time": time.time()}

    def delete_last_question(self):
        """Aktif seviyedeki son soruyu JSON dosyasından siler."""
        all_q_data = DataManager.load_json(FILES["questions"])
        level = self.admin_current_level
        
        if level in all_q_data and all_q_data[level]:
            deleted_q = all_q_data[level].pop() # Son soruyu listeden çıkar
            DataManager.save_json(FILES["questions"], all_q_data)
            
            self.feedback = {"msg": f"'{level.upper()}' seviyesinden son soru ('{deleted_q['q'][:20]}...') SİLİNDİ!", 
                             "color": COLORS["RED"], "time": time.time()}
        else:
            self.feedback = {"msg": f"'{level.upper()}' seviyesinde silinecek soru bulunamadı.", 
                             "color": COLORS["GRAY"], "time": time.time()}

    def save_new_question(self):
        """Admin panelinden alınan yeni soruyu ve cevabı JSON dosyasına güvenli bir şekilde kaydeder."""
        
        # 1. Giriş Verilerini Temizleme ve Kontrol Etme
        question_text = self.admin_question_input.text.strip()
        answer_text = self.admin_answer_input.text.strip()
        
        # Yer tutucu metinleri ve boşluğu kontrol etme
        if question_text in ["Soru metni buraya...", ""] or answer_text in ["Cevap (Kesin Değer)", ""]:
            self.feedback = {"msg": "Soru ve Cevap Alanları BOŞ Bırakılamaz!", "color": COLORS["RED"], "time": time.time()}
            return

        # 2. Yeni Soru Objesi Oluşturma
        new_question = {
            "q": question_text,
            "a": answer_text,
            "kategori": "matematik", 
            "mod": "klasik" 
        }

        # 3. Mevcut Soruları Yükleme ve Güncelleme
        level_to_save = self.admin_current_level 
        
        try:
            all_q_data = DataManager.load_json(FILES["questions"])
            
            if level_to_save in all_q_data:
                # Soru listesine yeni soruyu ekle
                all_q_data[level_to_save].append(new_question)
                
                # JSON dosyasına kaydet
                DataManager.save_json(FILES["questions"], all_q_data)
                
                # 4. Başarılı Geri Bildirim ve Inputları Temizleme
                self.feedback = {"msg": f"Yeni Soru ('{level_to_save.upper()}') BAŞARIYLA Kaydedildi! Toplam Soru: {len(all_q_data[level_to_save])}", 
                                 "color": COLORS["GREEN"], "time": time.time()}
                                 
                # Input kutularını temizle
                self.admin_question_input.text = "Soru metni buraya..." 
                self.admin_answer_input.text = "Cevap (Kesin Değer)"
                self.admin_question_input.color = COLORS["GRAY"]
                self.admin_answer_input.color = COLORS["GRAY"]
            else:
                self.feedback = {"msg": f"Hata: Geçersiz Seviye ('{level_to_save}')!", "color": COLORS["RED"], "time": time.time()}

        except Exception as e:
             # Eğer JSON yükleme/kaydetme sırasında bir hata olursa (örn. dosya izni)
            self.feedback = {"msg": f"Kritik Hata: Dosya İşlemi Başarısız. {e}", "color": COLORS["RED"], "time": time.time()}
            
    # ---------------- DRAWING ----------------

    def draw_bg(self):
        SCREEN.fill(COLORS["DARK"])
        for x in range(0, WIDTH, 60):
            pygame.draw.line(SCREEN, (44, 62, 80), (x, 0), (x, HEIGHT))

    def draw_menu(self):
        self.draw_bg()
        self.bg_effect.update()
        self.bg_effect.draw(SCREEN)
        
        title = FONTS["title"].render("MATEMATİK DEHASI", True, COLORS["BG"])
        SCREEN.blit(title, (self.CX - title.get_width()//2, 100)) 
        
        # Mod durumu (Yukarı taşınan kısım)
        mode_txt = FONTS["large"].render(f"Mevcut Mod: {self.settings['mode']} (Tek Kişilik)", True, COLORS["BLUE"])
        SCREEN.blit(mode_txt, (self.CX - mode_txt.get_width()//2, 260))
        
        for btn in self.buttons["menu"]:
            btn.draw(SCREEN)

        self.gamemodes_button.draw(SCREEN)
        self.mode_toggle_button.draw(SCREEN) 

    def draw_modes_menu(self):
        self.draw_bg()
        self.buttons["back"].draw(SCREEN) 
        
        t = FONTS["title"].render("OYUN MODLARI", True, COLORS["BG"])
        SCREEN.blit(t, (self.CX - t.get_width()//2, 100))
        
        for btn in self.buttons["modes_menu"]:
            btn.draw(SCREEN)
            
    def draw_two_player_setup(self):
        self.draw_bg()
        self.buttons["back_to_modes"].draw(SCREEN) # Mod menüsüne geri dönüş
        
        t = FONTS["title"].render("İKİ KİŞİLİK YARIŞ: ZORLUK SEÇ", True, COLORS["BG"])
        SCREEN.blit(t, (self.CX - t.get_width()//2, 100))
        
        # Mevcut mod bilgisini göster
        mode_display = "Çoktan Seçmeli (MCQ)" if self.two_player_mode == "MCQ" else "Klasik (Yazarak)"
        mode_color = COLORS["PURPLE"] if self.two_player_mode == "MCQ" else COLORS["BLUE"]
        info = FONTS["large"].render(f"Toplam {self.two_player_quiz_length} Soru | Mod: {mode_display}", True, mode_color)
        SCREEN.blit(info, (self.CX - info.get_width()//2, 250))
        
        for btn in self.buttons["two_player_setup"]:
            btn.draw(SCREEN)
        
        # Mod değiştirme butonunu çiz
        self.two_player_mode_toggle_button.draw(SCREEN)

    def draw_quiz(self):
        self.draw_bg()
        # ... (Tek kişilik quiz çizim mantığı) ...
        
        # Üst Panel
        pygame.draw.rect(SCREEN, COLORS["DARK"], (0, 0, WIDTH, 120)) 
        score_txt = FONTS["large"].render(f"Puan: {self.score}", True, COLORS["WHITE"])
        lvl_txt = FONTS["medium"].render(f"{self.current_level.upper()} | {self.current_q_index+1}/{len(self.quiz_data)}", True, COLORS["GRAY"])
        
        SCREEN.blit(lvl_txt, (40, 40))
        SCREEN.blit(score_txt, (WIDTH - 40 - score_txt.get_width(), 30))
        
        # Süre Çubuğu
        elapsed = time.time() - self.start_time
        remaining = max(0, self.settings["time_per_question"] - elapsed)
        bar_width = int((remaining / self.settings["time_per_question"]) * WIDTH)
        bar_color = COLORS["GREEN"] if remaining > 10 else COLORS["RED"]
        pygame.draw.rect(SCREEN, bar_color, (0, 120, bar_width, 20)) 
        
        if remaining <= 0:
            self.show_feedback("Süre Doldu!", COLORS["RED"])
            self.next_question()
            return

        if self.current_q_index < len(self.quiz_data):
            q_item = self.quiz_data[self.current_q_index]
            # Soru Paneli (Merkezlenmiş)
            q_panel_w, q_panel_h = WIDTH - 300, 250
            q_panel_rect = pygame.Rect(150, 200, q_panel_w, q_panel_h)
            pygame.draw.rect(SCREEN, COLORS["WHITE"], q_panel_rect, border_radius=20)
            
            lines = Utils.wrap_text(q_item["q"], FONTS["large"], q_panel_rect.width - 50)
            y_off = q_panel_rect.y + 40
            for line in lines:
                t = FONTS["large"].render(line, True, COLORS["DARK"])
                SCREEN.blit(t, (self.CX - t.get_width()//2, y_off))
                y_off += 70 
            
        if self.settings["mode"] == "MCQ":
            for i, (btn, val) in enumerate(self.mcq_buttons):
                # Joystick ile seçili olan butonu vurgula
                if i == self.mcq_selected_index:
                    btn.is_hovered = True
                    # Seçili butonun etrafına kalın çerçeve çiz
                    pygame.draw.rect(SCREEN, COLORS["YELLOW"], btn.rect.inflate(8, 8), 4, border_radius=18)
                btn.draw(SCREEN)
            
            # Joystick bilgisi göster (eğer joystick bağlıysa)
            if self.joysticks:
                joy_txt = FONTS["small"].render("🎮 Joystick: ↑↓ Seç, A/X Onayla", True, COLORS["GRAY"])
                SCREEN.blit(joy_txt, (self.CX - joy_txt.get_width()//2, HEIGHT * 0.92))
        else:
            self.input_box.draw(SCREEN)
            help_txt = "Cevabı yaz ve ENTER'a bas" if self.input_box.active else "Kutuya tıkla ve cevabı yaz"
            lbl = FONTS["medium"].render(help_txt, True, COLORS["GRAY"])
            SCREEN.blit(lbl, (self.input_box.rect.x, self.input_box.rect.bottom + 15))
        
        # Power-up Bilgisi (EN ALTTA, Merkeze hizalı)
        pu_txt = f"[F1] Süre ({self.powerups['extra']})    [F2] Geç ({self.powerups['skip']})    [F3] İpucu ({self.powerups['hint']})"
        pu_surf = FONTS["medium"].render(pu_txt, True, COLORS["BG"])
        SCREEN.blit(pu_surf, (self.CX - pu_surf.get_width()//2, HEIGHT - 50)) 
            
        if time.time() - self.feedback["time"] < 1.5:
            fb_w, fb_h = 700, 100
            fb = FONTS["large"].render(self.feedback["msg"], True, self.feedback["color"])
            pygame.draw.rect(SCREEN, (255,255,255), (self.CX - fb_w//2, self.CY + 150, fb_w, fb_h), border_radius=15)
            SCREEN.blit(fb, (self.CX - fb.get_width()//2, self.CY + 150 + (fb_h - fb.get_height())//2))
            
    def draw_two_player_quiz(self):
        self.draw_bg()
        
        # EKRAN ORTASI AYIRICI ÇİZGİ
        pygame.draw.line(SCREEN, COLORS["BG"], (self.CX, 0), (self.CX, HEIGHT), 5)
        
        # ORTAK SORU PANELİ
        q_panel_w, q_panel_h = WIDTH - 300, 150
        q_panel_rect = pygame.Rect(150, 100, q_panel_w, q_panel_h)
        pygame.draw.rect(SCREEN, COLORS["WHITE"], q_panel_rect, border_radius=20)
        pygame.draw.rect(SCREEN, COLORS["DARK"], q_panel_rect, 4, border_radius=20)
        
        # Soru Metni
        q_item = self.quiz_data[self.current_q_index]
        q_num_txt = FONTS["medium"].render(f"Soru {self.current_q_index + 1}/{self.two_player_quiz_length}", True, COLORS["GRAY"])
        SCREEN.blit(q_num_txt, (q_panel_rect.x + 20, q_panel_rect.y + 15))
        
        # Soru metni ortalama
        lines = Utils.wrap_text(q_item["q"], FONTS["quiz_large"], q_panel_rect.width - 50)
        y_off = q_panel_rect.y + 45
        for line in lines:
            t = FONTS["quiz_large"].render(line, True, COLORS["DARK"])
            SCREEN.blit(t, (self.CX - t.get_width()//2, y_off))
            y_off += 70 
            
        # ---------------- OYUNCU PANELLERİ ----------------
        
        # Oyuncu 1 (Sol)
        p1_lbl = FONTS["title"].render(f"P1 - SOL | {self.p1_score}", True, COLORS["P1"])
        SCREEN.blit(p1_lbl, (self.CX // 2 - p1_lbl.get_width() // 2, HEIGHT * 0.35))
        self.p1_input.draw(SCREEN)
        
        # Oyuncu 2 (Sağ)
        p2_lbl = FONTS["title"].render(f"P2 - SAĞ | {self.p2_score}", True, COLORS["P2"])
        SCREEN.blit(p2_lbl, (self.CX + self.CX // 2 - p2_lbl.get_width() // 2, HEIGHT * 0.35))
        self.p2_input.draw(SCREEN)

        # ---------------- ZAMANLAYICI VE GERİ BİLDİRİM ----------------

        # Kalan Süre (İki oyuncu için ortak)
        elapsed = time.time() - self.start_time
        remaining = max(0, self.settings["time_per_question"] - elapsed)
        
        time_text = FONTS["title"].render(f"{int(remaining)}s", True, COLORS["DARK"])
        time_x = self.CX - time_text.get_width()//2
        time_y = HEIGHT * 0.55
        
        # Zamanlayıcının etrafına renkli halka
        time_color = COLORS["RED"] if remaining < 5 else COLORS["YELLOW"] if remaining < 10 else COLORS["GREEN"]
        pygame.draw.circle(SCREEN, time_color, (time_x + time_text.get_width()//2, time_y + time_text.get_height()//2), 60, 0)
        pygame.draw.circle(SCREEN, COLORS["BG"], (time_x + time_text.get_width()//2, time_y + time_text.get_height()//2), 60, 4)
        
        SCREEN.blit(time_text, (time_x, time_y))

        if remaining <= 0:
            # Süre dolduğunda oyunu ilerletme
            self.feedback = {"msg": "Süre Doldu!", "color": COLORS["RED"], "time": time.time()}
            self.next_two_player_question()
            return
            
        # Geri Bildirim Gösterme (Eğer bir oyuncu cevap verdiyse)
        if time.time() - self.feedback["time"] < 1.5:
            fb_w, fb_h = 700, 100
            fb = FONTS["large"].render(self.feedback["msg"], True, self.feedback["color"])
            
            # Geri bildirimi alta, input kutularının üstüne ortalama
            fb_rect = pygame.Rect(self.CX - fb_w//2, HEIGHT * 0.85, fb_w, fb_h)
            pygame.draw.rect(SCREEN, COLORS["WHITE"], fb_rect, border_radius=15)
            pygame.draw.rect(SCREEN, self.feedback["color"], fb_rect, 4, border_radius=15)
            
            # Metni ortala
            SCREEN.blit(fb, (self.CX - fb.get_width()//2, fb_rect.y + (fb_h - fb.get_height())//2))
        
        # EKRAN ORTASI AYIRICI ÇİZGİ
        pygame.draw.line(SCREEN, COLORS["BG"], (self.CX, 0), (self.CX, HEIGHT), 5)
        
        # ORTAK SORU PANELİ
        q_panel_w, q_panel_h = WIDTH - 300, 150
        q_panel_rect = pygame.Rect(150, 100, q_panel_w, q_panel_h)
        pygame.draw.rect(SCREEN, COLORS["WHITE"], q_panel_rect, border_radius=20)
        pygame.draw.rect(SCREEN, COLORS["BG"], q_panel_rect, 4, border_radius=20)
        
        # Soru Metni
        q_item = self.quiz_data[self.current_q_index]
        q_num_txt = FONTS["medium"].render(f"Soru {self.current_q_index + 1}/{self.two_player_quiz_length}", True, COLORS["GRAY"])
        SCREEN.blit(q_num_txt, (q_panel_rect.x + 20, q_panel_rect.y + 15))
        
        lines = Utils.wrap_text(q_item["q"], FONTS["quiz_large"], q_panel_rect.width - 50)
        t = FONTS["quiz_large"].render(lines[0], True, COLORS["DARK"])
        SCREEN.blit(t, (self.CX - t.get_width()//2, q_panel_rect.y + 50))
        
        # SKOR TABLOSU (Sol ve Sağda)
        p1_score_txt = FONTS["title"].render(f"{self.p1_score}", True, COLORS["P1"])
        p2_score_txt = FONTS["title"].render(f"{self.p2_score}", True, COLORS["P2"])
        
        SCREEN.blit(p1_score_txt, (WIDTH * 0.25 - p1_score_txt.get_width()//2, 300))
        SCREEN.blit(p2_score_txt, (WIDTH * 0.75 - p2_score_txt.get_width()//2, 300))
        
        p1_lbl = FONTS["large"].render("PLAYER 1 (ENTER)", True, COLORS["P1"])
        p2_lbl = FONTS["large"].render("PLAYER 2 (KP Enter)", True, COLORS["P2"])
        
        SCREEN.blit(p1_lbl, (WIDTH * 0.25 - p1_lbl.get_width()//2, 450))
        SCREEN.blit(p2_lbl, (WIDTH * 0.75 - p2_lbl.get_width()//2, 450))
        
        # Input Kutuları
        self.p1_input.draw(SCREEN)
        self.p2_input.draw(SCREEN)

        # Durum/Geri Bildirim
        if time.time() - self.feedback["time"] < 1.5:
            fb = FONTS["large"].render(self.feedback["msg"], True, self.feedback["color"])
            fb_rect = fb.get_rect(center=(self.CX, HEIGHT - 100))
            SCREEN.blit(fb, fb_rect)
            
    def draw_two_player_quiz(self):
        self.draw_bg()
        
        # EKRAN ORTASI AYIRICI ÇİZGİ
        pygame.draw.line(SCREEN, COLORS["BG"], (self.CX, 0), (self.CX, HEIGHT), 5)
        
        # ORTAK SORU PANELİ
        q_panel_w, q_panel_h = WIDTH - 300, 150
        q_panel_rect = pygame.Rect(150, 100, q_panel_w, q_panel_h)
        pygame.draw.rect(SCREEN, COLORS["WHITE"], q_panel_rect, border_radius=20)
        pygame.draw.rect(SCREEN, COLORS["BG"], q_panel_rect, 4, border_radius=20)
        
        # Soru Metni
        q_item = self.quiz_data[self.current_q_index]
        mode_txt = "MCQ" if self.two_player_mode == "MCQ" else "Klasik"
        q_num_txt = FONTS["medium"].render(f"Soru {self.current_q_index + 1}/{self.two_player_quiz_length} | Zorluk: {self.current_level.upper()} | Mod: {mode_txt}", True, COLORS["GRAY"])
        SCREEN.blit(q_num_txt, (q_panel_rect.x + 20, q_panel_rect.y + 15))
        
        # Soru metni ortalama
        lines = Utils.wrap_text(q_item["q"], FONTS["quiz_large"], q_panel_rect.width - 50)
        y_off = q_panel_rect.y + 45
        for line in lines:
            t = FONTS["quiz_large"].render(line, True, COLORS["DARK"])
            SCREEN.blit(t, (self.CX - t.get_width()//2, y_off))
            y_off += 70 
            
        # ---------------- OYUNCU PANELLERİ ----------------
        
        # Oyuncu 1 (Sol)
        p1_title = FONTS["large"].render("OYUNCU 1 (SOL)", True, COLORS["P1"])
        p1_score_lbl = FONTS["title"].render(f"Puan: {self.p1_score}", True, COLORS["BG"])
        
        # Başlık ve Puanı Ortala
        SCREEN.blit(p1_title, (self.CX // 2 - p1_title.get_width() // 2, HEIGHT * 0.26))
        SCREEN.blit(p1_score_lbl, (self.CX // 2 - p1_score_lbl.get_width() // 2, HEIGHT * 0.32))
        
        # Oyuncu 2 (Sağ)
        p2_title = FONTS["large"].render("OYUNCU 2 (SAĞ)", True, COLORS["P2"])
        p2_score_lbl = FONTS["title"].render(f"Puan: {self.p2_score}", True, COLORS["BG"])
        
        # Başlık ve Puanı Ortala
        SCREEN.blit(p2_title, (self.CX + self.CX // 2 - p2_title.get_width() // 2, HEIGHT * 0.26))
        SCREEN.blit(p2_score_lbl, (self.CX + self.CX // 2 - p2_score_lbl.get_width() // 2, HEIGHT * 0.32))
        
        # MCQ veya Classic moduna göre çiz
        if self.two_player_mode == "MCQ":
            # P1 MCQ butonlarını çiz (joystick seçimi vurgulu)
            for i, (btn, val) in enumerate(self.p1_mcq_buttons):
                if i == self.p1_mcq_selected_index and not self.two_player_q_answered["p1"]:
                    btn.is_hovered = True
                    pygame.draw.rect(SCREEN, COLORS["YELLOW"], btn.rect.inflate(6, 6), 3, border_radius=18)
                btn.draw(SCREEN)
            
            # P2 MCQ butonlarını çiz (joystick seçimi vurgulu)
            for i, (btn, val) in enumerate(self.p2_mcq_buttons):
                if i == self.p2_mcq_selected_index and not self.two_player_q_answered["p2"]:
                    btn.is_hovered = True
                    pygame.draw.rect(SCREEN, COLORS["YELLOW"], btn.rect.inflate(6, 6), 3, border_radius=18)
                btn.draw(SCREEN)
            
            # Joystick bilgisi göster (eğer joystick bağlıysa)
            if self.joysticks:
                joy_info = FONTS["small"].render("🎮 Joy1: P1 | Joy2: P2 | ↑↓ Seç, A/X Onayla", True, COLORS["GRAY"])
                SCREEN.blit(joy_info, (self.CX - joy_info.get_width()//2, HEIGHT * 0.92))
        else:
            # Classic mod - Input kutuları
            p1_inst = FONTS["small"].render("Cevapla ve ENTER'a bas", True, COLORS["GRAY"])
            SCREEN.blit(p1_inst, (self.p1_input.rect.x, self.p1_input.rect.bottom + 10))
            self.p1_input.draw(SCREEN)
            
            p2_inst = FONTS["small"].render("Cevapla ve NUMPAD ENTER'a bas", True, COLORS["GRAY"])
            SCREEN.blit(p2_inst, (self.p2_input.rect.x, self.p2_input.rect.bottom + 10))
            self.p2_input.draw(SCREEN)


        # ---------------- ZAMANLAYICI VE GERİ BİLDİRİM ----------------

        # Don't count down timer if penalty is active
        if self.penalty_active and self.penalty_start_time is not None:
            # Use stored remaining time (timer is paused)
            remaining = self.time_remaining_before_penalty if self.time_remaining_before_penalty is not None else 0
        else:
            elapsed = time.time() - self.start_time
            remaining = max(0, self.settings["time_per_question"] - elapsed)
        
        time_text = FONTS["title"].render(f"{int(remaining)}s", True, COLORS["WHITE"])
        time_x = self.CX - 60
        time_y = HEIGHT * 0.70
        
        # Zamanlayıcının etrafına renkli halka
        time_color = COLORS["RED"] if remaining < 5 else COLORS["YELLOW"] if remaining < 10 else COLORS["GREEN"]
        pygame.draw.circle(SCREEN, time_color, (self.CX, time_y + time_text.get_height()//2), 65, 0)
        pygame.draw.circle(SCREEN, COLORS["BG"], (self.CX, time_y + time_text.get_height()//2), 65, 4)
        
        SCREEN.blit(time_text, (time_x, time_y))

        # Only check timer expiration if penalty is not active
        # This prevents crash when timer reaches 0 during penalty shootout
        if remaining <= 0 and not (self.penalty_active and self.penalty_start_time is not None):
            self.feedback = {"msg": "Süre Doldu!", "color": COLORS["RED"], "time": time.time()}
            self.next_two_player_question()
            return
            
        # Geri Bildirim Gösterme
        if time.time() - self.feedback["time"] < 1.5:
            fb_w, fb_h = 700, 100
            fb = FONTS["large"].render(self.feedback["msg"], True, self.feedback["color"])
            
            fb_rect = pygame.Rect(self.CX - fb_w//2, HEIGHT * 0.85 + 30, fb_w, fb_h)
            pygame.draw.rect(SCREEN, COLORS["WHITE"], fb_rect, border_radius=15)
            pygame.draw.rect(SCREEN, self.feedback["color"], fb_rect, 4, border_radius=15)
            
            SCREEN.blit(fb, (self.CX - fb.get_width()//2, fb_rect.y + (fb_h - fb.get_height())//2))


    def draw_gameover(self):
        # ... (Tek kişilik gameover çizim mantığı) ...
        self.draw_bg()
        panel_w, panel_h = 800, 600
        panel = pygame.Rect(self.CX - panel_w//2, self.CY - panel_h//2, panel_w, panel_h)
        pygame.draw.rect(SCREEN, COLORS["WHITE"], panel, border_radius=30)
        pygame.draw.rect(SCREEN, COLORS["DARK"], panel, 6, border_radius=30)
        
        t1 = FONTS["title"].render("Oyun Bitti!", True, COLORS["DARK"])
        t2 = FONTS["large"].render(f"Toplam Puan: {self.score}", True, COLORS["BLUE"])
        t3 = FONTS["medium"].render("Menüye dönmek için herhangi bir yere tıkla", True, COLORS["GRAY"])
        
        SCREEN.blit(t1, (self.CX - t1.get_width()//2, panel.y + 80))
        SCREEN.blit(t2, (self.CX - t2.get_width()//2, panel.y + 250))
        SCREEN.blit(t3, (self.CX - t3.get_width()//2, panel.y + 450))

    def draw_penalty_shootout(self):
        """Draw the penalty shootout activation screen"""
        self.draw_bg()
        self.bg_effect.update()
        self.bg_effect.draw(SCREEN)
        
        # Main panel
        panel_w, panel_h = 1000, 600
        panel = pygame.Rect(self.CX - panel_w//2, self.CY - panel_h//2, panel_w, panel_h)
        pygame.draw.rect(SCREEN, COLORS["WHITE"], panel, border_radius=30)
        pygame.draw.rect(SCREEN, COLORS["YELLOW"], panel, 8, border_radius=30)
        
        # Title
        title = FONTS["title"].render("PENALTY SHOOTOUT!", True, COLORS["YELLOW"])
        SCREEN.blit(title, (self.CX - title.get_width()//2, panel.y + 50))
        
        # Role assignment
        if self.penalty_goalkeeper and self.penalty_attacker:
            goalkeeper_name = "Player 1 (SOL)" if self.penalty_goalkeeper == "p1" else "Player 2 (SAĞ)"
            attacker_name = "Player 1 (SOL)" if self.penalty_attacker == "p1" else "Player 2 (SAĞ)"
            
            goalkeeper_color = COLORS["P1"] if self.penalty_goalkeeper == "p1" else COLORS["P2"]
            attacker_color = COLORS["P1"] if self.penalty_attacker == "p1" else COLORS["P2"]
            
            # Goalkeeper info
            gk_label = FONTS["large"].render("GOALKEEPER:", True, COLORS["DARK"])
            SCREEN.blit(gk_label, (self.CX - gk_label.get_width()//2, panel.y + 180))
            
            gk_name = FONTS["title"].render(goalkeeper_name, True, goalkeeper_color)
            SCREEN.blit(gk_name, (self.CX - gk_name.get_width()//2, panel.y + 240))
            
            # Attacker info
            att_label = FONTS["large"].render("PENALTY TAKER:", True, COLORS["DARK"])
            SCREEN.blit(att_label, (self.CX - att_label.get_width()//2, panel.y + 340))
            
            att_name = FONTS["title"].render(attacker_name, True, attacker_color)
            SCREEN.blit(att_name, (self.CX - att_name.get_width()//2, panel.y + 400))
        
        # Instructions
        inst1 = FONTS["medium"].render("Starting penalty shootout...", True, COLORS["GRAY"])
        SCREEN.blit(inst1, (self.CX - inst1.get_width()//2, panel.y + 520))
    
    def draw_two_player_gameover(self):
        # İki kişilik mod oyun sonu ekranı
        self.draw_bg()
        panel_w, panel_h = 900, 650
        panel = pygame.Rect(self.CX - panel_w//2, self.CY - panel_h//2, panel_w, panel_h)
        pygame.draw.rect(SCREEN, COLORS["WHITE"], panel, border_radius=30)
        pygame.draw.rect(SCREEN, COLORS["DARK"], panel, 6, border_radius=30)
        
        t1 = FONTS["title"].render("OYUN BİTTİ!", True, COLORS["DARK"])
        SCREEN.blit(t1, (self.CX - t1.get_width()//2, panel.y + 50))
        
        # Kazanan
        if self.winner == "Berabere":
            winner_txt = FONTS["large"].render("BERABERE!", True, COLORS["YELLOW"])
        else:
            winner_color = COLORS["P1"] if "Player 1" in self.winner else COLORS["P2"]
            winner_txt = FONTS["large"].render(f"KAZANAN: {self.winner}", True, winner_color)
        SCREEN.blit(winner_txt, (self.CX - winner_txt.get_width()//2, panel.y + 180))
        
        # Skorlar
        p1_score_txt = FONTS["large"].render(f"Oyuncu 1: {self.p1_score} Puan", True, COLORS["P1"])
        p2_score_txt = FONTS["large"].render(f"Oyuncu 2: {self.p2_score} Puan", True, COLORS["P2"])
        SCREEN.blit(p1_score_txt, (self.CX - p1_score_txt.get_width()//2, panel.y + 300))
        SCREEN.blit(p2_score_txt, (self.CX - p2_score_txt.get_width()//2, panel.y + 380))
        
        t3 = FONTS["medium"].render("Menüye dönmek için herhangi bir yere tıkla", True, COLORS["GRAY"])
        SCREEN.blit(t3, (self.CX - t3.get_width()//2, panel.y + 520))

    def draw_highscores(self):
        # ... (Yüksek skorlar çizim mantığı) ...
        self.draw_bg()
        self.buttons["back"].draw(SCREEN)
        
        t = FONTS["title"].render("SKORLAR", True, COLORS["BG"])
        SCREEN.blit(t, (self.CX - t.get_width()//2, 100))
        
        y = 250
        card_w, card_h = 600, 100
        for lvl, scr in self.highscores.items():
            card = pygame.Rect(self.CX - card_w//2, y, card_w, card_h)
            pygame.draw.rect(SCREEN, COLORS["WHITE"], card, border_radius=15)
            
            lt = FONTS["large"].render(lvl.upper(), True, COLORS["BLUE"])
            st = FONTS["large"].render(str(scr), True, COLORS["GREEN"])
            SCREEN.blit(lt, (card.x + 40, card.y + 20))
            SCREEN.blit(st, (card.right - 40 - st.get_width(), card.y + 20))
            y += 130 

    def draw_settings(self):
        # ... (Ayarlar çizim mantığı) ...
        self.draw_bg()
        self.buttons["back"].draw(SCREEN)
        
        t = FONTS["title"].render("AYARLAR", True, COLORS["BG"])
        SCREEN.blit(t, (self.CX - t.get_width()//2, 100))
        
        info_lines = [
            f"Müzik: {'AÇIK' if self.settings['music'] else 'KAPALI'} (M)",
            f"Ses Efektleri: {'AÇIK' if self.settings['sfx'] else 'KAPALI'} (S)",
            f"Tam Ekran: {'AÇIK' if self.settings['fullscreen'] else 'KAPALI'} (F)"
        ]
        y = 300
        for line in info_lines:
            surface = FONTS["large"].render(line, True, COLORS["TEXT"])
            SCREEN.blit(surface, (self.CX - surface.get_width()//2, y))
            y += 100 
            
    def draw_admin(self):
        # ... (Admin çizim mantığı) ...
        self.draw_bg()
        self.buttons["back"].draw(SCREEN)
        
        t = FONTS["title"].render("ADMIN PANELİ: SORU YÖNETİMİ", True, COLORS["BG"])
        SCREEN.blit(t, (self.CX - t.get_width()//2, 100))
        
        current_lvl_text = FONTS["large"].render(f"Yönetilen Seviye: {self.admin_current_level.upper()}", True, COLORS["BLUE"])
        SCREEN.blit(current_lvl_text, (self.CX - current_lvl_text.get_width()//2, HEIGHT * 0.35))
        
        for key, btn in self.admin_buttons.items():
            if "level" in key:
                if self.admin_current_level in key:
                    btn.color = COLORS["PURPLE"]
                    btn.hover_color = COLORS["PURPLE_HOVER"]
                else:
                    btn.color = COLORS["GRAY"]
                    btn.hover_color = COLORS["BLUE"]
                btn.draw(SCREEN)
                
        self.admin_question_input.draw(SCREEN)
        self.admin_answer_input.draw(SCREEN)
        self.admin_buttons["save"].draw(SCREEN)
        self.admin_buttons["delete_last"].draw(SCREEN)
        
        if time.time() - self.feedback["time"] < 2.0:
            fb = FONTS["large"].render(self.feedback["msg"], True, self.feedback["color"])
            SCREEN.blit(fb, (self.CX - fb.get_width()//2, HEIGHT * 0.95 - fb.get_height()))

    def draw(self):
        if self.state == "MENU": self.draw_menu()
        elif self.state == "MODES_MENU": self.draw_modes_menu()
        elif self.state == "TWO_PLAYER_SETUP": self.draw_two_player_setup()
        elif self.state == "TWO_PLAYER_QUIZ": self.draw_two_player_quiz()
        elif self.state == "TWO_PLAYER_GAMEOVER": self.draw_two_player_gameover()
        elif self.state == "PENALTY_SHOOTOUT": self.draw_penalty_shootout()
        elif self.state == "QUIZ": self.draw_quiz()
        elif self.state == "GAMEOVER": self.draw_gameover()
        elif self.state == "HIGHSCORE": self.draw_highscores()
        elif self.state == "SETTINGS": self.draw_settings()
        elif self.state == "ADMIN": self.draw_admin()


    # ---------------- MAIN LOOP ----------------

    def run(self):
        while True:
            mouse_pos = pygame.mouse.get_pos()
            mouse_click = False
            
            # Joystick cooldown güncelle
            if self.joystick_cooldown > 0:
                self.joystick_cooldown -= 1

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                
                # --- JOYSTICK BAĞLANTI/ÇIKMA ---
                if event.type == pygame.JOYDEVICEADDED:
                    self.init_joysticks()
                if event.type == pygame.JOYDEVICEREMOVED:
                    self.init_joysticks()
                
                # --- JOYSTICK HAT (D-PAD) HAREKETİ ---
                if event.type == pygame.JOYHATMOTION:
                    joy_id = event.joy
                    hat_x, hat_y = event.value
                    if self.joystick_cooldown == 0:
                        if hat_y == 1:  # Yukarı
                            self.handle_joystick_mcq_navigation(joy_id, "up")
                            self.joystick_cooldown = 10
                        elif hat_y == -1:  # Aşağı
                            self.handle_joystick_mcq_navigation(joy_id, "down")
                            self.joystick_cooldown = 10
                
                # --- JOYSTICK AXIS HAREKETİ (Analog çubuk) ---
                if event.type == pygame.JOYAXISMOTION:
                    joy_id = event.joy
                    # Y ekseni (axis 1) - yukarı/aşağı
                    if event.axis == 1 and self.joystick_cooldown == 0:
                        if event.value < -0.5:  # Yukarı
                            self.handle_joystick_mcq_navigation(joy_id, "up")
                            self.joystick_cooldown = 15
                        elif event.value > 0.5:  # Aşağı
                            self.handle_joystick_mcq_navigation(joy_id, "down")
                            self.joystick_cooldown = 15
                
                # --- JOYSTICK BUTON BASMA ---
                if event.type == pygame.JOYBUTTONDOWN:
                    joy_id = event.joy
                    button_id = event.button
                    
                    # Expanded button support: 0 (A/Cross), 1 (B/Circle), 2 (X/Square), 3 (Y/Triangle)
                    # Also support common button numbers that work on most controllers
                    if button_id in [0, 1, 2, 3, 4, 5, 6, 7]:
                        self.handle_joystick_button_press(joy_id, button_id)
                
                # --- TEK KİŞİLİK QUIZ INPUT ---
                if self.state == "QUIZ" and self.settings["mode"] == "Classic":
                    ans = self.input_box.handle_event(event)
                    if ans: self.check_answer(ans)
                
                # --- İKİ KİŞİLİK QUIZ INPUT (Sadece Classic modda) ---
                if self.state == "TWO_PLAYER_QUIZ" and self.two_player_mode == "Classic":
                    # Handle mouse clicks for both inputs
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.p1_input.rect.collidepoint(event.pos):
                            self.p1_input.active = True
                            self.p1_input.color = COLORS["BLUE"]
                            self.p2_input.active = False
                            self.p2_input.color = self.p2_input.base_color
                        elif self.p2_input.rect.collidepoint(event.pos):
                            self.p2_input.active = True
                            self.p2_input.color = COLORS["BLUE"]
                            self.p1_input.active = False
                            self.p1_input.color = self.p1_input.base_color
                    
                    # P1 (ENTER) - check if input is active and not already answered
                    # Skip mouse handling since we handle it above
                    # Only process keyboard events for the active input to avoid double processing
                    if event.type == pygame.KEYDOWN:
                        if self.p1_input.active and not self.two_player_q_answered["p1"]:
                            p1_ans = self.p1_input.handle_event(event, submit_key=pygame.K_RETURN, skip_mouse=True)
                            if p1_ans: 
                                self.check_two_player_answer("p1", p1_ans)
                        elif self.p2_input.active and not self.two_player_q_answered["p2"]:
                            # Only process P2 if P1 is not active (to avoid double processing)
                            p2_ans = self.p2_input.handle_event(event, submit_key=pygame.K_KP_ENTER, skip_mouse=True)
                            if p2_ans: 
                                self.check_two_player_answer("p2", p2_ans)
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        # Mouse events are already handled above, so skip
                        pass
                    else:
                        # For other events, process normally
                        if self.p1_input.active and not self.two_player_q_answered["p1"]:
                            self.p1_input.handle_event(event, submit_key=pygame.K_RETURN, skip_mouse=True)
                        if self.p2_input.active and not self.two_player_q_answered["p2"]:
                            self.p2_input.handle_event(event, submit_key=pygame.K_KP_ENTER, skip_mouse=True)

                # --- ADMIN/DİĞER INPUTLAR ---
                if self.state == "ADMIN":
                    self.admin_question_input.handle_event(event)
                    self.admin_answer_input.handle_event(event)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_click = True
                    
                    if self.state == "MENU":
                        for btn in self.buttons["menu"]:
                            btn.update(mouse_pos, True)
                        self.mode_toggle_button.update(mouse_pos, True)
                        self.gamemodes_button.update(mouse_pos, True)

                    if self.state == "MODES_MENU":
                        for btn in self.buttons["modes_menu"]:
                            btn.update(mouse_pos, True)
                        self.buttons["back"].update(mouse_pos, True)

                    if self.state == "TWO_PLAYER_SETUP":
                        for btn in self.buttons["two_player_setup"]:
                            btn.update(mouse_pos, True)
                        self.buttons["back_to_modes"].update(mouse_pos, True)
                        self.two_player_mode_toggle_button.update(mouse_pos, True)
                        
                    if self.state in ["HIGHSCORE", "SETTINGS", "ADMIN"]:
                         self.buttons["back"].update(mouse_pos, True)
                         
                    if self.state == "ADMIN":
                        for btn in self.admin_buttons.values():
                            btn.update(mouse_pos, True)

                    if self.state == "GAMEOVER":
                        if pygame.Rect(self.CX - 400, self.CY - 300, 800, 600).collidepoint(mouse_pos) or mouse_click:
                             self.set_state("MENU")

                    if self.state == "TWO_PLAYER_GAMEOVER":
                        if pygame.Rect(self.CX - 400, self.CY - 300, 800, 600).collidepoint(mouse_pos) or mouse_click:
                             self.set_state("MENU")

                    if self.state == "QUIZ" and self.settings["mode"] == "MCQ":
                        for btn, val in self.mcq_buttons:
                            if btn.update(mouse_pos, True):
                                self.check_answer(val)

                    # İki kişilik MCQ mod buton tıklamaları
                    if self.state == "TWO_PLAYER_QUIZ" and self.two_player_mode == "MCQ":
                        for btn, val in self.p1_mcq_buttons:
                            if btn.update(mouse_pos, True):
                                self.check_two_player_answer("p1", val)
                        for btn, val in self.p2_mcq_buttons:
                            if btn.update(mouse_pos, True):
                                self.check_two_player_answer("p2", val)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == "MENU": sys.exit()
                        elif self.state == "MODES_MENU": self.set_state("MENU")
                        elif self.state == "TWO_PLAYER_SETUP": self.set_state("MODES_MENU")
                        elif self.state in ["HIGHSCORE", "SETTINGS", "ADMIN", "GAMEOVER", "TWO_PLAYER_GAMEOVER"]: self.set_state("MENU")
                        elif self.state == "QUIZ": self.set_state("MENU") # Quiz'den çıkış
                        elif self.state == "TWO_PLAYER_QUIZ": self.set_state("MENU") # İki kişilik quiz'den çıkış
                    
                    # ... (Tek kişilik F1, F2, F3 tuş mantığı) ...
                    if self.state == "QUIZ":
                        is_typing = (self.settings["mode"] == "Classic" and self.input_box.active)
                        if event.key == pygame.K_F1 or (event.key == pygame.K_1 and not is_typing): 
                            self.use_powerup("extra")
                        if event.key == pygame.K_F2 or (event.key == pygame.K_2 and not is_typing): 
                            self.use_powerup("skip")
                        if event.key == pygame.K_F3 or (event.key == pygame.K_3 and not is_typing): 
                            self.use_powerup("hint")

                    if self.state == "SETTINGS":
                        if event.key == pygame.K_m: self.settings["music"] = not self.settings["music"]
                        if event.key == pygame.K_s: self.settings["sfx"] = not self.settings["sfx"]
                        if event.key == pygame.K_f:
                            self.settings["fullscreen"] = not self.settings["fullscreen"]
                            pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN if self.settings["fullscreen"] else 0)

            # Buton Hover Güncellemeleri
            if self.state == "MENU":
                for btn in self.buttons["menu"]:
                    btn.update(mouse_pos, False)
                self.mode_toggle_button.update(mouse_pos, False) 
                self.gamemodes_button.update(mouse_pos, False) 
            
            elif self.state == "MODES_MENU":
                 for btn in self.buttons["modes_menu"]:
                    btn.update(mouse_pos, False)
                 self.buttons["back"].update(mouse_pos, False)
            
            elif self.state == "TWO_PLAYER_SETUP":
                 for btn in self.buttons["two_player_setup"]:
                    btn.update(mouse_pos, False)
                 self.buttons["back_to_modes"].update(mouse_pos, False)
                 self.two_player_mode_toggle_button.update(mouse_pos, False)
            
            elif self.state == "ADMIN":
                for btn in self.admin_buttons.values():
                    btn.update(mouse_pos, False)

            elif self.state == "QUIZ":
                 if self.settings["mode"] == "MCQ":
                     for btn, val in self.mcq_buttons:
                         btn.update(mouse_pos, False)
            
            elif self.state == "TWO_PLAYER_QUIZ":
                 if self.two_player_mode == "MCQ":
                     for btn, val in self.p1_mcq_buttons:
                         btn.update(mouse_pos, False)
                     for btn, val in self.p2_mcq_buttons:
                         btn.update(mouse_pos, False)
            
            # Handle penalty shootout if active
            if self.state == "PENALTY_SHOOTOUT" and self.penalty_active:
                self.handle_penalty_shootout()
            
            self.draw()
            pygame.display.flip()
            CLOCK.tick(60)

if __name__ == "__main__":
    game = Game()
    game.run()
