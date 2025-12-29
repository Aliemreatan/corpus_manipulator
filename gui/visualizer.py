"""
Corpus Visualizer Module

Bu modül, Tkinter arayüzü içine Matplotlib grafikleri gömmek için kullanılır.
Bar Chart, Pie Chart ve Word Cloud gibi görselleştirmeler sağlar.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import logging

# Opsiyonel WordCloud desteği
try:
    from wordcloud import WordCloud
    WORDCLOUD_AVAILABLE = True
except ImportError:
    WORDCLOUD_AVAILABLE = False

class CorpusVisualizer:
    """Handles data visualization generation and embedding"""
    
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.figure = None
        self.canvas = None
        
        # Matplotlib style
        plt.style.use('ggplot')
        
        # Create container for plot
        self.plot_frame = ttk.Frame(self.parent)
        self.plot_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def clear_plot(self):
        """Mevcut grafiği temizle"""
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        if self.figure:
            plt.close(self.figure)
            self.figure = None

    def plot_bar_chart(self, data, title="En Sık Kullanılan Kelimeler", xlabel="Kelime", ylabel="Frekans"):
        """Sütun grafiği çiz (Top N kelimeler)"""
        self.clear_plot()
        
        # Veriyi hazırla
        words = [item['word'] for item in data]
        counts = [item['frequency'] for item in data]
        
        # Grafik oluştur
        self.figure, ax = plt.subplots(figsize=(10, 6), dpi=100)
        
        # Çubukları çiz
        bars = ax.bar(words, counts, color='#3498db')
        
        # Etiketler ve Başlık
        ax.set_title(title, fontsize=14)
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        
        # X ekseni yazıları okunabilsin diye döndür
        plt.xticks(rotation=45, ha='right')
        
        # Değerleri çubukların üzerine yaz
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=8)
        
        # Layout sıkıştırma (yazılar kesilmesin diye)
        plt.tight_layout()
        
        # Tkinter'a göm
        self._embed_plot()

    def plot_pie_chart(self, data, title="POS Etiket Dağılımı"):
        """Pasta grafiği çiz (POS dağılımı)"""
        self.clear_plot()
        
        # Veriyi hazırla (None olanları filtrele)
        labels = [item['pos'] if item['pos'] else "Bilinmeyen" for item in data]
        sizes = [item['count'] for item in data]
        
        # Grafik oluştur
        self.figure, ax = plt.subplots(figsize=(8, 6), dpi=100)
        
        # Pasta dilimlerini çiz
        # Sadece %2'den büyük olanları etiketle, karmaşayı önle
        def make_autopct(values):
            def my_autopct(pct):
                return f'{pct:.1f}%' if pct > 2 else ''
            return my_autopct

        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct=make_autopct(sizes),
                                          startangle=90, pctdistance=0.85, shadow=True)
        
        # Halka görünümü için ortayı beyaz yap
        centre_circle = plt.Circle((0,0),0.70,fc='white')
        self.figure.gca().add_artist(centre_circle)
        
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        ax.set_title(title, fontsize=14)
        
        plt.tight_layout()
        
        # Tkinter'a göm
        self._embed_plot()

    def plot_word_cloud(self, data):
        """Kelime bulutu çiz"""
        self.clear_plot()
        
        if not WORDCLOUD_AVAILABLE:
            self._show_error("WordCloud kütüphanesi eksik", 
                           "Lütfen terminalden şu komutu çalıştırın:\npip install wordcloud")
            return

        # Veriyi hazırla (Dict formatı gerekli: {'kelime': frekans})
        word_freq = {item['word']: item['frequency'] for item in data}
        
        if not word_freq:
            self._show_error("Veri Yok", "Görselleştirilecek veri bulunamadı.")
            return

        # WordCloud oluştur
        try:
            wc = WordCloud(width=800, height=400, background_color='white', 
                          colormap='viridis', max_words=100).generate_from_frequencies(word_freq)
            
            # Grafik oluştur
            self.figure, ax = plt.subplots(figsize=(10, 6), dpi=100)
            ax.imshow(wc, interpolation='bilinear')
            ax.axis('off')
            ax.set_title("Kelime Bulutu", fontsize=14)
            
            plt.tight_layout()
            self._embed_plot()
            
        except Exception as e:
            self._show_error("WordCloud Hatası", str(e))

    def _embed_plot(self):
        """Oluşturulan grafiği Tkinter canvas'ına yerleştir"""
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _show_error(self, title, message):
        """Hata mesajını grafik alanında göster"""
        self.figure, ax = plt.subplots(figsize=(5, 1))
        ax.text(0.5, 0.5, f"{title}\n{message}", 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, color='red')
        ax.axis('off')
        self._embed_plot()
