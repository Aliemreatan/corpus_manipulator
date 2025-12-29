#!/usr/bin/env python3
"""
Corpus Data Manipulator - GUI Application

Tkinter tabanlı kullanıcı arayüzü ile Corpus Data Manipulator'ı GUI üzerinden kullanma

Özellikler:
- Klasör seçme ve corpus içeri aktarma
- KWIC arama
- Frekans analizi
- Collocation analizi
- Word sketch
- Sonuçları görüntüleme

Kullanım:
    py corpus_gui.py
"""

# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import sys
import os
from pathlib import Path
import threading
import json

# Set UTF-8 encoding for Turkish characters
if sys.platform.startswith('win'):
    try:
        import codecs
        import io
        
        # Only redirect if stdout is still valid
        if hasattr(sys.stdout, 'buffer') and not sys.stdout.closed:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'buffer') and not sys.stderr.closed:
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        # Fallback for older Python versions
        try:
            if not sys.stdout.closed:
                sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
            if not sys.stderr.closed:
                sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
        except:
            pass  # Continue if it fails

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.schema import CorpusDatabase
from nlp.turkish_processor import TurkishNLPProcessor
from ingestion.corpus_ingestor import CorpusIngestor
from query.corpus_query import CorpusQuery

class CorpusGUI:
    """Main GUI application for Corpus Data Manipulator"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Corpus Data Manipulator - Türkçe")
        self.root.geometry("1200x800")
        
        # Variables
        self.db_path = tk.StringVar(value="corpus.db")
        self.corpus_dir = tk.StringVar()
        self.search_term = tk.StringVar()
        self.window_size = tk.IntVar(value=5)
        self.analysis_type = tk.StringVar(value="kwic")
        self.corpus_source_var = tk.StringVar(value="database")  # Default to database
        
        # Components
        self.setup_ui()
    
    def _ensure_utf8_text(self, text):
        """Ensure text is properly encoded as UTF-8 for BERT processing"""
        if not isinstance(text, str):
            text = str(text)
        
        # Fix common Turkish keyboard mapping issues
        # Some keyboards may show 'ş' as 'þ' and 'ı' as 'ý'
        keyboard_fixes = {
            'þ': 'ş',  # thorn to s-cedilla
            'ý': 'ı',  # y-acute to dotless-i
        }
        
        for wrong_char, correct_char in keyboard_fixes.items():
            text = text.replace(wrong_char, correct_char)
        
        # Ensure UTF-8 encoding and handle any encoding issues
        try:
            # Normalize to NFC form for consistent handling
            import unicodedata
            text = unicodedata.normalize('NFC', text)
            return text
        except Exception as e:
            print(f"Warning: Text encoding issue: {e}")
            return text
        
    def setup_ui(self):
        """Setup the user interface"""

        # Create main container with grid
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Create notebook (tab system) inside main frame
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create tabs
        self.setup_database_tab()
        self.setup_ingestion_tab()
        self.setup_corpus_editor_tab()
        self.setup_file_editor_tab()
        self.setup_analysis_tab()
        self.setup_realtime_analysis_tab()
        self.setup_visualization_tab()
        self.setup_tools_tab()
        self.setup_results_tab()

        # Status bar at bottom
        self.status_var = tk.StringVar(value="Hazır")
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        status_frame.columnconfigure(0, weight=1)

        self.status_bar = ttk.Label(status_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
    def setup_database_tab(self):
        """Setup database configuration tab"""
        db_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(db_frame, text="Veritabanı")

        self.setup_database_section(db_frame)

    def setup_ingestion_tab(self):
        """Setup corpus ingestion tab"""
        ingest_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(ingest_frame, text="İçeri Aktarma")

        self.setup_ingestion_section(ingest_frame)

    def setup_corpus_editor_tab(self):
        """Setup corpus editor tab"""
        editor_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(editor_frame, text="Corpus Düzenleme")

        self.setup_corpus_editor_section(editor_frame)

    def setup_tools_tab(self):
        """Setup tools tab"""
        tools_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tools_frame, text="Araçlar")

        self.setup_tools_section(tools_frame)

    def setup_analysis_tab(self):
        """Setup analysis tab"""
        analysis_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(analysis_frame, text="Analiz")

        self.setup_analysis_section(analysis_frame)

    def setup_visualization_tab(self):
        """Setup visualization tab"""
        viz_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(viz_frame, text="Görselleştirme")

        self.setup_visualization_section(viz_frame)

    def setup_realtime_analysis_tab(self):
        """Setup real-time analysis tab"""
        realtime_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(realtime_frame, text="Anlık Analiz")

        self.setup_realtime_analysis_section(realtime_frame)

    def setup_results_tab(self):
        """Setup results tab"""
        results_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(results_frame, text="Sonuçlar")

        self.setup_results_section(results_frame)

    def setup_file_editor_tab(self):
        """Setup file editor tab for editing saved analysis files"""
        editor_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(editor_frame, text="Dosya Düzenleme")

        self.setup_file_editor_section(editor_frame)
        
    def setup_file_editor_section(self, parent):
        """Setup file editor section for editing saved analysis files"""

        # Configure grid weights
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)

        # File selection frame
        file_frame = ttk.Frame(parent)
        file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)

        # Current file label
        ttk.Label(file_frame, text="Düzenlenen Dosya:").grid(row=0, column=0, sticky=tk.W)
        self.edit_file_var = tk.StringVar(value="Dosya seçilmedi")
        ttk.Label(file_frame, textvariable=self.edit_file_var, foreground="blue").grid(row=0, column=1, sticky=tk.W, padx=(10, 0))

        # File operation buttons
        button_frame = ttk.Frame(file_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=(5, 0))

        ttk.Button(button_frame, text="JSON Aç", command=self.load_json_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="XML Aç", command=self.load_xml_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="TXT Aç", command=self.load_txt_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Kaydet", command=self.save_edited_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Farklı Kaydet", command=self.save_edited_file_as).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Doğrula", command=self.validate_file_format).pack(side=tk.LEFT, padx=(0, 5))

        # Format info
        ttk.Label(file_frame, text="İpucu: JSON/XML dosyalarını düzenledikten sonra 'Doğrula' butonuna tıklayın",
                 font=("Arial", 8, "italic"), foreground="gray").grid(row=2, column=0, columnspan=2, pady=(5, 0))

        # Text editor for file content
        self.file_editor_text = scrolledtext.ScrolledText(parent, wrap=tk.WORD, font=("Consolas", 10))
        self.file_editor_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Editor status
        self.file_editor_status_var = tk.StringVar(value="")
        ttk.Label(parent, textvariable=self.file_editor_status_var, foreground="green").grid(row=2, column=0, sticky=tk.W, pady=(5, 0))

        # Track current edited file
        self.current_edit_file_path = None
        self.edit_file_format = None  # 'json', 'xml', or 'txt'
    
    def load_json_file(self):
        """Load a JSON file for editing"""
        filename = filedialog.askopenfilename(
            title="JSON Dosyası Aç",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.file_editor_text.delete(1.0, tk.END)
                self.file_editor_text.insert(tk.END, content)
                
                self.current_edit_file_path = filename
                self.edit_file_var.set(filename)
                self.edit_file_format = 'json'
                self.file_editor_status_var.set("JSON dosyası yüklendi")
                
            except Exception as e:
                messagebox.showerror("Hata", f"JSON dosyası açılamadı: {str(e)}")
    
    def load_xml_file(self):
        """Load an XML file for editing"""
        filename = filedialog.askopenfilename(
            title="XML Dosyası Aç",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.file_editor_text.delete(1.0, tk.END)
                self.file_editor_text.insert(tk.END, content)
                
                self.current_edit_file_path = filename
                self.edit_file_var.set(filename)
                self.edit_file_format = 'xml'
                self.file_editor_status_var.set("XML dosyası yüklendi")
                
            except Exception as e:
                messagebox.showerror("Hata", f"XML dosyası açılamadı: {str(e)}")
    
    def load_txt_file(self):
        """Load a TXT file for editing"""
        filename = filedialog.askopenfilename(
            title="TXT Dosyası Aç",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.file_editor_text.delete(1.0, tk.END)
                self.file_editor_text.insert(tk.END, content)
                
                self.current_edit_file_path = filename
                self.edit_file_var.set(filename)
                self.edit_file_format = 'txt'
                self.file_editor_status_var.set("TXT dosyası yüklendi")
                
            except Exception as e:
                messagebox.showerror("Hata", f"TXT dosyası açılamadı: {str(e)}")
    
    def save_edited_file(self):
        """Save the edited file"""
        if not self.current_edit_file_path:
            messagebox.showwarning("Uyarı", "Kaydedilecek dosya yok!")
            return
        
        content = self.file_editor_text.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("Uyarı", "Kaydedilecek içerik yok!")
            return
        
        try:
            with open(self.current_edit_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.file_editor_status_var.set(f"Dosya kaydedildi: {self.current_edit_file_path}")
            messagebox.showinfo("Başarılı", "Dosya başarıyla kaydedildi!")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya kaydedilemedi: {str(e)}")
    
    def save_edited_file_as(self):
        """Save the edited file with a new name"""
        content = self.file_editor_text.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("Uyarı", "Kaydedilecek içerik yok!")
            return
        
        # Determine default extension
        defaultextension = ".txt"
        filetypes = [("All files", "*.*")]
        
        if self.edit_file_format == 'json':
            defaultextension = ".json"
            filetypes = [("JSON files", "*.json"), ("All files", "*.*")]
        elif self.edit_file_format == 'xml':
            defaultextension = ".xml"
            filetypes = [("XML files", "*.xml"), ("All files", "*.*")]
        elif self.edit_file_format == 'txt':
            defaultextension = ".txt"
            filetypes = [("Text files", "*.txt"), ("All files", "*.*")]
        
        filename = filedialog.asksaveasfilename(
            title="Düzenlenen Dosyayı Farklı Kaydet",
            defaultextension=defaultextension,
            filetypes=filetypes
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.current_edit_file_path = filename
                self.edit_file_var.set(filename)
                self.file_editor_status_var.set(f"Dosya kaydedildi: {filename}")
                messagebox.showinfo("Başarılı", f"Dosya {filename} olarak kaydedildi!")
                
            except Exception as e:
                messagebox.showerror("Hata", f"Dosya kaydedilemedi: {str(e)}")
    
    def validate_file_format(self):
        """Validate the current file format (JSON/XML)"""
        if not self.edit_file_format or self.edit_file_format == 'txt':
            messagebox.showinfo("Bilgi", "TXT dosyaları için doğrulama gerekli değildir.")
            return
        
        content = self.file_editor_text.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("Uyarı", "Doğrulanacak içerik yok!")
            return
        
        try:
            if self.edit_file_format == 'json':
                json.loads(content)
                self.file_editor_status_var.set("✓ JSON formatı geçerli")
                messagebox.showinfo("Başarılı", "JSON formatı geçerli!")
                
            elif self.edit_file_format == 'xml':
                # Basic XML validation
                import xml.etree.ElementTree as ET
                ET.fromstring(content)
                self.file_editor_status_var.set("✓ XML formatı geçerli")
                messagebox.showinfo("Başarılı", "XML formatı geçerli!")
                
        except json.JSONDecodeError as e:
            self.file_editor_status_var.set("✗ JSON hatası")
            messagebox.showerror("JSON Hatası", f"Geçersiz JSON formatı:\n{str(e)}")
            
        except ET.ParseError as e:
            self.file_editor_status_var.set("✗ XML hatası")
            messagebox.showerror("XML Hatası", f"Geçersiz XML formatı:\n{str(e)}")
            
        except Exception as e:
            self.file_editor_status_var.set("✗ Doğrulama hatası")
            messagebox.showerror("Hata", f"Doğrulama yapılamadı: {str(e)}")
        
    def setup_database_section(self, parent):
        """Setup database configuration section"""

        # Configure grid weights
        parent.columnconfigure(1, weight=1)

        # Database path
        ttk.Label(parent, text="Veritabanı Dosyası:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(parent, textvariable=self.db_path, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 5))
        ttk.Button(parent, text="Gözat", command=self.browse_database).grid(row=0, column=2)

        # Create database button
        ttk.Button(parent, text="Veritabanı Oluştur", command=self.create_database).grid(row=1, column=0, columnspan=3, pady=(10, 0))
        
    def setup_ingestion_section(self, parent):
        """Setup corpus ingestion section"""

        # Configure grid weights
        parent.columnconfigure(1, weight=1)

        # Corpus directory
        ttk.Label(parent, text="Metin Klasörü:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(parent, textvariable=self.corpus_dir, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 5))
        ttk.Button(parent, text="Gözat", command=self.browse_corpus_dir).grid(row=0, column=2)

        # NLP Backend selection
        ttk.Label(parent, text="NLP Backend:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.backend_var = tk.StringVar(value="custom_bert")  # Default to BERT now
        backend_combo = ttk.Combobox(parent, textvariable=self.backend_var,
                                    values=["custom_bert", "stanza", "spacy", "simple"], state="readonly")
        backend_combo.grid(row=1, column=1, sticky=tk.W, padx=(10, 5), pady=(10, 0))

        # File formats info
        ttk.Label(parent, text="Desteklenen Formatlar:", font=("Arial", 8, "italic")).grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        ttk.Label(parent, text="TXT, JSON, XML dosyaları", font=("Arial", 8)).grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=(5, 0))

        # Ingest button
        ttk.Button(parent, text="Corpus'u İçeri Aktar", command=self.ingest_corpus).grid(row=3, column=0, columnspan=3, pady=(10, 0))
        
    def setup_corpus_editor_section(self, parent):
        """Setup corpus editor section"""

        # Configure grid weights
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)

        # File selection frame
        file_frame = ttk.Frame(parent)
        file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)

        # Current file label
        ttk.Label(file_frame, text="Düzenlenen Dosya:").grid(row=0, column=0, sticky=tk.W)
        self.current_file_var = tk.StringVar(value="Dosya seçilmedi")
        ttk.Label(file_frame, textvariable=self.current_file_var, foreground="blue").grid(row=0, column=1, sticky=tk.W, padx=(10, 0))

        # File operation buttons
        button_frame = ttk.Frame(file_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=(5, 0))

        ttk.Button(button_frame, text="Dosya Aç", command=self.load_corpus_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Kaydet", command=self.save_corpus_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Farklı Kaydet", command=self.save_corpus_file_as).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Yeni Dosya", command=self.new_corpus_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Veritabanını Güncelle", command=self.update_database_from_editor).pack(side=tk.LEFT, padx=(0, 5))

        # Text editor
        self.editor_text = scrolledtext.ScrolledText(parent, wrap=tk.WORD, font=("Consolas", 10))
        self.editor_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Editor status
        self.editor_status_var = tk.StringVar(value="")
        ttk.Label(parent, textvariable=self.editor_status_var, foreground="green").grid(row=2, column=0, sticky=tk.W, pady=(5, 0))

        # Track current file
        self.current_file_path = None
        self.original_content = ""

    def setup_tools_section(self, parent):
        """Setup tools section"""
        
        # Configure grid
        parent.columnconfigure(0, weight=1)
        
        # BERT Re-tagging Tool
        bert_frame = ttk.LabelFrame(parent, text="BERT Re-Tagging Aracı", padding="10")
        bert_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        ttk.Label(bert_frame, text="Mevcut veritabanındaki tüm cümleleri BERT modeli ile yeniden işler.", 
                 wraplength=800).pack(anchor=tk.W, pady=(0, 5))
        
        ttk.Label(bert_frame, text="Bu işlem:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
        ttk.Label(bert_frame, text="1. Tüm cümleleri veritabanından çeker").pack(anchor=tk.W, padx=(20, 0))
        ttk.Label(bert_frame, text="2. Tokenizasyon ve POS etiketlemeyi BERT ile yeniler").pack(anchor=tk.W, padx=(20, 0))
        ttk.Label(bert_frame, text="3. Eski 'simple' tokenları silip yenilerini kaydeder").pack(anchor=tk.W, padx=(20, 0))
        
        ttk.Label(bert_frame, text="Uyarı: Büyük veritabanları için bu işlem uzun sürebilir!", 
                 foreground="red").pack(anchor=tk.W, pady=(10, 5))
        
        ttk.Button(bert_frame, text="Veritabanını BERT ile Güncelle", 
                  command=self.run_bert_retagging).pack(pady=10)
        
        # Database Editor Tool
        editor_frame = ttk.LabelFrame(parent, text="Veritabanı Düzenleyici", padding="10")
        editor_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        ttk.Label(editor_frame, text="Veritabanındaki verileri manuel olarak görüntüleyin ve düzenleyin.", 
                 wraplength=800).pack(anchor=tk.W, pady=(0, 5))
                 
        ttk.Button(editor_frame, text="Veritabanı Editörünü Aç", 
                  command=self.open_database_editor).pack(pady=10)
        
        # Statistics Tool
        stats_frame = ttk.LabelFrame(parent, text="İstatistikler", padding="10")
        stats_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N), padx=(10, 0), pady=(0, 20))
        
        ttk.Label(stats_frame, text="Corpus hakkında derinlemesine analizler.", 
                 wraplength=300).pack(anchor=tk.W, pady=(0, 5))
        
        ttk.Button(stats_frame, text="Detaylı İstatistik Raporu", 
                  command=self.show_advanced_stats).pack(pady=10)
                  
        # Export Tool
        export_frame = ttk.LabelFrame(parent, text="Dışa Aktarma (Export)", padding="10")
        export_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N), padx=(10, 0), pady=(0, 20))
        
        ttk.Label(export_frame, text="Verileri akademik formatlarda dışa aktarın.", 
                 wraplength=300).pack(anchor=tk.W, pady=(0, 5))
        
        ttk.Button(export_frame, text="CoNLL-U Formatında Dışa Aktar", 
                  command=self.export_conllu).pack(pady=10)

    def show_advanced_stats(self):
        """Show advanced corpus statistics"""
        if not self.db_path.get():
            messagebox.showwarning("Uyarı", "Lütfen önce veritabanı dosyasını seçin!")
            return
            
        try:
            query = CorpusQuery(self.db_path.get())
            stats = query.get_advanced_stats()
            query.close()
            
            # Create popup
            win = tk.Toplevel(self.root)
            win.title("Detaylı Corpus Raporu")
            win.geometry("500x600")
            
            text = scrolledtext.ScrolledText(win, wrap=tk.WORD, font=("Consolas", 10))
            text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Formatting
            text.insert(tk.END, "=== CORPUS SAĞLIK RAPORU ===\n\n")
            
            text.insert(tk.END, "GENEL METRİKLER:\n")
            text.insert(tk.END, f"• Toplam Token:    {stats['total_tokens']:,}\n")
            text.insert(tk.END, f"• Benzersiz Kelime:{stats['unique_types']:,}\n")
            text.insert(tk.END, f"• Toplam Cümle:    {stats['total_sentences']:,}\n\n")
            
            text.insert(tk.END, "DİLBİLİMSEL METRİKLER:\n")
            text.insert(tk.END, f"• TTR (Sözcük Çeşitliliği): %{stats['ttr']*100:.2f}\n")
            text.insert(tk.END, "  (Yüksek TTR, zengin bir kelime dağarcığını gösterir)\n\n")
            
            text.insert(tk.END, f"• Ort. Cümle Uzunluğu:      {stats['avg_sent_len']:.2f} kelime\n\n")
            
            text.insert(tk.END, "POS DAĞILIMI (EN SIK 5):\n")
            for pos, count in stats['top_pos']:
                pos_name = pos if pos else "Bilinmeyen"
                ratio = (count / stats['total_tokens']) * 100
                text.insert(tk.END, f"• {pos_name:<10}: {count:,} (%{ratio:.1f})\n")
                
            text.configure(state='disabled')
            
        except Exception as e:
            messagebox.showerror("Hata", f"İstatistikler alınamadı: {e}")

    def export_conllu(self):
        """Export database to CoNLL-U format"""
        if not self.db_path.get():
            messagebox.showwarning("Uyarı", "Lütfen önce veritabanı dosyasını seçin!")
            return
            
        filename = filedialog.asksaveasfilename(
            title="CoNLL-U Olarak Kaydet",
            defaultextension=".conllu",
            filetypes=[("CoNLL-U files", "*.conllu"), ("All files", "*.*")]
        )
        
        if not filename:
            return
            
        try:
            self.status_var.set("CoNLL-U export hazırlanıyor...")
            self.root.update()
            
            query = CorpusQuery(self.db_path.get())
            generator = query.get_all_tokens_for_export()
            
            with open(filename, 'w', encoding='utf-8') as f:
                # Header info
                f.write(f"# global.columns = ID FORM LEMMA UPOS XPOS FEATS HEAD DEPREL DEPS MISC\n")
                
                sent_count = 0
                
                for row, is_new_sent in generator:
                    sent_id, token_num, form, lemma, upos, xpos, morph, head, dep, text, doc = row
                    
                    if is_new_sent:
                        if sent_count > 0:
                            f.write("\n") # Empty line between sentences
                        
                        sent_count += 1
                        # Sentence headers
                        f.write(f"# sent_id = {sent_id}\n")
                        f.write(f"# text = {text}\n")
                        f.write(f"# doc = {doc}\n")
                    
                    # CoNLL-U Fields (1-based index)
                    # ID, FORM, LEMMA, UPOS, XPOS, FEATS, HEAD, DEPREL, DEPS, MISC
                    
                    # Handle None values
                    form = form if form else "_"
                    lemma = lemma if lemma else "_"
                    upos = upos if upos else "_"
                    xpos = xpos if xpos else "_"
                    morph = morph if morph else "_"
                    head = str(head) if head is not None else "0" # Root is usually 0
                    dep = dep if dep else "_"
                    
                    # Write line
                    # ID is token_num + 1 (1-based)
                    f.write(f"{token_num + 1}\t{form}\t{lemma}\t{upos}\t{xpos}\t{morph}\t{head}\t{dep}\t_\t_\n")
                
                f.write("\n") # Final newline
                
            query.close()
            self.status_var.set("CoNLL-U export tamamlandı")
            messagebox.showinfo("Başarılı", f"CoNLL-U dosyası oluşturuldu:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Export hatası: {e}")
            self.status_var.set("Hata oluştu")
        
    def run_bert_retagging(self):
        """Run BERT re-tagging in background"""
        if not self.db_path.get():
            messagebox.showwarning("Uyarı", "Lütfen önce veritabanı dosyasını seçin!")
            return
            
        result = messagebox.askyesno("Onay", 
                                   "Bu işlem veritabanındaki tüm analizleri silip BERT ile yeniden oluşturacak.\n\n"
                                   "Bu işlem geri alınamaz. Devam etmek istiyor musunuz?")
        
        if not result:
            return
            
        # Start in background thread
        thread = threading.Thread(target=self._bert_retagging_thread)
        thread.daemon = True
        thread.start()

    def open_database_editor(self):
        """Open the database editor window"""
        if not self.db_path.get():
            messagebox.showwarning("Uyarı", "Lütfen önce veritabanı dosyasını seçin!")
            return
            
        try:
            from gui.database_editor import DatabaseEditor
            editor_window = tk.Toplevel(self.root)
            editor = DatabaseEditor(editor_window, self.db_path.get())
        except ImportError:
            messagebox.showerror("Hata", "DatabaseEditor modülü bulunamadı!")
        except Exception as e:
            messagebox.showerror("Hata", f"Editör açılamadı: {str(e)}")

    def _bert_retagging_thread(self):
        """Background thread for BERT re-tagging"""
        try:
            self.status_var.set("BERT modeli yükleniyor ve veritabanı güncelleniyor... (Lütfen bekleyin)")
            self.root.update()
            
            # Import here to avoid circular dependencies
            from update_db_with_bert import DatabaseUpdater
            
            updater = DatabaseUpdater(self.db_path.get())
            updater.update_all_sentences()
            updater.close()
            
            self.root.after(0, self._bert_retagging_complete)
            
        except Exception as e:
            self.root.after(0, self._bert_retagging_error, str(e))
            
    def _bert_retagging_complete(self):
        """Handle successful re-tagging"""
        self.status_var.set("BERT güncellemesi tamamlandı")
        messagebox.showinfo("Başarılı", "Veritabanı başarıyla BERT modeli ile güncellendi!")
        
    def _bert_retagging_error(self, error_msg):
        """Handle re-tagging error"""
        self.status_var.set("Güncelleme hatası")
        messagebox.showerror("Hata", f"Veritabanı güncellenemedi:\n{error_msg}")

    def _bert_retagging_error(self, error_msg):
        """Handle re-tagging error"""
        self.status_var.set("Güncelleme hatası")
        messagebox.showerror("Hata", f"Veritabanı güncellenemedi:\n{error_msg}")

    def setup_visualization_section(self, parent):
        """Setup visualization section"""
        # Configure grid
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        
        # Control Panel
        control_frame = ttk.Frame(parent)
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(control_frame, text="Grafik Türü:").pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(control_frame, text="En Sık Kelimeler (Bar)", 
                  command=self.show_bar_chart).pack(side=tk.LEFT, padx=5)
                  
        ttk.Button(control_frame, text="POS Dağılımı (Pie)", 
                  command=self.show_pie_chart).pack(side=tk.LEFT, padx=5)
                  
        ttk.Button(control_frame, text="Kelime Bulutu", 
                  command=self.show_word_cloud).pack(side=tk.LEFT, padx=5)
        
        # Plot Area
        plot_frame = ttk.Frame(parent, relief=tk.SUNKEN, borderwidth=1)
        plot_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Initialize Visualizer
        try:
            from gui.visualizer import CorpusVisualizer
            self.visualizer = CorpusVisualizer(plot_frame)
        except ImportError as e:
            ttk.Label(plot_frame, text=f"Görselleştirme modülü yüklenemedi:\n{e}", 
                     foreground="red").pack(expand=True)
            self.visualizer = None

    def show_bar_chart(self):
        """Show bar chart of top words"""
        if not self._check_db_ready(): return
        if not self.visualizer: return
        
        try:
            query = CorpusQuery(self.db_path.get())
            # Get top 20 words
            data = query.frequency_list(limit=20)
            query.close()
            
            if not data:
                messagebox.showinfo("Bilgi", "Gösterilecek veri bulunamadı.")
                return
                
            self.visualizer.plot_bar_chart(data)
            self.status_var.set("Sütun grafiği oluşturuldu")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Grafik oluşturulamadı: {e}")

    def show_pie_chart(self):
        """Show pie chart of POS distribution"""
        if not self._check_db_ready(): return
        if not self.visualizer: return
        
        try:
            query = CorpusQuery(self.db_path.get())
            # Get POS distribution
            data = query.get_pos_distribution()
            query.close()
            
            if not data:
                messagebox.showinfo("Bilgi", "Gösterilecek veri bulunamadı.")
                return
                
            self.visualizer.plot_pie_chart(data)
            self.status_var.set("Pasta grafiği oluşturuldu")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Grafik oluşturulamadı: {e}")

    def show_word_cloud(self):
        """Show word cloud"""
        if not self._check_db_ready(): return
        if not self.visualizer: return
        
        try:
            query = CorpusQuery(self.db_path.get())
            # Get top 100 words for word cloud
            data = query.frequency_list(limit=100)
            query.close()
            
            if not data:
                messagebox.showinfo("Bilgi", "Gösterilecek veri bulunamadı.")
                return
                
            self.visualizer.plot_word_cloud(data)
            self.status_var.set("Kelime bulutu oluşturuldu")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Grafik oluşturulamadı: {e}")

    def _check_db_ready(self):
        """Check if database is selected"""
        if not self.db_path.get():
            messagebox.showwarning("Uyarı", "Lütfen önce veritabanı dosyasını seçin!")
            return False
        return True

    def setup_analysis_section(self, parent):
        """Setup analysis section"""

        # Configure grid weights
        parent.columnconfigure(1, weight=1)

        # Analysis type selection
        ttk.Label(parent, text="Analiz Türü:").grid(row=0, column=0, sticky=tk.W)
        analysis_combo = ttk.Combobox(parent, textvariable=self.analysis_type,
                                     values=["kwic", "frequency", "collocation", "word_sketch", "cql"], state="readonly")
        analysis_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 5))

        # Search term (for KWIC, collocation)
        ttk.Label(parent, text="Aranacak Kelime / CQL:").grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        ttk.Entry(parent, textvariable=self.search_term, width=20).grid(row=0, column=3, sticky=tk.W, padx=(10, 5))

        # Window size
        ttk.Label(parent, text="Pencere Boyutu:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        ttk.Spinbox(parent, from_=1, to=20, textvariable=self.window_size, width=10).grid(row=1, column=1, sticky=tk.W, padx=(10, 5), pady=(10, 0))

        # Analysis button
        ttk.Button(parent, text="Analiz Yap", command=self.run_analysis).grid(row=1, column=2, columnspan=2, pady=(10, 0))

        # Stats button
        ttk.Button(parent, text="İstatistikler", command=self.show_stats).grid(row=2, column=0, columnspan=4, pady=(10, 0))
        
    def _run_cql_analysis(self, query):
        """Run CQL analysis"""
        if not self.search_term.get():
            messagebox.showwarning("Uyarı", "Lütfen CQL sorgusunu girin! Örn: [pos='NOUN'] [lemma='git']")
            return
            
        self.status_var.set("CQL araması yapılıyor...")
        
        try:
            results = query.cql_search(
                query_string=self.search_term.get(),
                limit=100
            )
            
            # Display results (CQL results are KWIC-like)
            self.display_results("CQL Arama Sonuçları", results, "kwic")
            
        except Exception as e:
            messagebox.showerror("Hata", f"CQL hatası: {e}")

    def setup_realtime_analysis_section(self, parent):
        """Setup real-time NLP analysis section for all backends"""
        
        # Real-time Analysis frame
        analysis_frame = ttk.LabelFrame(parent, text="Real-time NLP Analizi (Tüm Backendler)", padding="10")
        analysis_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        analysis_frame.columnconfigure(1, weight=1)
        
        # Backend selection for real-time analysis
        ttk.Label(analysis_frame, text="NLP Backend:").grid(row=0, column=0, sticky=tk.W)
        self.realtime_backend_var = tk.StringVar(value="custom_bert")
        backend_combo = ttk.Combobox(analysis_frame, textvariable=self.realtime_backend_var,
                                    values=["custom_bert", "stanza", "spacy", "simple"], state="readonly")
        backend_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 5))
        
        # Word selection
        ttk.Label(analysis_frame, text="Kelime Seç:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.selected_word = tk.StringVar()
        word_entry = ttk.Entry(analysis_frame, textvariable=self.selected_word, width=30)
        word_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=(10, 0))
        
        # Load words button
        ttk.Button(analysis_frame, text="Veritabanından Kelimeleri Yükle", 
                  command=self.load_words_from_db).grid(row=1, column=2, padx=(5, 0), pady=(10, 0))
        
        # Word list (for selection)
        ttk.Label(analysis_frame, text="Veya Kelime Listesi:").grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        
        # Word listbox with scrollbar
        word_frame = ttk.Frame(analysis_frame)
        word_frame.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        word_frame.columnconfigure(0, weight=1)
        
        self.word_listbox = tk.Listbox(word_frame, height=4)
        self.word_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        word_scrollbar = ttk.Scrollbar(word_frame, orient="vertical", command=self.word_listbox.yview)
        word_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.word_listbox.config(yscrollcommand=word_scrollbar.set)
        
        # Bind double-click event
        self.word_listbox.bind('<Double-1>', self.on_word_select)
        
        # Test text input
        ttk.Label(analysis_frame, text="Test Metni:").grid(row=3, column=0, sticky=tk.W, pady=(10, 0))
        self.test_text = tk.StringVar()
        test_entry = ttk.Entry(analysis_frame, textvariable=self.test_text, width=50)
        test_entry.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=(10, 0), pady=(10, 0))
        
        # Process button
        ttk.Button(analysis_frame, text="NLP ile Analiz Et", 
                  command=self.process_with_nlp).grid(row=4, column=0, sticky=tk.W, pady=(10, 0))
        
        # Clear results button
        ttk.Button(analysis_frame, text="Temizle", 
                  command=self.clear_realtime_results).grid(row=4, column=1, sticky=tk.W, padx=(10, 0), pady=(10, 0))
        
        # Results display
        ttk.Label(analysis_frame, text="NLP Sonuçları:").grid(row=5, column=0, sticky=tk.W, pady=(10, 0))
        
        self.realtime_results_text = scrolledtext.ScrolledText(analysis_frame, height=8, wrap=tk.WORD)
        self.realtime_results_text.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))
        analysis_frame.rowconfigure(6, weight=1)
        
    def setup_results_section(self, parent):
        """Setup results display section"""
        
        # Results frame
        results_frame = ttk.LabelFrame(parent, text="Sonuçlar", padding="10")
        results_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        parent.rowconfigure(6, weight=1)
        
        # Results text area with scrollbar
        self.results_text = scrolledtext.ScrolledText(results_frame, height=15, wrap=tk.WORD)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Clear results button
        ttk.Button(results_frame, text="Temizle", command=self.clear_results).grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        
        # Export button
        ttk.Button(results_frame, text="Sonuçları Kaydet", command=self.export_results).grid(row=1, column=0, sticky=tk.E, pady=(10, 0))

    def browse_database(self):
        """Browse for database file"""
        filename = filedialog.asksaveasfilename(
            title="Veritabanı Dosyası Seç",
            defaultextension=".db",
            filetypes=[("SQLite DB", "*.db"), ("All files", "*.*")]
        )
        if filename:
            self.db_path.set(filename)
            
    def browse_corpus_dir(self):
        """Browse for corpus directory"""
        directory = filedialog.askdirectory(title="Metin Klasörü Seç")
        if directory:
            self.corpus_dir.set(directory)
            
    def create_database(self):
        """Create new database"""
        try:
            self.status_var.set("Veritabanı oluşturuluyor...")
            self.root.update()
            
            db = CorpusDatabase(self.db_path.get())
            db.connect()
            db.create_schema()
            db.close()
            
            self.status_var.set("Veritabanı başarıyla oluşturuldu")
            messagebox.showinfo("Başarılı", "Veritabanı başarıyla oluşturuldu!")
            
        except Exception as e:
            self.status_var.set("Hata oluştu")
            messagebox.showerror("Hata", f"Veritabanı oluşturulamadı: {str(e)}")
            
    def ingest_corpus(self):
        """Ingest corpus in background thread"""
        if not self.corpus_dir.get():
            messagebox.showwarning("Uyarı", "Lütfen metin klasörünü seçin!")
            return
            
        if not self.db_path.get():
            messagebox.showwarning("Uyarı", "Lütfen veritabanı dosyasını belirtin!")
            return
            
        # Start ingestion in background
        thread = threading.Thread(target=self._ingest_corpus_thread)
        thread.daemon = True
        thread.start()
        
    def _ingest_corpus_thread(self):
        """Background corpus ingestion"""
        try:
            self.status_var.set("Corpus içeri aktarılıyor...")
            self.root.update()
            
            ingestor = CorpusIngestor(self.db_path.get(), nlp_backend=self.backend_var.get())
            stats = ingestor.ingest_directory(self.corpus_dir.get())
            ingestor.close()
            
            # Update UI in main thread
            self.root.after(0, self._ingestion_complete, stats)
            
        except Exception as e:
            self.root.after(0, self._ingestion_error, str(e))
            
    def _ingestion_complete(self, stats):
        """Handle successful ingestion"""
        self.status_var.set("Corpus içeri aktarımı tamamlandı")
        messagebox.showinfo("Başarılı", 
                           f"Corpus içeri aktarımı tamamlandı!\n"
                           f"Dosya: {stats['documents_processed']}\n"
                           f"Cümle: {stats['sentences_processed']}\n"
                           f"Token: {stats['tokens_processed']}")
        
    def _ingestion_error(self, error_msg):
        """Handle ingestion error"""
        self.status_var.set("Hata oluştu")
        messagebox.showerror("Hata", f"Corpus içeri aktarılamadı: {error_msg}")
        
    def run_analysis(self):
        """Run analysis based on selected type and corpus source"""
        try:
            # Always use database for now
            if not self.db_path.get():
                messagebox.showwarning("Uyarı", "Lütfen veritabanı dosyasını belirtin!")
                return
                
            query = CorpusQuery(self.db_path.get())
            
            if self.analysis_type.get() == "kwic":
                self._run_kwic_analysis(query)
            elif self.analysis_type.get() == "frequency":
                self._run_frequency_analysis(query)
            elif self.analysis_type.get() == "collocation":
                self._run_collocation_analysis(query)
            elif self.analysis_type.get() == "word_sketch":
                self._run_word_sketch_analysis(query)
            elif self.analysis_type.get() == "cql":
                self._run_cql_analysis(query)
            else:
                messagebox.showwarning("Uyarı", "Lütfen geçerli bir analiz türü seçin!")
                
            query.close()
            
        except Exception as e:
            messagebox.showerror("Hata", f"Analiz yapılamadı: {str(e)}")
            
    def _run_kwic_analysis(self, query):
        """Run KWIC analysis"""
        if not self.search_term.get():
            messagebox.showwarning("Uyarı", "Lütfen aranacak kelimeyi girin!")
            return
            
        self.status_var.set("KWIC analizi yapılıyor...")
        
        results = query.kwic_concordance(
            search_term=self.search_term.get(),
            window_size=self.window_size.get(),
            limit=100
        )
        
        # Display results
        self.display_results("KWIC Analizi", results, "kwic")
        
    def _run_frequency_analysis(self, query):
        """Run frequency analysis"""
        self.status_var.set("Frekans analizi yapılıyor...")
        
        results = query.frequency_list(
            word_type='norm',
            limit=100
        )
        
        self.display_results("Frekans Analizi", results, "frequency")
        
    def _run_collocation_analysis(self, query):
        """Run collocation analysis"""
        if not self.search_term.get():
            messagebox.showwarning("Uyarı", "Lütfen hedef kelimeyi girin!")
            return
            
        self.status_var.set("Collocation analizi yapılıyor...")
        
        results = query.collocation_analysis(
            target_word=self.search_term.get(),
            window_size=self.window_size.get(),
            measure='pmi',
            limit=50
        )
        
        self.display_results("Collocation Analizi", results, "collocation")
        
    def _run_word_sketch_analysis(self, query):
        """Run word sketch analysis"""
        if not self.search_term.get():
            messagebox.showwarning("Uyarı", "Lütfen lemma'yı girin!")
            return
            
        self.status_var.set("Word sketch analizi yapılıyor...")
        
        results = query.word_sketch(
            lemma=self.search_term.get(),
            limit=50
        )
        
        self.display_results("Word Sketch Analizi", results, "word_sketch")
        
    def _run_file_based_analysis(self):
        """Run analysis directly from files (real-time)"""
        if not self.source_path_var.get():
            messagebox.showwarning("Uyarı", "Lütfen kaynak yolunu belirtin!")
            return
            
        if not self.search_term.get():
            messagebox.showwarning("Uyarı", "Lütfen aranacak kelimeyi girin!")
            return
            
        self.status_var.set("Dosyalardan analiz yapılıyor...")
        
        try:
            from pathlib import Path
            import os
            
            source_path = Path(self.source_path_var.get())
            all_text = ""
            
            if source_path.is_dir():
                # Process all text files in directory
                for file_path in source_path.glob("*.txt"):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            all_text += f.read() + "\n"
                    except Exception as e:
                        print(f"Dosya okunamadı {file_path}: {e}")
            else:
                # Single file
                with open(source_path, 'r', encoding='utf-8') as f:
                    all_text = f.read()
            
            if not all_text.strip():
                messagebox.showwarning("Uyarı", "Dosyalarda metin bulunamadı!")
                return
                
            # Simple analysis based on type
            analysis_type = self.analysis_type.get()
            
            if analysis_type == "kwic":
                self._run_simple_kwic_analysis(all_text)
            elif analysis_type == "frequency":
                self._run_simple_frequency_analysis(all_text)
            elif analysis_type == "collocation":
                self._run_simple_collocation_analysis(all_text)
            else:
                messagebox.showwarning("Uyarı", "Bu analiz türü dosya tabanlı kaynaklar için desteklenmiyor!")
                
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya analizi yapılamadı: {str(e)}")
            
    def _run_mixed_analysis(self):
        """Run combined database + file analysis"""
        # For now, just run database analysis
        # Could be extended to combine results
        if not self.db_path.get():
            messagebox.showwarning("Uyarı", "Lütfen veritabanı dosyasını belirtin!")
            return
            
        query = CorpusQuery(self.db_path.get())
        
        if self.analysis_type.get() == "kwic":
            self._run_kwic_analysis(query)
        elif self.analysis_type.get() == "frequency":
            self._run_frequency_analysis(query)
        # Add other types as needed
        
        query.close()
        
    def _run_simple_kwic_analysis(self, text):
        """Simple KWIC analysis from text"""
        search_term = self.search_term.get().lower()
        lines = text.split('\n')
        results = []
        
        for line in lines:
            line_lower = line.lower()
            if search_term in line_lower:
                # Find position
                pos = line_lower.find(search_term)
                left_context = line[:pos].strip()
                right_context = line[pos + len(search_term):].strip()
                keyword = line[pos:pos + len(search_term)]
                
                results.append({
                    'left_context': left_context[-50:],  # Last 50 chars
                    'keyword': keyword,
                    'right_context': right_context[:50]  # First 50 chars
                })
        
        self.display_results("Dosya KWIC Analizi", results, "kwic")
        
    def _run_simple_frequency_analysis(self, text):
        """Simple frequency analysis from text"""
        import re
        from collections import Counter
        
        # Simple word tokenization
        words = re.findall(r'\b\w+\b', text.lower())
        word_counts = Counter(words)
        
        results = []
        for word, count in word_counts.most_common(100):
            results.append({
                'word': word,
                'frequency': count
            })
            
        self.display_results("Dosya Frekans Analizi", results, "frequency")
        
    def _run_simple_collocation_analysis(self, text):
        """Simple collocation analysis from text"""
        import re
        from collections import Counter
        
        search_term = self.search_term.get().lower()
        window_size = self.window_size.get()
        
        words = re.findall(r'\b\w+\b', text.lower())
        collocations = []
        
        for i, word in enumerate(words):
            if word == search_term:
                # Get window around the word
                start = max(0, i - window_size)
                end = min(len(words), i + window_size + 1)
                window_words = words[start:end]
                
                # Find collocations (words near the target)
                for j, w in enumerate(window_words):
                    if w != search_term and abs((start + j) - i) <= window_size:
                        collocations.append(w)
        
        collocation_counts = Counter(collocations)
        results = []
        
        for word, count in collocation_counts.most_common(50):
            results.append({
                'collocate': word,
                'co_occurrence_count': count,
                'score': count  # Simple score
            })
            
        self.display_results("Dosya Collocation Analizi", results, "collocation")
        
    def display_results(self, title, data, analysis_type):
        """Display analysis results"""
        from datetime import datetime
        
        self.results_text.delete(1.0, tk.END)
        
        # Store current analysis data for export
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.current_analysis_data = {
            'title': title,
            'data': data,
            'analysis_type': analysis_type,
            'timestamp': timestamp
        }
        
        # Title
        self.results_text.insert(tk.END, f"=== {title} ===\n")
        self.results_text.insert(tk.END, f"Analiz Zamanı: {timestamp}\n\n")
        
        if analysis_type == "kwic":
            self._display_kwic_results(data)
        elif analysis_type == "frequency":
            self._display_frequency_results(data)
        elif analysis_type == "collocation":
            self._display_collocation_results(data)
        elif analysis_type == "word_sketch":
            self._display_word_sketch_results(data)
            
        self.status_var.set(f"{title} tamamlandı")
        
    def _display_kwic_results(self, results):
        """Display KWIC results"""
        if not results:
            self.results_text.insert(tk.END, "Sonuç bulunamadı.\n")
            return
            
        for i, result in enumerate(results[:20], 1):  # Limit to 20 results
            line = f"{i:2d}. {result['left_context']} [[[{result['keyword']}]] {result['right_context']}\n"
            self.results_text.insert(tk.END, line)
            
        if len(results) > 20:
            self.results_text.insert(tk.END, f"\n... ve {len(results) - 20} sonuç daha\n")
            
    def _display_frequency_results(self, results):
        """Display frequency results"""
        if not results:
            self.results_text.insert(tk.END, "Sonuç bulunamadı.\n")
            return
            
        self.results_text.insert(tk.END, "Kelime              Frekans\n")
        self.results_text.insert(tk.END, "-" * 35 + "\n")
        
        for item in results[:50]:  # Limit to 50 results
            line = f"{item['word']:<20} {item['frequency']:>8}\n"
            self.results_text.insert(tk.END, line)
            
    def _display_collocation_results(self, results):
        """Display collocation results"""
        if not results:
            self.results_text.insert(tk.END, "Sonuç bulunamadı.\n")
            return
            
        self.results_text.insert(tk.END, "Collocate           Co-occ   PMI Score\n")
        self.results_text.insert(tk.END, "-" * 45 + "\n")
        
        for item in results[:30]:  # Limit to 30 results
            line = f"{item['collocate']:<20} {item['co_occurrence_count']:>7} {item['score']:>8.3f}\n"
            self.results_text.insert(tk.END, line)
            
    def _display_word_sketch_results(self, results):
        """Display word sketch results"""
        if not results:
            self.results_text.insert(tk.END, "Sonuç bulunamadı.\n")
            return
            
        for relation, words in results.items():
            if words:
                self.results_text.insert(tk.END, f"\n=== {relation.upper()} ===\n")
                for word_info in words[:10]:  # Limit to 10 per relation
                    line = f"  {word_info['related_word']} ({word_info['frequency']} kez)\n"
                    self.results_text.insert(tk.END, line)
                    
    def show_stats(self):
        """Show database statistics"""
        try:
            query = CorpusQuery(self.db_path.get())
            stats = query.get_processing_stats()
            query.close()
            
            # Create stats window
            stats_window = tk.Toplevel(self.root)
            stats_window.title("Veritabanı İstatistikleri")
            stats_window.geometry("500x400")
            
            stats_text = scrolledtext.ScrolledText(stats_window, wrap=tk.WORD)
            stats_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Display stats
            stats_text.insert(tk.END, "=== VERİTABANI İSTATİSTİKLERİ ===\n\n")
            stats_text.insert(tk.END, f"Toplam Belge: {stats['database_stats']['total_documents']}\n")
            stats_text.insert(tk.END, f"Toplam Cümle: {stats['database_stats']['total_sentences']}\n")
            stats_text.insert(tk.END, f"Toplam Token: {stats['database_stats']['total_tokens']}\n")
            stats_text.insert(tk.END, f"Benzersiz Kelime: {stats['database_stats']['unique_words']}\n")
            
            if 'processing_stats' in stats:
                stats_text.insert(tk.END, f"\nİşlenen Dosya: {stats['processing_stats']['documents_processed']}\n")
                stats_text.insert(tk.END, f"Hatalar: {stats['processing_stats']['errors']}\n")
                
            stats_text.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Hata", f"İstatistikler alınamadı: {str(e)}")
            
    def clear_results(self):
        """Clear results area"""
        self.results_text.delete(1.0, tk.END)
        self.status_var.set("Hazır")
        
    def load_words_from_db(self):
        """Load words from database for selection"""
        try:
            if not self.db_path.get():
                messagebox.showwarning("Uyarı", "Önce veritabanı dosyasını seçin!")
                return
                
            self.status_var.set("Veritabanından kelimeler yükleniyor...")
            
            query = CorpusQuery(self.db_path.get())
            
            # Get frequency list to populate word list
            results = query.frequency_list(word_type='norm', limit=100)
            query.close()
            
            # Clear existing items
            self.word_listbox.delete(0, tk.END)
            
            # Add words to listbox
            for item in results:
                word = item['word']
                freq = item['frequency']
                display_text = f"{word} ({freq})"
                self.word_listbox.insert(tk.END, display_text)
            
            self.status_var.set(f"{len(results)} kelime yüklendi")
            
        except Exception as e:
            self.status_var.set("Hata oluştu")
            messagebox.showerror("Hata", f"Kelimeler yüklenemedi: {str(e)}")
    
    def on_word_select(self, event):
        """Handle word selection from listbox"""
        selection = self.word_listbox.curselection()
        if selection:
            selected_item = self.word_listbox.get(selection[0])
            # Extract word from "word (frequency)" format
            word = selected_item.split(' (')[0]
            self.selected_word.set(word)
            
            # Also set test text to demonstrate usage
            self.test_text.set(f"{word} kelimesi ile bir test cümlesi oluşturuyoruz.")
    
    def process_with_nlp(self):
        """Process text with selected NLP backend"""
        try:
            # Get text to process
            text_to_process = self.test_text.get().strip()
            if not text_to_process:
                # Use selected word if no test text
                selected_word = self.selected_word.get().strip()
                if not selected_word:
                    messagebox.showwarning("Uyarı", "Lütfen bir kelime seçin veya test metni girin!")
                    return
                text_to_process = f"{selected_word} kelimesi ile bir test cümlesi oluşturuyoruz."
            
            # Ensure proper UTF-8 encoding
            text_to_process = self._ensure_utf8_text(text_to_process)
            
            backend = self.realtime_backend_var.get()
            self.status_var.set(f"{backend.upper()} analizi yapılıyor...")
            self.root.update()
            
            # Create NLP processor based on selected backend
            from nlp.turkish_processor import TurkishNLPProcessor
            processor = TurkishNLPProcessor(backend=backend)
            
            # Process text
            tokens = processor.process_text(text_to_process)
            
            # Display results
            self.display_realtime_results(text_to_process, tokens, backend)
            
            self.status_var.set(f"{backend.upper()} analizi tamamlandı")
            
        except Exception as e:
            self.status_var.set("Hata oluştu")
            error_msg = f"NLP analizi yapılamadı: {str(e)}"
            
            # Check for common issues
            if "No module named" in str(e):
                backend_name = self.realtime_backend_var.get()
                if backend_name == "stanza":
                    error_msg = "Stanza kütüphanesi bulunamadı!\n\nKurulum:\npip install stanza"
                elif backend_name == "spacy":
                    error_msg = "SpaCy kütüphanesi bulunamadı!\n\nKurulum:\npip install spacy"
                elif backend_name == "custom_bert":
                    error_msg = "Transformers kütüphanesi bulunamadı!\n\nKurulum:\npip install transformers torch"
            
            messagebox.showerror("Hata", error_msg)
    
    def display_realtime_results(self, text, tokens, backend):
        """Display real-time NLP analysis results"""
        self.realtime_results_text.delete(1.0, tk.END)
        
        # Header
        self.realtime_results_text.insert(tk.END, f"=== {backend.upper()} ANALİZİ ===\n")
        self.realtime_results_text.insert(tk.END, f"Metin: {text}\n\n")
        
        if not tokens:
            self.realtime_results_text.insert(tk.END, "Sonuç bulunamadı.\n")
            return
        
        # Backend info
        backend_names = {
            "custom_bert": "BERT (Hugging Face)",
            "stanza": "Stanza",
            "spacy": "SpaCy",
            "simple": "Basit Tokenizasyon"
        }
        backend_display = backend_names.get(backend, backend.upper())
        self.realtime_results_text.insert(tk.END, f"Backend: {backend_display}\n\n")
        
        # Display tokens
        self.realtime_results_text.insert(tk.END, "Token Analizi:\n")
        for i, token in enumerate(tokens, 1):
            if isinstance(token, dict):
                # Structured token (BERT, Stanza, SpaCy)
                word = token.get('word', token.get('text', 'N/A'))
                pos_en = token.get('pos', token.get('upos', 'N/A'))
                pos_tr = token.get('upos_tr', 'N/A')  # Turkish POS tag
                confidence = token.get('confidence', token.get('score', 'N/A'))
                
                if backend == "custom_bert" and 'entity' in token:
                    # BERT specific format
                    entity = token.get('entity', 'N/A')
                    score = token.get('score', 'N/A')
                    self.realtime_results_text.insert(tk.END, f"  {i}. {word} -> {entity} (conf: {score:.3f})\n")
                else:
                    # Standard format with bilingual POS tags
                    conf_str = f" (conf: {confidence:.3f})" if isinstance(confidence, (int, float)) else ""
                    if pos_tr != 'N/A':
                        pos_display = f"POS: {pos_en}/{pos_tr}"
                    else:
                        pos_display = f"POS: {pos_en}"
                    self.realtime_results_text.insert(tk.END, f"  {i}. {word} -> {pos_display}{conf_str}\n")
            else:
                # Simple string token
                self.realtime_results_text.insert(tk.END, f"  {i}. {token}\n")
        
        # Summary
        self.realtime_results_text.insert(tk.END, f"\nToplam Token: {len(tokens)}\n")
    
    def clear_realtime_results(self):
        """Clear real-time analysis results"""
        self.realtime_results_text.delete(1.0, tk.END)
        self.selected_word.set("")
        self.test_text.set("")
        
    def browse_database(self):
        """Browse for database file"""
        filename = filedialog.asksaveasfilename(
            title="Veritabanı Dosyası Seç",
            defaultextension=".db",
            filetypes=[("SQLite DB", "*.db"), ("All files", "*.*")]
        )
        if filename:
            self.db_path.set(filename)
            
    def browse_corpus_dir(self):
        """Browse for corpus directory"""
        dirname = filedialog.askdirectory(title="Corpus Klasörü Seç")
        if dirname:
            self.corpus_dir.set(dirname)
            
    def browse_corpus_source(self):
        """Browse for corpus source (file or directory)"""
        source_type = self.corpus_source_var.get()
        
        if source_type == "database":
            # Browse for database file
            filename = filedialog.askopenfilename(
                title="Veritabanı Dosyası Seç",
                filetypes=[("SQLite DB", "*.db"), ("All files", "*.*")]
            )
            if filename:
                self.source_path_var.set(filename)
        elif source_type == "files":
            # Browse for directory containing text files
            dirname = filedialog.askdirectory(title="Metin Dosyaları Klasörü Seç")
            if dirname:
                self.source_path_var.set(dirname)
        else:  # mixed
            # Browse for directory
            dirname = filedialog.askdirectory(title="Karma Kaynak Klasörü Seç")
            if dirname:
                self.source_path_var.set(dirname)
        
    def export_results(self):
        """Export results to file in various formats"""
        if not hasattr(self, 'current_analysis_data') or not self.current_analysis_data:
            messagebox.showwarning("Uyarı", "Kaydedilecek analiz sonucu yok! Önce analiz yapın.")
            return
            
        # Format selection dialog
        format_dialog = tk.Toplevel(self.root)
        format_dialog.title("Dışa Aktarma Formatı Seçin")
        format_dialog.geometry("400x200")
        format_dialog.resizable(False, False)
        
        ttk.Label(format_dialog, text="Analiz sonuçlarını hangi formatta kaydetmek istiyorsunuz?",
                 font=("Arial", 10)).pack(pady=10)
        
        format_var = tk.StringVar(value="txt")
        
        # Format options
        formats_frame = ttk.Frame(format_dialog)
        formats_frame.pack(pady=10)
        
        ttk.Radiobutton(formats_frame, text="TXT (Metin)", variable=format_var, value="txt").pack(anchor=tk.W)
        ttk.Radiobutton(formats_frame, text="JSON (Yapısal Veri)", variable=format_var, value="json").pack(anchor=tk.W)
        ttk.Radiobutton(formats_frame, text="XML (Web Standardı)", variable=format_var, value="xml").pack(anchor=tk.W)
        ttk.Radiobutton(formats_frame, text="Veritabanı (SQLite)", variable=format_var, value="db").pack(anchor=tk.W)
        
        def confirm_format():
            selected_format = format_var.get()
            format_dialog.destroy()
            
            if selected_format == "txt":
                self._export_as_txt()
            elif selected_format == "json":
                self._export_as_json()
            elif selected_format == "xml":
                self._export_as_xml()
            elif selected_format == "db":
                self._export_to_database()
        
        ttk.Button(format_dialog, text="Devam", command=confirm_format).pack(pady=10)
    
    def _export_as_txt(self):
        """Export results as plain text"""
        content = self.results_text.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("Uyarı", "Kaydedilecek sonuç yok!")
            return
            
        filename = filedialog.asksaveasfilename(
            title="Sonuçları TXT Olarak Kaydet",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Başarılı", f"Sonuçlar TXT olarak {filename} dosyasına kaydedildi!")
            except Exception as e:
                messagebox.showerror("Hata", f"Dosya kaydedilemedi: {str(e)}")
    
    def _export_as_json(self):
        """Export results as JSON"""
        if not hasattr(self, 'current_analysis_data'):
            messagebox.showwarning("Uyarı", "Kaydedilecek analiz sonucu yok!")
            return
            
        filename = filedialog.asksaveasfilename(
            title="Sonuçları JSON Olarak Kaydet",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                # Prepare JSON data
                json_data = {
                    'analysis_title': self.current_analysis_data['title'],
                    'analysis_type': self.current_analysis_data['analysis_type'],
                    'timestamp': self.current_analysis_data.get('timestamp', ''),
                    'results': self.current_analysis_data['data']
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
                    
                messagebox.showinfo("Başarılı", f"Sonuçlar JSON olarak {filename} dosyasına kaydedildi!")
            except Exception as e:
                messagebox.showerror("Hata", f"JSON dosyası kaydedilemedi: {str(e)}")
    
    def _export_as_xml(self):
        """Export results as XML"""
        if not hasattr(self, 'current_analysis_data'):
            messagebox.showwarning("Uyarı", "Kaydedilecek analiz sonucu yok!")
            return
            
        filename = filedialog.asksaveasfilename(
            title="Sonuçları XML Olarak Kaydet",
            defaultextension=".xml",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                # Create XML structure
                xml_content = self._create_xml_content()
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(xml_content)
                    
                messagebox.showinfo("Başarılı", f"Sonuçlar XML olarak {filename} dosyasına kaydedildi!")
            except Exception as e:
                messagebox.showerror("Hata", f"XML dosyası kaydedilemedi: {str(e)}")
    
    def _export_to_database(self):
        """Export results to a new database table"""
        if not hasattr(self, 'current_analysis_data'):
            messagebox.showwarning("Uyarı", "Kaydedilecek analiz sonucu yok!")
            return
            
        # Database selection dialog
        db_dialog = tk.Toplevel(self.root)
        db_dialog.title("Veritabanı Seçimi")
        db_dialog.geometry("400x150")
        
        ttk.Label(db_dialog, text="Analiz sonuçlarını hangi veritabanına kaydetmek istiyorsunuz?",
                 font=("Arial", 10)).pack(pady=10)
        
        db_path_var = tk.StringVar()
        
        # Database path entry
        path_frame = ttk.Frame(db_dialog)
        path_frame.pack(pady=5)
        
        ttk.Entry(path_frame, textvariable=db_path_var, width=40).pack(side=tk.LEFT)
        ttk.Button(path_frame, text="Gözat", command=lambda: self._browse_db_file(db_path_var)).pack(side=tk.LEFT, padx=(5,0))
        
        def save_to_db():
            db_path = db_path_var.get().strip()
            if not db_path:
                messagebox.showwarning("Uyarı", "Lütfen veritabanı dosyasını belirtin!")
                return
                
            db_dialog.destroy()
            self._save_analysis_to_db(db_path)
        
        ttk.Button(db_dialog, text="Kaydet", command=save_to_db).pack(pady=10)
    
    def _create_xml_content(self):
        """Create XML content from analysis data"""
        data = self.current_analysis_data
        analysis_type = data['analysis_type']
        
        xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml_lines.append(f'<analysis title="{data["title"]}" type="{analysis_type}">')
        
        if analysis_type == "kwic":
            xml_lines.append('  <kwic_results>')
            for i, result in enumerate(data['data'][:50], 1):
                xml_lines.append(f'    <result id="{i}">')
                xml_lines.append(f'      <left_context>{result["left_context"]}</left_context>')
                xml_lines.append(f'      <keyword>{result["keyword"]}</keyword>')
                xml_lines.append(f'      <right_context>{result["right_context"]}</right_context>')
                xml_lines.append('    </result>')
            xml_lines.append('  </kwic_results>')
            
        elif analysis_type == "frequency":
            xml_lines.append('  <frequency_results>')
            for item in data['data'][:100]:
                xml_lines.append('    <word>')
                xml_lines.append(f'      <text>{item["word"]}</text>')
                xml_lines.append(f'      <frequency>{item["frequency"]}</frequency>')
                xml_lines.append('    </word>')
            xml_lines.append('  </frequency_results>')
            
        elif analysis_type == "collocation":
            xml_lines.append('  <collocation_results>')
            for item in data['data'][:50]:
                xml_lines.append('    <collocate>')
                xml_lines.append(f'      <word>{item["collocate"]}</word>')
                xml_lines.append(f'      <co_occurrence>{item["co_occurrence_count"]}</co_occurrence>')
                xml_lines.append(f'      <pmi_score>{item["score"]:.3f}</pmi_score>')
                xml_lines.append('    </collocate>')
            xml_lines.append('  </collocation_results>')
            
        elif analysis_type == "word_sketch":
            xml_lines.append('  <word_sketch_results>')
            for relation, words in data['data'].items():
                if words:
                    xml_lines.append(f'    <relation type="{relation}">')
                    for word_info in words[:20]:
                        xml_lines.append('      <related_word>')
                        xml_lines.append(f'        <word>{word_info["related_word"]}</word>')
                        xml_lines.append(f'        <frequency>{word_info["frequency"]}</frequency>')
                        xml_lines.append('      </related_word>')
                    xml_lines.append('    </relation>')
            xml_lines.append('  </word_sketch_results>')
        
        xml_lines.append('</analysis>')
        return '\n'.join(xml_lines)
    
    def _browse_db_file(self, path_var):
        """Browse for database file"""
        filename = filedialog.asksaveasfilename(
            title="Veritabanı Dosyası Seç",
            defaultextension=".db",
            filetypes=[("SQLite Database", "*.db"), ("All files", "*.*")]
        )
        if filename:
            path_var.set(filename)
    
    def _save_analysis_to_db(self, db_path):
        """Save analysis results to database"""
        try:
            import sqlite3
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create table based on analysis type
            analysis_type = self.current_analysis_data['analysis_type']
            table_name = f"analysis_{analysis_type}"
            
            if analysis_type == "kwic":
                cursor.execute(f'''
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        id INTEGER PRIMARY KEY,
                        left_context TEXT,
                        keyword TEXT,
                        right_context TEXT
                    )
                ''')
                
                for result in self.current_analysis_data['data'][:100]:
                    cursor.execute(f'''
                        INSERT INTO {table_name} (left_context, keyword, right_context)
                        VALUES (?, ?, ?)
                    ''', (result['left_context'], result['keyword'], result['right_context']))
                    
            elif analysis_type == "frequency":
                cursor.execute(f'''
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        id INTEGER PRIMARY KEY,
                        word TEXT,
                        frequency INTEGER
                    )
                ''')
                
                for item in self.current_analysis_data['data'][:200]:
                    cursor.execute(f'''
                        INSERT INTO {table_name} (word, frequency)
                        VALUES (?, ?)
                    ''', (item['word'], item['frequency']))
                    
            elif analysis_type == "collocation":
                cursor.execute(f'''
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        id INTEGER PRIMARY KEY,
                        collocate TEXT,
                        co_occurrence INTEGER,
                        pmi_score REAL
                    )
                ''')
                
                for item in self.current_analysis_data['data'][:100]:
                    cursor.execute(f'''
                        INSERT INTO {table_name} (collocate, co_occurrence, pmi_score)
                        VALUES (?, ?, ?)
                    ''', (item['collocate'], item['co_occurrence_count'], item['score']))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Başarılı", f"Analiz sonuçları {db_path} veritabanına kaydedildi!")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Veritabanına kaydedilemedi: {str(e)}")

    # Corpus Editor Functions
    def load_corpus_file(self):
        """Load a corpus file for editing"""
        filename = filedialog.askopenfilename(
            title="Corpus Dosyası Aç",
            filetypes=[("Text files", "*.txt"), ("JSON files", "*.json"), ("XML files", "*.xml"), ("All files", "*.*")]
        )

        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()

                self.editor_text.delete(1.0, tk.END)
                self.editor_text.insert(tk.END, content)

                self.current_file_path = filename
                self.current_file_var.set(filename)
                self.original_content = content
                self.editor_status_var.set("Dosya başarıyla yüklendi")

            except Exception as e:
                messagebox.showerror("Hata", f"Dosya yüklenemedi: {str(e)}")

    def save_corpus_file(self):
        """Save the current corpus file"""
        if not self.current_file_path:
            self.save_corpus_file_as()
            return

        try:
            content = self.editor_text.get(1.0, tk.END).rstrip()
            with open(self.current_file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            self.original_content = content
            self.editor_status_var.set("Dosya kaydedildi")
            messagebox.showinfo("Başarılı", "Dosya başarıyla kaydedildi!")

        except Exception as e:
            messagebox.showerror("Hata", f"Dosya kaydedilemedi: {str(e)}")

    def save_corpus_file_as(self):
        """Save the corpus file with a new name"""
        filename = filedialog.asksaveasfilename(
            title="Corpus Dosyası Farklı Kaydet",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("JSON files", "*.json"), ("XML files", "*.xml"), ("All files", "*.*")]
        )

        if filename:
            try:
                content = self.editor_text.get(1.0, tk.END).rstrip()
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)

                self.current_file_path = filename
                self.current_file_var.set(filename)
                self.original_content = content
                self.editor_status_var.set("Dosya farklı kaydedildi")
                messagebox.showinfo("Başarılı", f"Dosya {filename} olarak kaydedildi!")

            except Exception as e:
                messagebox.showerror("Hata", f"Dosya kaydedilemedi: {str(e)}")

    def new_corpus_file(self):
        """Create a new corpus file"""
        # Check if current file has unsaved changes
        if self._has_unsaved_changes():
            result = messagebox.askyesnocancel("Kaydedilmemiş Değişiklikler",
                                             "Mevcut dosyada kaydedilmemiş değişiklikler var. Kaydetmek istiyor musunuz?")
            if result is None:  # Cancel
                return
            elif result:  # Yes
                self.save_corpus_file()

        # Clear editor
        self.editor_text.delete(1.0, tk.END)
        self.current_file_path = None
        self.current_file_var.set("Yeni dosya")
        self.original_content = ""
        self.editor_status_var.set("Yeni dosya oluşturuldu")

    def _has_unsaved_changes(self):
        """Check if there are unsaved changes"""
        if self.current_file_path is None:
            current_content = self.editor_text.get(1.0, tk.END).rstrip()
            return len(current_content) > 0
        else:
            current_content = self.editor_text.get(1.0, tk.END).rstrip()
            return current_content != self.original_content

    def update_database_from_editor(self):
        """Update database with the edited content from the editor"""
        if not self.db_path.get():
            messagebox.showwarning("Uyarı", "Lütfen önce veritabanı dosyasını belirtin!")
            return

        content = self.editor_text.get(1.0, tk.END).rstrip()
        if not content.strip():
            messagebox.showwarning("Uyarı", "Düzenleyicide metin yok!")
            return

        # Ask for confirmation
        result = messagebox.askyesno("Veritabanını Güncelle",
                                   "Düzenlenmiş metin NLP işlenip veritabanına kaydedilecek. Devam edilsin mi?")
        if not result:
            return

        # Start update in background thread
        thread = threading.Thread(target=self._update_database_thread, args=(content,))
        thread.daemon = True
        thread.start()

    def _update_database_thread(self, content):
        """Background database update"""
        try:
            self.status_var.set("Veritabanı güncelleniyor...")
            self.root.update()

            # Create temporary file for ingestion
            import tempfile
            import os

            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(content)
                temp_file_path = f.name

            try:
                # Ingest the single file
                ingestor = CorpusIngestor(self.db_path.get(), nlp_backend=self.backend_var.get())
                stats = ingestor.ingest_directory(os.path.dirname(temp_file_path),
                                                file_patterns=[os.path.basename(temp_file_path)],
                                                max_files=1)
                ingestor.close()

                # Update UI in main thread
                self.root.after(0, self._database_update_complete, stats)

            finally:
                # Clean up temporary file
                os.unlink(temp_file_path)

        except Exception as e:
            self.root.after(0, self._database_update_error, str(e))

    def _database_update_complete(self, stats):
        """Handle successful database update"""
        self.status_var.set("Veritabanı güncellendi")
        messagebox.showinfo("Başarılı",
                           f"Veritabanı güncellendi!\n"
                           f"İşlenen doküman: {stats['documents_processed']}\n"
                           f"İşlenen token: {stats['tokens_processed']}")

    def _database_update_error(self, error_msg):
        """Handle database update error"""
        self.status_var.set("Güncelleme hatası")
        messagebox.showerror("Hata", f"Veritabanı güncellenemedi: {error_msg}")

def main():
    """Main function to run the GUI"""
    root = tk.Tk()
    app = CorpusGUI(root)
    
    # Center window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()