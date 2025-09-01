import webbrowser
import threading
import pystray
from PIL import Image, ImageDraw
import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
import socket
from flask import Flask, request

class ModernButton(tk.Canvas):
    def __init__(self, parent, text, command=None, bg="#1DB954", fg="white", 
                 active_bg="#1ed760", active_fg="white", width=140, height=45, 
                 corner_radius=12, font=("Segoe UI", 11, "bold"), icon=None):
        try:
            parent_bg = parent.cget("bg")
        except:
            try:
                parent_bg = parent.cget("background")
            except:
                parent_bg = "#0F0F0F"
        
        super().__init__(parent, width=width, height=height, bg=parent_bg, 
                        highlightthickness=0, relief="flat")
        
        self.command = command
        self.bg = bg
        self.fg = fg
        self.active_bg = active_bg
        self.active_fg = active_fg
        self.corner_radius = corner_radius
        self.font = font
        self.state = "normal"
        self.text = text
        self.icon = icon
        
        self.draw_button()
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
    def draw_button(self):
        self.delete("all")
        bg_color = self.active_bg if self.state == "active" else self.bg
        fg_color = self.active_fg if self.state == "active" else self.fg
        
        # Bouton principal
        self.create_rounded_rectangle(0, 0, self.winfo_reqwidth(), self.winfo_reqheight(), 
                                    self.corner_radius, fill=bg_color, outline="")
        
        # Effet de brillance
        highlight_height = int(self.winfo_reqheight() * 0.4)
        self.create_rounded_rectangle(2, 2, self.winfo_reqwidth()-2, highlight_height, 
                                    self.corner_radius-2, fill="", outline="", 
                                    stipple="gray50")
        
        # Texte avec icône si présente
        if self.icon:
            # Calculer la largeur totale du texte et de l'icône
            icon_width = 20  # Largeur approximative de l'icône
            text_width = len(self.text) * 7  # Largeur approximative du texte
            
            # Positionner l'icône à gauche et le texte à droite
            total_width = icon_width + text_width + 10  # 10px d'espacement
            start_x = (self.winfo_reqwidth() - total_width) // 2
            
            icon_x = start_x + icon_width // 2
            text_x = start_x + icon_width + 10 + text_width // 2
            
            self.create_text(icon_x, self.winfo_reqheight()//2, 
                           text=self.icon, fill=fg_color, font=("Segoe UI", 16))
            self.create_text(text_x, self.winfo_reqheight()//2, 
                           text=self.text, fill=fg_color, font=self.font)
        else:
            self.create_text(self.winfo_reqwidth()//2, self.winfo_reqheight()//2, 
                           text=self.text, fill=fg_color, font=self.font)
    
    def create_rounded_rectangle(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def _on_click(self, event):
        if self.command:
            self.command()
    
    def _on_enter(self, event):
        self.state = "active"
        self.draw_button()
    
    def _on_leave(self, event):
        self.state = "normal"
        self.draw_button()
    
    def configure(self, **kwargs):
        if "text" in kwargs:
            self.text = kwargs["text"]
            self.draw_button()
        if "bg" in kwargs:
            self.bg = kwargs["bg"]
            self.draw_button()
        if "active_bg" in kwargs:
            self.active_bg = kwargs["active_bg"]
            self.draw_button()
        tk_kwargs = {k: v for k, v in kwargs.items() if k not in ["text", "bg", "active_bg"]}
        if tk_kwargs:
            super().configure(**tk_kwargs)

class ModernEntry(tk.Frame):
    def __init__(self, parent, placeholder="", **kwargs):
        super().__init__(parent, bg="#1A1A1A", relief="flat", bd=0)
        
        self.placeholder = placeholder
        self.placeholder_color = "#666666"
        self.text_color = "#FFFFFF"
        self.focus_color = "#1A1A1A"
        self.bg_color = "#1A1A1A"
        
        self.entry = tk.Entry(self, 
                             font=("Segoe UI", 10),
                             bg=self.bg_color,
                             fg=self.placeholder_color,
                             insertbackground=self.text_color,
                             relief="flat",
                             bd=0,
                             **kwargs)
        self.entry.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)
        
        # Événements
        self.entry.insert(0, placeholder)
        self.entry.bind('<FocusIn>', self._on_focus_in)
        self.entry.bind('<FocusOut>', self._on_focus_out)
        self.entry.bind('<KeyRelease>', self._on_key_release)
        
        # Support pour le mode read-only
        self._readonly = False
        
    def _on_focus_in(self, event):
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, tk.END)
            self.entry.config(fg=self.text_color)
        
        # Changement de couleur de fond au focus
        self.configure(bg=self.focus_color)
    
    def _on_focus_out(self, event):
        if not self.entry.get():
            self.entry.insert(0, self.placeholder)
            self.entry.config(fg=self.placeholder_color)
        
        # Retour à la couleur normale
        self.configure(bg=self.bg_color)
    
    def _on_key_release(self, event):
        if self.entry.get() and self.entry.get() != self.placeholder:
            self.entry.config(fg=self.text_color)
    
    def get(self):
        value = self.entry.get()
        return value if value != self.placeholder else ""
    
    def insert(self, index, string):
        self.entry.insert(index, string)
        if string and string != self.placeholder:
            self.entry.config(fg=self.text_color)
    
    def delete(self, first, last=None):
        if not self._readonly:
            self.entry.delete(first, last)
            if not self.entry.get():
                self.entry.config(fg=self.placeholder_color)
    
    def set_readonly(self, readonly=True):
        """Définit si le champ est en lecture seule"""
        self._readonly = readonly
        if readonly:
            self.entry.config(state="readonly", fg="#CCCCCC", readonlybackground="#1A1A1A")
            self.configure(bg="#1A1A1A")  # Garder la même couleur de fond
        else:
            self.entry.config(state="normal", fg=self.text_color)
            self.configure(bg=self.bg_color)
    
    def is_readonly(self):
        """Retourne si le champ est en lecture seule"""
        return self._readonly
    
    def set_text(self, text):
        """Définit le texte du champ (fonctionne même en lecture seule)"""
        if self._readonly:
            # Temporairement désactiver le mode readonly pour modifier le texte
            self.entry.config(state="normal")
            self.entry.delete(0, tk.END)
            self.entry.insert(0, text)
            self.entry.config(state="readonly")
        else:
            self.entry.delete(0, tk.END)
            self.entry.insert(0, text)



CONFIG_FILE = "spotify_nfc_config.json"
DEFAULT_CONFIG = {
    "auto_start": False,
}

# Créer l'application Flask
app = Flask(__name__)

@app.route("/spotify")
def open_spotify():
    link = request.args.get("link")
    if not link:
        return "Missing link", 400
    webbrowser.open(link)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Lien ouvert: {link}")
    html_content = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>Spotag - Succès</title>
        <link rel="icon" type="image/x-png" href="https://raw.githubusercontent.com/alex-m00n/Spotag/refs/heads/main/spotag2.png">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                background: linear-gradient(135deg, #0F0F0F 0%, #1A1A1A 100%);
                color: #fff;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center; 
                justify-content: center;
                min-height: 100vh;
                margin: 0;
                overflow: hidden;
            }
            
            .background-animation {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: -1;
                opacity: 0.1;
            }
            
            .background-animation::before {
                content: '';
                position: absolute;
                top: 50%;
                left: 50%;
                width: 200px;
                height: 200px;
                background: radial-gradient(circle, #1DB954 0%, transparent 70%);
                transform: translate(-50%, -50%);
                animation: pulse 3s ease-in-out infinite;
            }
            
            @keyframes pulse {
                0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.3; }
                50% { transform: translate(-50%, -50%) scale(1.2); opacity: 0.6; }
            }
            
            .container {
                background: rgba(26, 26, 26, 0.95);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(29, 185, 84, 0.2);
                border-radius: 24px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.5), 0 0 40px rgba(29, 185, 84, 0.1);
                padding: 50px 40px;
                text-align: center;
                max-width: 500px;
                width: 90%;
                transform: translateY(20px);
                animation: slideUp 0.8s ease-out forwards;
            }
            
            @keyframes slideUp {
                to {
                    transform: translateY(0);
                    opacity: 1;
                }
            }
            
            .icon {
                width: 80px;
                height: 80px;
                margin-bottom: 25px;
                filter: drop-shadow(0 8px 16px rgba(29, 185, 84, 0.3));
                animation: iconFloat 2s ease-in-out infinite;
            }
            
            @keyframes iconFloat {
                0%, 100% { transform: translateY(0px); }
                50% { transform: translateY(-10px); }
            }
            
            h1 {
                color: #1DB954;
                margin-bottom: 15px;
                font-size: 2.5em;
                font-weight: 700;
                text-shadow: 0 4px 8px rgba(29, 185, 84, 0.3);
                animation: fadeIn 1s ease-out 0.3s both;
            }
            
            p {
                font-size: 1.1em;
                margin-bottom: 0;
                line-height: 1.6;
                color: #CCCCCC;
                font-weight: 400;
                animation: fadeIn 1s ease-out 0.5s both;
            }
            
            .success-check {
                display: inline-block;
                width: 60px;
                height: 60px;
                background: #1DB954;
                border-radius: 50%;
                margin-bottom: 20px;
                position: relative;
                animation: checkAppear 0.6s ease-out 0.8s both;
            }
            
            .success-check::after {
                content: '✓';
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                color: white;
                font-size: 30px;
                font-weight: bold;
            }
            
            @keyframes checkAppear {
                from {
                    transform: scale(0) rotate(-180deg);
                    opacity: 0;
                }
                to {
                    transform: scale(1) rotate(0deg);
                    opacity: 1;
                }
            }
            
            @keyframes fadeIn {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            .spotify-link {
                margin-top: 25px;
                padding: 15px 25px;
                background: rgba(29, 185, 84, 0.1);
                border: 1px solid rgba(29, 185, 84, 0.3);
                border-radius: 12px;
                color: #1DB954;
                font-family: 'Consolas', monospace;
                font-size: 0.9em;
                word-break: break-all;
                animation: fadeIn 1s ease-out 0.7s both;
            }
        </style>
    </head>
    <body>
        <div class="background-animation"></div>
        <div class="container">
            <div class="success-check"></div>
            <img src="https://raw.githubusercontent.com/alex-m00n/Spotag/refs/heads/main/spotag2.png" alt="Spotag" class="icon">
            <h1>Prêt !</h1>
            <p>Le lien Spotify a été ouvert avec succès sur votre PC.<br><br>
            Vous pouvez maintenant utiliser l'application Spotify sur votre ordinateur pour écouter votre musique.</p>
            <div class="spotify-link">🎵 Spotify est en cours d'ouverture...</div>
        </div>
    </body>
    </html>
    """
    return html_content, 200

class SpotifyNFCGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Spotag - Spotify NFC pour PC")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        # Configuration de la fenêtre
        self.root.configure(bg="#0F0F0F")
        
        # Configuration de l'icône de la fenêtre
        try:
            # Essayer de charger l'icône avec le chemin absolu
            current_dir = os.path.dirname(os.path.abspath(__file__))
            icon_paths = [
                os.path.join(current_dir, "spotag.ico"),
                os.path.join(current_dir, "spotag2.png"),
                "spotag.ico",
                "spotag2.png",
            ]
            
            icon_loaded = False
            for icon_path in icon_paths:
                if os.path.exists(icon_path):
                    try:
                        if icon_path.endswith('.png'):
                            # Convertir PNG en ICO temporaire
                            from PIL import Image
                            img = Image.open(icon_path)
                            temp_ico = os.path.join(current_dir, "temp_icon.ico")
                            img.save(temp_ico, format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64)])
                            self.root.iconbitmap(temp_ico)
                            # Nettoyer le fichier temporaire
                            try:
                                os.remove(temp_ico)
                            except:
                                pass
                        else:
                            self.root.iconbitmap(icon_path)
                        print(f"✅ Icône chargée: {icon_path}")
                        icon_loaded = True
                        break
                    except Exception as e:
                        print(f"❌ Erreur avec {icon_path}: {e}")
                        continue
            
            if not icon_loaded:
                print("⚠️ Aucune icône n'a pu être chargée")
                
        except Exception as e:
            print(f"❌ Erreur générale lors du chargement de l'icône: {e}")
            pass
        
        self.config = self.load_config()
        self.tray_icon = None
        self.setup_styles()
        self.create_widgets()
        self.setup_system_tray()
        self.start_flask_server()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "localhost"
    
    def start_flask_server(self):
        """Démarre le serveur Flask dans un thread séparé"""
        def run_server():
            try:
                app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
            except Exception as e:
                print(f"Erreur lors du démarrage du serveur Flask: {e}")
        
        # Démarrer le serveur dans un thread séparé
        flask_thread = threading.Thread(target=run_server, daemon=True)
        flask_thread.start()
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Serveur Flask démarré sur http://{self.get_local_ip()}:5000")
    
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        self.spotify_green = "#1DB954"
        self.spotify_black = "#0F0F0F"
        self.spotify_dark_gray = "#1A1A1A"
        self.spotify_medium_gray = "#2A2A2A"
        self.spotify_white = "#FFFFFF"
        self.spotify_light_gray = "#CCCCCC"
        
        # Configuration des styles
        style.configure("Modern.TFrame", background=self.spotify_black)
        style.configure("Modern.TLabel", background=self.spotify_black, foreground=self.spotify_white)
        style.configure("Modern.TLabelframe", background=self.spotify_black, bordercolor=self.spotify_medium_gray)
        style.configure("Modern.TLabelframe.Label", background=self.spotify_black, foreground=self.spotify_white, font=("Segoe UI", 11, "bold"))
        
        self.root.configure(bg=self.spotify_black)
        
    def create_widgets(self):
        # Créer un canvas avec scrollbar
        canvas = tk.Canvas(self.root, bg=self.spotify_black, highlightthickness=0, relief="flat", bd=0)
        
        class YouTubeScrollbar(tk.Canvas):
            def __init__(self, parent, **kwargs):
                super().__init__(parent, **kwargs)
                self.parent = parent
                self.scrollable_widget = None
                self.scrollbar_width = 8
                self.scrollbar_color = "#606060"
                self.scrollbar_hover_color = "#909090"
                self.trough_color = "#0F0F0F"
                self.scrollbar_visible = False
                self.scrollbar_rect = None
                self.scrollbar_dragging = False
                self.last_y = 0
                
                # Configuration du canvas
                self.configure(
                    width=self.scrollbar_width,
                    bg=self.trough_color,
                    highlightthickness=0,
                    relief="flat",
                    bd=0
                )
                
                # Bindings
                self.bind("<Enter>", self.on_enter)
                self.bind("<Leave>", self.on_leave)
                self.bind("<Button-1>", self.on_click)
                self.bind("<B1-Motion>", self.on_drag)
                self.bind("<ButtonRelease-1>", self.on_release)
                self.bind("<MouseWheel>", self.on_mousewheel)
                
            def set_scrollable_widget(self, widget):
                self.scrollable_widget = widget
                self.update_scrollbar()
                
            def on_enter(self, event):
                self.scrollbar_color = self.scrollbar_hover_color
                self.draw_scrollbar()
                
            def on_leave(self, event):
                if not self.scrollbar_dragging:
                    self.scrollbar_color = "#606060"
                    self.draw_scrollbar()
                    
            def on_click(self, event):
                if self.scrollbar_rect:
                    x, y = event.x, event.y
                    if self.coords(self.scrollbar_rect)[1] <= y <= self.coords(self.scrollbar_rect)[3]:
                        self.scrollbar_dragging = True
                        self.last_y = y
                        
            def on_drag(self, event):
                if self.scrollbar_dragging and self.scrollable_widget:
                    delta_y = event.y - self.last_y
                    self.last_y = event.y
                    
                    # Calculer le déplacement relatif
                    canvas_height = self.winfo_height()
                    scrollbar_height = self.coords(self.scrollbar_rect)[3] - self.coords(self.scrollbar_rect)[1]
                    max_scrollbar_y = canvas_height - scrollbar_height
                    
                    current_y = self.coords(self.scrollbar_rect)[1]
                    new_y = max(0, min(max_scrollbar_y, current_y + delta_y))
                    
                    # Mettre à jour la position de la scrollbar
                    self.coords(self.scrollbar_rect, 0, new_y, self.scrollbar_width, new_y + scrollbar_height)
                    
                    # Calculer la position relative pour le widget
                    if max_scrollbar_y > 0:
                        relative_pos = new_y / max_scrollbar_y
                        self.scrollable_widget.yview_moveto(relative_pos)
                        
            def on_release(self, event):
                self.scrollbar_dragging = False
                
            def on_mousewheel(self, event):
                if self.scrollable_widget:
                    self.scrollable_widget.yview_scroll(int(-1 * (event.delta / 120)), "units")
                    self.update_scrollbar()
                    
            def draw_scrollbar(self):
                self.delete("scrollbar")
                if self.scrollbar_visible:
                    self.scrollbar_rect = self.create_rectangle(
                        0, 0, self.scrollbar_width, 50,
                        fill=self.scrollbar_color,
                        outline="",
                        tags="scrollbar"
                    )
                    
            def update_scrollbar(self):
                if not self.scrollable_widget:
                    return
                    
                # Obtenir les informations de scroll
                try:
                    first, last = self.scrollable_widget.yview()
                except Exception as e:
                    print(f"Erreur lors de la mise à jour de la scrollbar: {e}")
                    return
                    
                if first == 0 and last == 1:
                    # Pas besoin de scrollbar
                    self.scrollbar_visible = False
                    self.draw_scrollbar()
                    return
                    
                self.scrollbar_visible = True
                
                # Calculer la taille et position de la scrollbar
                canvas_height = self.winfo_height()
                if canvas_height <= 0:
                    return
                    
                scrollbar_height = max(30, int(canvas_height * (last - first)))
                scrollbar_y = int(canvas_height * first)
                
                # Dessiner la scrollbar
                self.delete("scrollbar")
                self.scrollbar_rect = self.create_rectangle(
                    0, scrollbar_y,
                    self.scrollbar_width, scrollbar_y + scrollbar_height,
                    fill=self.scrollbar_color,
                    outline="",
                    tags="scrollbar"
                )
        
        # Créer la scrollbar personnalisée
        scrollbar = YouTubeScrollbar(self.root)
        scrollable_frame = tk.Frame(canvas, bg=self.spotify_black, relief="flat", bd=0)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Configurer la scrollbar personnalisée
        scrollbar.set_scrollable_widget(canvas)
        canvas.configure(yscrollcommand=scrollbar.update_scrollbar)
        
        # Frame principal avec dégradé
        main_frame = tk.Frame(scrollable_frame, bg=self.spotify_black, relief="flat", bd=0)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # En-tête avec logo et titre
        header_frame = tk.Frame(main_frame, bg=self.spotify_black, relief="flat", bd=0)
        header_frame.pack(fill=tk.X, pady=(0, 30))
        
        # Logo et titre
        logo_frame = tk.Frame(header_frame, bg=self.spotify_black, relief="flat", bd=0)
        logo_frame.pack()
        
        # Titre principal avec effet de dégradé
        title_label = tk.Label(logo_frame, 
                              text="🎵 Spotag", 
                              font=("Segoe UI", 32, "bold"),
                              fg=self.spotify_green,
                              bg=self.spotify_black)
        title_label.pack()
        
        subtitle_label = tk.Label(logo_frame, 
                                 text="Spotify NFC pour PC", 
                                 font=("Segoe UI", 16),
                                 fg=self.spotify_light_gray,
                                 bg=self.spotify_black)
        subtitle_label.pack()
        
        # Section des boutons de contrôle
        control_frame = tk.Frame(main_frame, bg=self.spotify_dark_gray, relief="flat", bd=0)
        control_frame.pack(fill=tk.X, pady=(0, 25), padx=5)
        
        # Titre de section
        section_title = tk.Label(control_frame, 
                                text="Contrôles", 
                                font=("Segoe UI", 14, "bold"),
                                fg=self.spotify_white,
                                bg=self.spotify_dark_gray)
        section_title.pack(pady=(20, 15))
        
        # Boutons de contrôle
        button_frame = tk.Frame(control_frame, bg=self.spotify_dark_gray, relief="flat", bd=0)
        button_frame.pack(pady=20)
        
        self.minimize_button = ModernButton(button_frame, 
                                          text="Minimiser",
                                          command=self.hide_window,
                                          bg=self.spotify_medium_gray,
                                          active_bg="#505050",
                                          width=120, height=50,
                                          icon="➖")
        self.minimize_button.pack(side=tk.LEFT, padx=10)
        
        # URL du serveur
        url_frame = tk.Frame(control_frame, bg=self.spotify_dark_gray, relief="flat", bd=0)
        url_frame.pack(pady=20)
        
        url_label = tk.Label(url_frame, 
                            text="URL du serveur:", 
                            font=("Segoe UI", 10, "bold"), 
                            fg=self.spotify_white, 
                            bg=self.spotify_dark_gray)
        url_label.pack()
        
        local_ip = self.get_local_ip()
        self.url_label = tk.Label(url_frame, 
                                 text=f"http://{local_ip}:5000/spotify",
                                 font=("Consolas", 11),
                                 fg=self.spotify_green,
                                 bg=self.spotify_dark_gray)
        self.url_label.pack(pady=(8, 0))
        
        # Section du convertisseur
        converter_frame = tk.Frame(main_frame, bg=self.spotify_dark_gray, relief="flat", bd=0)
        converter_frame.pack(fill=tk.X, pady=(0, 25), padx=5)
        
        # Titre de section
        converter_title = tk.Label(converter_frame, 
                                  text="Convertisseur d'URL Spotify", 
                                  font=("Segoe UI", 14, "bold"),
                                  fg=self.spotify_white,
                                  bg=self.spotify_dark_gray)
        converter_title.pack(pady=(20, 15))
        
        # Champ de saisie du lien
        link_frame = tk.Frame(converter_frame, bg=self.spotify_dark_gray, relief="flat", bd=0)
        link_frame.pack(fill=tk.X, pady=15, padx=20)
        
        link_label = tk.Label(link_frame, 
                             text="Lien Spotify:", 
                             font=("Segoe UI", 10, "bold"), 
                             fg=self.spotify_white, 
                             bg=self.spotify_dark_gray)
        link_label.pack(anchor=tk.W)
        
        self.link_entry = ModernEntry(link_frame, 
                                     placeholder="https://open.spotify.com/track/...",
                                     width=50)
        self.link_entry.pack(fill=tk.X, pady=(8, 0))
        
        # Lier l'événement de changement pour la conversion automatique
        self.link_entry.entry.bind('<KeyRelease>', self.on_link_change)
        
        # Champ de résultat
        result_frame = tk.Frame(converter_frame, bg=self.spotify_dark_gray, relief="flat", bd=0)
        result_frame.pack(fill=tk.X, pady=(0, 20), padx=20)
        
        result_label = tk.Label(result_frame, 
                               text="URL Spotag:", 
                               font=("Segoe UI", 10, "bold"), 
                               fg=self.spotify_white, 
                               bg=self.spotify_dark_gray)
        result_label.pack(anchor=tk.W)
        
        # Frame pour l'entry et le bouton copier
        result_input_frame = tk.Frame(result_frame, bg=self.spotify_dark_gray, relief="flat", bd=0)
        result_input_frame.pack(fill=tk.X, pady=(8, 0))
        
        self.result_entry = ModernEntry(result_input_frame, 
                                       placeholder="Entrez un lien Spotify valide",
                                       width=50)
        self.result_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Définir le champ URL Spotag en lecture seule
        self.result_entry.set_readonly(True)
        
        copy_button = ModernButton(result_input_frame, 
                                  text="Copier",
                                  command=lambda: self.copy_to_clipboard(self.result_entry.get()),
                                  bg=self.spotify_medium_gray,
                                  active_bg="#505050",
                                  width=100, height=45,
                                  icon="📋")
        copy_button.pack(side=tk.RIGHT, padx=(15, 0))
        
        # Footer
        footer_frame = tk.Frame(main_frame, bg=self.spotify_black, relief="flat", bd=0)
        footer_frame.pack(fill=tk.X, pady=(20, 0))
        
        footer_text = tk.Label(footer_frame, 
                              text="Développé avec ♥ par AlexM00n", 
                              font=("Segoe UI", 9),
                              fg=self.spotify_light_gray,
                              bg=self.spotify_black)
        footer_text.pack()
        
        # Configurer le scroll avec la scrollbar YouTube
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Centrer le contenu dans le canvas
        def center_content():
            canvas.update_idletasks()
            canvas_width = canvas.winfo_width()
            frame_width = scrollable_frame.winfo_reqwidth()
            if frame_width < canvas_width:
                x_offset = (canvas_width - frame_width) // 2
                canvas.coords(canvas.find_withtag("all")[0], x_offset, 0)
        
        # Centrer après le chargement et lors du redimensionnement
        self.root.after(100, center_content)
        canvas.bind('<Configure>', lambda e: center_content())
        
        # Lier les événements de scroll
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            scrollbar.update_scrollbar()
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def setup_system_tray(self):
        """Configure l'icône de la barre système"""
        try:
            # Créer l'icône pour la barre système
            tray_image = self.create_tray_image()
            
            # Menu contextuel pour la barre système
            menu = pystray.Menu(
                pystray.MenuItem("Afficher Spotag", self.show_window),
                pystray.MenuItem("Masquer Spotag", self.hide_window),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Quitter", self.quit_application)
            )
            
            self.tray_icon = pystray.Icon("Spotag", tray_image, "Spotag - Spotify NFC", menu)
            
            # Démarrer l'icône de la barre système dans un thread séparé
            tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
            tray_thread.start()
            
        except Exception as e:
            print(f"Erreur lors de la configuration de la barre système: {e}")
    
    def create_tray_image(self):
        """Crée l'icône pour la barre système"""
        try:
            # Essayer de charger l'icône spotag2.png
            current_dir = os.path.dirname(os.path.abspath(__file__))
            icon_paths = [
                os.path.join(current_dir, "spotag2.png"),
                os.path.join(current_dir, "spotag.ico"),
                "spotag2.png",
                "spotag.ico"
            ]
            
            for icon_path in icon_paths:
                if os.path.exists(icon_path):
                    try:
                        if icon_path.endswith('.png'):
                            icon = Image.open(icon_path)
                        else:
                            # Convertir ICO en PNG
                            icon = Image.open(icon_path)
                        
                        # Redimensionner à 64x64 pour la barre système
                        icon = icon.resize((64, 64), Image.Resampling.LANCZOS)
                        return icon
                    except Exception as e:
                        print(f"Erreur avec {icon_path}: {e}")
                        continue
        except Exception as e:
            print(f"Erreur lors du chargement de l'icône: {e}")
        
        # Fallback: Icône simple (cercle vert façon Spotify)
        image = Image.new("RGB", (64, 64), (15, 15, 15))
        draw = ImageDraw.Draw(image)
        draw.ellipse((8, 8, 56, 56), fill=(29, 185, 84))
        # Ajouter un petit symbole musical
        draw.text((32, 32), "♪", fill="white", anchor="mm")
        return image
    
    def show_window(self, icon=None, item=None):
        """Affiche la fenêtre principale"""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
    
    def hide_window(self, icon=None, item=None):
        """Masque la fenêtre principale"""
        self.root.withdraw()
    
    def quit_application(self, icon=None, item=None):
        """Quitte complètement l'application"""
        if self.tray_icon:
            self.tray_icon.stop()
        self.save_config()
        self.root.quit()
        os._exit(0)
        
    def load_config(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement de la configuration: {e}")
        return DEFAULT_CONFIG.copy()
    
    def save_config(self):
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la configuration: {e}")
    
    def on_link_change(self, event=None):
        self.convert_link()
    
    def convert_link(self):
        link = self.link_entry.get().strip()
        
        if not link or link == "https://open.spotify.com/track/...":
            self.result_entry.set_text("Entrez un lien Spotify valide")
            return
        
        if not link.startswith("https://open.spotify.com/"):
            self.result_entry.set_text("Lien Spotify invalide")
            return
        
        try:
            parts = link.split('/')
            if len(parts) >= 5:
                # Gérer les URLs avec locale (ex: /intl-fr/album/)
                if len(parts) >= 6 and parts[3].startswith('intl-'):
                    # URL avec locale: https://open.spotify.com/intl-fr/album/Abcde1245
                    spotify_type = parts[4]  # album, track, playlist, etc.
                    spotify_id = parts[5].split('?')[0]
                else:
                    # URL normale: https://open.spotify.com/album/Abcde1245
                    spotify_type = parts[3]
                    spotify_id = parts[4].split('?')[0]
                
                # Générer l'URI Spotify
                spotify_uri = f"spotify:{spotify_type}:{spotify_id}"
                self.result_entry.set_text(spotify_uri)
            else:
                raise ValueError("Format d'URL invalide")
        except Exception as e:
            self.result_entry.set_text(f"Erreur: {str(e)}")
    
    def copy_to_clipboard(self, text):
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            messagebox.showinfo("Succès", "Texte copié dans le presse-papiers!")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de copier: {e}")
    
    def on_closing(self):
        # Minimiser dans la barre système au lieu de fermer
        self.hide_window()
        # Optionnel: Afficher une notification
        if self.tray_icon:
            try:
                self.tray_icon.notify("Spotag a été minimisé dans la barre système", "Spotag")
            except:
                pass  # Ignorer les erreurs de notification





if __name__ == "__main__":
    # Vérifier si une instance est déjà en cours d'exécution
    import socket
    try:
        # Essayer de créer un socket sur un port spécifique pour détecter les instances multiples
        lock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lock_socket.bind(('localhost', 5001))  # Port de verrouillage
        lock_socket.close()
    except socket.error:
        # Une instance est déjà en cours d'exécution
        import tkinter.messagebox as msgbox
        msgbox.showwarning("Spotag", "Une instance de Spotag est déjà en cours d'exécution.")
        sys.exit(1)
    
    # Créer l'interface graphique
    root = tk.Tk()
    app_gui = SpotifyNFCGUI(root)
    
    # Lancer l'interface
    root.mainloop()
