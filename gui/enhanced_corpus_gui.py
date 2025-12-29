#!/usr/bin/env python3
"""
Enhanced Corpus Data Manipulator - GUI Application with Model Mapping

Tkinter tabanlı kullanıcı arayüzü ile Corpus Data Manipulator'ı GUI üzerinden kullanma
+ Model Mapping entegrasyonu

Özellikler:
- Klasör seçme ve corpus içeri aktarma
- KWIC arama
- Frekans analizi
- Collocation analizi
- Word sketch
- Model Mapping (YENİ!)
- BERT analizleri
- Sonuçları görüntüleme ve dışa aktarma

Kullanım:
    py enhanced_corpus_gui.py
"""

# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import sys
import os
from pathlib import Path
import threading
import json
import logging

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

# Add project root directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from database.schema import CorpusDatabase
from nlp.turkish_processor import TurkishNLPProcessor
from ingestion.corpus_ingestor import CorpusIngestor
from query.corpus_query import CorpusQuery
from model_mapper import TurkishModelMapper
from model_bert_mapper import BERTModelMapper
from model_integration import CorpusModelIntegration

class EnhancedCorpusGUI:
    """Enhanced GUI application with Model Mapping capabilities"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Corpus Data Manipulator - Model Mapping")
        self.root.geometry("1400x900")
        
        # Variables
        self.db_path = tk.StringVar(value="corpus.db")
        self.csv_path = tk.StringVar(value="Cleaned-for-tags.csv")
        self.corpus_dir = tk.StringVar()
        self.search_term = tk.StringVar()
        self.window_size = tk.IntVar(value=5)
        self.analysis_type = tk.StringVar(value="kwic")
        
        # Model Mapping variables
        self.model_type = tk.StringVar(value="traditional")
        self.output_dir = tk.StringVar(value="model_outputs")
        self.include_bert = tk.BooleanVar(value=True)
        self.include_traditional = tk.BooleanVar(value=True)
        self.test_size = tk.DoubleVar(value=0.2)
        self.bert_model_name = tk.StringVar(value="dbmdz/bert-base-turkish-128k-cased")
        
        # Components
        self.setup_ui()
        
        # Status
        self.status_var = tk.StringVar(value="Hazır")
        self.setup_status_bar()
    
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
        """Setup the enhanced user interface"""
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Enhanced Corpus Data Manipulator", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 20))
        
        # Create notebook for different sections
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure notebook tabs
        self.setup_database_tab()
        self.setup_ingestion_tab()
        self.setup_analysis_tab()
        self.setup_bert_analysis_tab()
        self.setup_model_mapping_tab()
        self.setup_results_tab()
        
        # Configure main frame weights
        main_frame.rowconfigure(1, weight=1)
        
    def setup_database_tab(self):
        """Setup database configuration tab"""
        db_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(db_frame, text="Veritabanı")
        
        # Database path
        ttk.Label(db_frame, text="Veritabanı Dosyası:").grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        ttk.Entry(db_frame, textvariable=self.db_path, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=(0, 10))
        ttk.Button(db_frame, text="Gözat", command=self.browse_database).grid(row=0, column=2, pady=(0, 10))
        
        # Create database button
        ttk.Button(db_frame, text="Veritabanı Oluştur", command=self.create_database).grid(row=1, column=0, columnspan=3, pady=(10, 0))
        
        # Database info
        self.db_info_text = scrolledtext.ScrolledText(db_frame, height=10, wrap=tk.WORD)
        self.db_info_text.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        db_frame.columnconfigure(1, weight=1)
        db_frame.rowconfigure(2, weight=1)
        
        # Stats button
        ttk.Button(db_frame, text="Veritabanı İstatistikleri", command=self.show_db_stats).grid(row=3, column=0, columnspan=3, pady=(10, 0))
        
    def setup_ingestion_tab(self):
        """Setup corpus ingestion tab"""
        ingest_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(ingest_frame, text="Corpus İçeri Aktarma")
        
        # Corpus directory
        ttk.Label(ingest_frame, text="Metin Klasörü:").grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        ttk.Entry(ingest_frame, textvariable=self.corpus_dir, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=(0, 10))
        ttk.Button(ingest_frame, text="Gözat", command=self.browse_corpus_dir).grid(row=0, column=2, pady=(0, 10))
        
        # NLP Backend selection
        ttk.Label(ingest_frame, text="NLP Backend:").grid(row=1, column=0, sticky=tk.W, pady=(5, 10))
        self.backend_var = tk.StringVar(value="custom_bert")
        backend_combo = ttk.Combobox(ingest_frame, textvariable=self.backend_var, 
                                    values=["custom_bert", "stanza", "spacy", "simple"], state="readonly")
        backend_combo.grid(row=1, column=1, sticky=tk.W, padx=(10, 5), pady=(5, 10))
        
        # File formats info
        ttk.Label(ingest_frame, text="Desteklenen Formatlar:", font=("Arial", 8, "italic")).grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        ttk.Label(ingest_frame, text="TXT, JSON, XML dosyaları", font=("Arial", 8)).grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=(0, 5))
        
        # Ingest button
        ttk.Button(ingest_frame, text="Corpus'u İçeri Aktar", command=self.ingest_corpus).grid(row=3, column=0, columnspan=3, pady=(10, 0))
        
        # Progress bar
        self.ingest_progress = ttk.Progressbar(ingest_frame, orient="horizontal", length=300, mode="determinate")
        self.ingest_progress.grid(row=4, column=0, columnspan=3, pady=(10, 0))
        
        # Ingestion log
        self.ingest_log = scrolledtext.ScrolledText(ingest_frame, height=8, wrap=tk.WORD)
        self.ingest_log.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        ingest_frame.columnconfigure(1, weight=1)
        ingest_frame.rowconfigure(5, weight=1)
        
    def setup_analysis_tab(self):
        """Setup analysis tab"""
        analysis_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(analysis_frame, text="Analiz")
        
        # Analysis type selection
        ttk.Label(analysis_frame, text="Analiz Türü:").grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        analysis_combo = ttk.Combobox(analysis_frame, textvariable=self.analysis_type,
                                     values=["kwic", "frequency", "collocation", "word_sketch", "ngram", "keywords", "cql_search"], state="readonly")
        analysis_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 5), pady=(0, 10))
        
        # Search term (for KWIC, collocation)
        ttk.Label(analysis_frame, text="Aranacak Kelime:").grid(row=0, column=2, sticky=tk.W, padx=(20, 0), pady=(0, 10))
        ttk.Entry(analysis_frame, textvariable=self.search_term, width=20).grid(row=0, column=3, sticky=tk.W, padx=(10, 5), pady=(0, 10))
        
        # Window size
        ttk.Label(analysis_frame, text="Pencere Boyutu:").grid(row=1, column=0, sticky=tk.W, pady=(5, 10))
        ttk.Spinbox(analysis_frame, from_=1, to=20, textvariable=self.window_size, width=10).grid(row=1, column=1, sticky=tk.W, padx=(10, 5), pady=(5, 10))
        
        # Analysis button
        ttk.Button(analysis_frame, text="Analiz Yap", command=self.run_analysis).grid(row=1, column=2, columnspan=2, pady=(5, 10))
        
        # Analysis results
        self.analysis_results = scrolledtext.ScrolledText(analysis_frame, height=20, wrap=tk.WORD)
        self.analysis_results.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        analysis_frame.columnconfigure(1, weight=1)
        analysis_frame.columnconfigure(3, weight=1)
        analysis_frame.rowconfigure(2, weight=1)
        
        # Export button
        ttk.Button(analysis_frame, text="Sonuçları Dışa Aktar", command=self.export_analysis_results).grid(row=3, column=0, columnspan=4, pady=(10, 0))
        
    def setup_bert_analysis_tab(self):
        """Setup BERT analysis tab"""
        bert_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(bert_frame, text="BERT Analizi")
        
        # BERT Model Selection (New)
        ttk.Label(bert_frame, text="BERT Model Yolu:").grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        self.bert_analysis_model_path = tk.StringVar()
        ttk.Entry(bert_frame, textvariable=self.bert_analysis_model_path, width=40).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=(0, 10))
        ttk.Button(bert_frame, text="Model Seç", command=self.browse_bert_model).grid(row=0, column=2, padx=(5, 0), pady=(0, 10))

        # Word selection
        ttk.Label(bert_frame, text="Kelime Seç:").grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        self.selected_word = tk.StringVar()
        word_entry = ttk.Entry(bert_frame, textvariable=self.selected_word, width=30)
        word_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=(0, 10))
        
        # Load words button
        ttk.Button(bert_frame, text="Veritabanından Kelimeleri Yükle", 
                  command=self.load_words_from_db).grid(row=1, column=2, padx=(5, 0), pady=(0, 10))
        
        # Word list
        ttk.Label(bert_frame, text="Kelimeler Listesi:").grid(row=2, column=0, sticky=tk.W, pady=(5, 10))
        
        word_frame = ttk.Frame(bert_frame)
        word_frame.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 10))
        word_frame.columnconfigure(0, weight=1)
        
        self.word_listbox = tk.Listbox(word_frame, height=6)
        self.word_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        word_scrollbar = ttk.Scrollbar(word_frame, orient="vertical", command=self.word_listbox.yview)
        word_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.word_listbox.config(yscrollcommand=word_scrollbar.set)
        
        # Bind double-click event
        self.word_listbox.bind('<Double-1>', self.on_word_select)
        
        # Test text input
        ttk.Label(bert_frame, text="Test Metni:").grid(row=3, column=0, sticky=tk.W, pady=(10, 10))
        self.test_text = tk.StringVar()
        test_entry = ttk.Entry(bert_frame, textvariable=self.test_text, width=50)
        test_entry.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=(10, 0), pady=(10, 10))
        
        # BERT Process button
        ttk.Button(bert_frame, text="BERT ile Analiz Et", 
                  command=self.process_with_bert).grid(row=4, column=0, sticky=tk.W, pady=(10, 10))
        
        # Clear BERT results button
        ttk.Button(bert_frame, text="Temizle", 
                  command=self.clear_bert_results).grid(row=4, column=1, sticky=tk.W, padx=(10, 0), pady=(10, 10))
        
        # BERT Results display
        ttk.Label(bert_frame, text="BERT Sonuçları:").grid(row=5, column=0, sticky=tk.W, pady=(10, 10))
        
        self.bert_results_text = scrolledtext.ScrolledText(bert_frame, height=12, wrap=tk.WORD)
        self.bert_results_text.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 10))
        bert_frame.columnconfigure(1, weight=1)
        bert_frame.rowconfigure(6, weight=1)
        
        # Export BERT results
        ttk.Button(bert_frame, text="BERT Sonuçlarını Dışa Aktar", 
                  command=self.export_bert_results).grid(row=7, column=0, columnspan=3, pady=(10, 0))
        
    def setup_model_mapping_tab(self):
        """Setup model mapping tab"""
        model_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(model_frame, text="Model Mapping")
        
        # Model type selection
        ttk.Label(model_frame, text="Model Türü:").grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        model_combo = ttk.Combobox(model_frame, textvariable=self.model_type,
                                  values=["traditional", "bert", "both", "full_pipeline"], state="readonly")
        model_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 5), pady=(0, 10))
        
        # CSV path
        ttk.Label(model_frame, text="CSV Dosyası (Etiketler):").grid(row=1, column=0, sticky=tk.W, pady=(5, 10))
        ttk.Entry(model_frame, textvariable=self.csv_path, width=40).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=(5, 10))
        ttk.Button(model_frame, text="Gözat", command=self.browse_csv).grid(row=1, column=2, pady=(5, 10))
        
        # Output directory
        ttk.Label(model_frame, text="Çıktı Dizini:").grid(row=2, column=0, sticky=tk.W, pady=(5, 10))
        ttk.Entry(model_frame, textvariable=self.output_dir, width=40).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=(5, 10))
        ttk.Button(model_frame, text="Gözat", command=self.browse_output_dir).grid(row=2, column=2, pady=(5, 10))
        
        # Traditional ML options
        traditional_frame = ttk.LabelFrame(model_frame, text="Traditional ML Options", padding="5")
        traditional_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 10))
        
        ttk.Checkbutton(traditional_frame, text="Traditional ML Dahil", variable=self.include_traditional).grid(row=0, column=0, sticky=tk.W)
        ttk.Label(traditional_frame, text="Test Set Boyutu:").grid(row=0, column=1, sticky=tk.W, padx=(20, 5))
        ttk.Spinbox(traditional_frame, from_=0.1, to=0.5, increment=0.1, textvariable=self.test_size, width=5).grid(row=0, column=2, sticky=tk.W)
        
        # BERT options
        bert_options_frame = ttk.LabelFrame(model_frame, text="BERT Options", padding="5")
        bert_options_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 10))
        
        ttk.Checkbutton(bert_options_frame, text="BERT Model Dahil", variable=self.include_bert).grid(row=0, column=0, sticky=tk.W)
        ttk.Label(bert_options_frame, text="BERT Model:").grid(row=0, column=1, sticky=tk.W, padx=(20, 5))
        ttk.Entry(bert_options_frame, textvariable=self.bert_model_name, width=30).grid(row=0, column=2, sticky=tk.W, padx=(10, 5))
        
        # Model mapping button
        ttk.Button(model_frame, text="Model Mapping Başlat", 
                  command=self.run_model_mapping).grid(row=5, column=0, columnspan=3, pady=(20, 10))
        
        # Progress bar
        self.model_progress = ttk.Progressbar(model_frame, orient="horizontal", length=400, mode="determinate")
        self.model_progress.grid(row=6, column=0, columnspan=3, pady=(10, 10))
        
        # Model mapping log
        self.model_log = scrolledtext.ScrolledText(model_frame, height=12, wrap=tk.WORD)
        self.model_log.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 10))
        model_frame.columnconfigure(1, weight=1)
        model_frame.rowconfigure(7, weight=1)
        
        # Export model results
        ttk.Button(model_frame, text="Model Sonuçlarını Dışa Aktar", 
                  command=self.export_model_results).grid(row=8, column=0, columnspan=3, pady=(10, 0))
        
    def setup_results_tab(self):
        """Setup results tab"""
        results_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(results_frame, text="Genel Sonuçlar")
        
        # Combined results display
        self.combined_results = scrolledtext.ScrolledText(results_frame, height=25, wrap=tk.WORD)
        self.combined_results.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Clear and export buttons
        button_frame = ttk.Frame(results_frame)
        button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(button_frame, text="Tüm Sonuçları Temizle", command=self.clear_all_results).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="Tüm Sonuçları Dışa Aktar", command=self.export_all_results).grid(row=0, column=1)
        
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
    def setup_status_bar(self):
        """Setup status bar"""
        status_frame = ttk.Frame(self.root)
        status_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        status_frame.columnconfigure(0, weight=1)
        
        self.status_bar = ttk.Label(status_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
    def browse_database(self):
        """Browse for database file"""
        filename = filedialog.asksaveasfilename(
            title="Veritabanı Dosyası Seç",
            defaultextension=".db",
            filetypes=[("SQLite DB", "*.db"), ("All files", "*.*")]
        )
        if filename:
            self.db_path.set(filename)

    def browse_csv(self):
        """Browse for CSV file"""
        filename = filedialog.askopenfilename(
            title="CSV Dosyası Seç",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.csv_path.set(filename)

    def browse_bert_model(self):
        """Browse for BERT model directory"""
        directory = filedialog.askdirectory(title="BERT Model Klasörü Seç")
        if directory:
            self.bert_analysis_model_path.set(directory)
            
    def browse_corpus_dir(self):
        """Browse for corpus directory"""
        directory = filedialog.askdirectory(title="Metin Klasörü Seç")
        if directory:
            self.corpus_dir.set(directory)
            
    def browse_output_dir(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(title="Çıktı Dizini Seç")
        if directory:
            self.output_dir.set(directory)
            
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
            self.ingest_progress['value'] = 0
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
        self.ingest_progress['value'] = 100
        
        # Log results
        log_text = f"Corpus içeri aktarımı tamamlandı!\n"
        log_text += f"Dosya: {stats['documents_processed']}\n"
        log_text += f"Cümle: {stats['sentences_processed']}\n"
        log_text += f"Token: {stats['tokens_processed']}\n"
        log_text += f"Hatalar: {stats['errors']}\n"
        
        self.ingest_log.insert(tk.END, log_text)
        self.ingest_log.see(tk.END)
        
        messagebox.showinfo("Başarılı", log_text)
        
    def _ingestion_error(self, error_msg):
        """Handle ingestion error"""
        self.status_var.set("Hata oluştu")
        self.ingest_progress['value'] = 0
        messagebox.showerror("Hata", f"Corpus içeri aktarılamadı: {error_msg}")
        
    def run_analysis(self):
        """Run analysis based on selected type"""
        try:
            query = CorpusQuery(self.db_path.get())
            
            if self.analysis_type.get() == "kwic":
                self._run_kwic_analysis(query)
            elif self.analysis_type.get() == "frequency":
                self._run_frequency_analysis(query)
            elif self.analysis_type.get() == "collocation":
                self._run_collocation_analysis(query)
            elif self.analysis_type.get() == "word_sketch":
                self._run_word_sketch_analysis(query)
            elif self.analysis_type.get() == "ngram":
                self._run_ngram_analysis(query)
            elif self.analysis_type.get() == "keywords":
                self._run_keywords_analysis(query)
            elif self.analysis_type.get() == "cql_search":
                self._run_cql_search(query)
                
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
        self.display_analysis_results("KWIC Analizi", results, "kwic")
        
    def _run_frequency_analysis(self, query):
        """Run frequency analysis"""
        self.status_var.set("Frekans analizi yapılıyor...")
        
        results = query.frequency_list(
            word_type='norm',
            limit=100
        )
        
        self.display_analysis_results("Frekans Analizi", results, "frequency")
        
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
        
        self.display_analysis_results("Collocation Analizi", results, "collocation")
        
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
        
        self.display_analysis_results("Word Sketch Analizi", results, "word_sketch")

    def _run_ngram_analysis(self, query):
        """Run N-Gram analysis"""
        self.status_var.set("N-Gram analizi yapılıyor...")
        
        # Use window size as N
        n = self.window_size.get()
        if n < 2: n = 2
        
        results = query.generate_ngrams(
            n=n,
            min_freq=2,
            limit=100
        )
        
        self.display_analysis_results(f"{n}-Gram Analizi", results, "ngram")

    def _run_keywords_analysis(self, query):
        """Run Keywords analysis"""
        self.status_var.set("Anahtar Kelime analizi yapılıyor...")
        
        results = query.calculate_keywords(limit=100)
        
        self.display_analysis_results("Anahtar Kelimeler (Keyness)", results, "keywords")

    def _run_cql_search(self, query):
        """Run CQL search"""
        if not self.search_term.get():
            messagebox.showwarning("Uyarı", "Lütfen CQL sorgusunu girin! (Örn: [pos=\"NOUN\"])")
            return
            
        self.status_var.set("CQL araması yapılıyor...")
        
        results = query.cql_search(
            cql_query=self.search_term.get(),
            limit=100
        )
        
        self.display_analysis_results("CQL Arama Sonuçları", results, "cql_search")
        
    def display_analysis_results(self, title, data, analysis_type):
        """Display analysis results"""
        self.analysis_results.delete(1.0, tk.END)
        
        # Title
        self.analysis_results.insert(tk.END, f"=== {title} ===\n\n")
        
        if analysis_type == "kwic":
            self._display_kwic_results(data)
        elif analysis_type == "frequency":
            self._display_frequency_results(data)
        elif analysis_type == "collocation":
            self._display_collocation_results(data)
        elif analysis_type == "word_sketch":
            self._display_word_sketch_results(data)
        elif analysis_type == "ngram":
            self._display_ngram_results(data)
        elif analysis_type == "keywords":
            self._display_keywords_results(data)
        elif analysis_type == "cql_search":
            self._display_cql_results(data)
            
        self.status_var.set(f"{title} tamamlandı")

    def _display_ngram_results(self, results):
        """Display N-Gram results"""
        if not results:
            self.analysis_results.insert(tk.END, "Sonuç bulunamadı.\n")
            return
            
        self.analysis_results.insert(tk.END, "N-Gram              Frekans\n")
        self.analysis_results.insert(tk.END, "-" * 35 + "\n")
        
        for item in results:
            line = f"{item['ngram']:<25} {item['frequency']:>8}\n"
            self.analysis_results.insert(tk.END, line)

    def _display_keywords_results(self, results):
        """Display Keywords results"""
        if not results:
            self.analysis_results.insert(tk.END, "Sonuç bulunamadı.\n")
            return
            
        self.analysis_results.insert(tk.END, f"{'Kelime':<20} {'Keyness':<10} {'Frekans':<8} {'Ref.Frek':<8}\n")
        self.analysis_results.insert(tk.END, "-" * 55 + "\n")
        
        for item in results:
            # Score format
            score = item['score']
            score_str = f"{score:.1f}" if score < 1000 else f"{score:.0f}"
            
            line = f"{item['word']:<20} {score_str:>10} {item['freq_target']:>8} {item['freq_ref']:>8}\n"
            self.analysis_results.insert(tk.END, line)

    def _display_cql_results(self, results):
        """Display CQL search results"""
        if not results:
            self.analysis_results.insert(tk.END, "Sonuç bulunamadı.\n")
            return
            
        self.analysis_results.insert(tk.END, f"Toplam {len(results)} sonuç bulundu.\n\n")
        
        for i, result in enumerate(results, 1):
            self.analysis_results.insert(tk.END, f"{i}. MATCH: [{result['match']}]\n")
            self.analysis_results.insert(tk.END, f"   CONTEXT: {result['context']}\n\n")
        
    def _display_kwic_results(self, results):
        """Display KWIC results"""
        if not results:
            self.analysis_results.insert(tk.END, "Sonuç bulunamadı.\n")
            return
            
        for i, result in enumerate(results[:20], 1):  # Limit to 20 results
            line = f"{i:2d}. {result['left_context']} [[[{result['keyword']}]] {result['right_context']}\n"
            self.analysis_results.insert(tk.END, line)
            
        if len(results) > 20:
            self.analysis_results.insert(tk.END, f"\n... ve {len(results) - 20} sonuç daha\n")
            
    def _display_frequency_results(self, results):
        """Display frequency results"""
        if not results:
            self.analysis_results.insert(tk.END, "Sonuç bulunamadı.\n")
            return
            
        self.analysis_results.insert(tk.END, "Kelime              Frekans\n")
        self.analysis_results.insert(tk.END, "-" * 35 + "\n")
        
        for item in results[:50]:  # Limit to 50 results
            line = f"{item['word']:<20} {item['frequency']:>8}\n"
            self.analysis_results.insert(tk.END, line)
            
    def _display_collocation_results(self, results):
        """Display collocation results"""
        if not results:
            self.analysis_results.insert(tk.END, "Sonuç bulunamadı.\n")
            return
            
        self.analysis_results.insert(tk.END, "Collocate           Co-occ   PMI Score\n")
        self.analysis_results.insert(tk.END, "-" * 45 + "\n")
        
        for item in results[:30]:  # Limit to 30 results
            line = f"{item['collocate']:<20} {item['co_occurrence_count']:>7} {item['score']:>8.3f}\n"
            self.analysis_results.insert(tk.END, line)
            
    def _display_word_sketch_results(self, results):
        """Display word sketch results"""
        if not results:
            self.analysis_results.insert(tk.END, "Sonuç bulunamadı.\n")
            return
            
        for relation, words in results.items():
            if words:
                self.analysis_results.insert(tk.END, f"\n=== {relation.upper()} ===\n")
                for word_info in words[:10]:  # Limit to 10 per relation
                    line = f"  {word_info['related_word']} ({word_info['frequency']} kez)\n"
                    self.analysis_results.insert(tk.END, line)
                    
    def show_db_stats(self):
        """Show database statistics"""
        try:
            query = CorpusQuery(self.db_path.get())
            stats = query.get_processing_stats()
            query.close()
            
            # Display in database tab
            self.db_info_text.delete(1.0, tk.END)
            self.db_info_text.insert(tk.END, "=== VERİTABANI İSTATİSTİKLERİ ===\n\n")
            self.db_info_text.insert(tk.END, f"Toplam Belge: {stats['database_stats']['total_documents']}\n")
            self.db_info_text.insert(tk.END, f"Toplam Cümle: {stats['database_stats']['total_sentences']}\n")
            self.db_info_text.insert(tk.END, f"Toplam Token: {stats['database_stats']['total_tokens']}\n")
            self.db_info_text.insert(tk.END, f"Benzersiz Kelime: {stats['database_stats']['unique_words']}\n")
            
            if 'processing_stats' in stats:
                self.db_info_text.insert(tk.END, f"\nİşlenen Dosya: {stats['processing_stats']['documents_processed']}\n")
                self.db_info_text.insert(tk.END, f"Hatalar: {stats['processing_stats']['errors']}\n")
                
        except Exception as e:
            messagebox.showerror("Hata", f"İstatistikler alınamadı: {str(e)}")
            
    def clear_all_results(self):
        """Clear all results"""
        self.analysis_results.delete(1.0, tk.END)
        self.bert_results_text.delete(1.0, tk.END)
        self.model_log.delete(1.0, tk.END)
        self.combined_results.delete(1.0, tk.END)
        self.ingest_log.delete(1.0, tk.END)
        self.db_info_text.delete(1.0, tk.END)
        self.status_var.set("Hazır")
        
    def export_analysis_results(self):
        """Export analysis results"""
        content = self.analysis_results.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("Uyarı", "Kaydedilecek sonuç yok!")
            return
            
        filename = filedialog.asksaveasfilename(
            title="Analiz Sonuçlarını Kaydet",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Başarılı", f"Analiz sonuçları {filename} dosyasına kaydedildi!")
            except Exception as e:
                messagebox.showerror("Hata", f"Dosya kaydedilemedi: {str(e)}")
                
    def export_bert_results(self):
        """Export BERT results"""
        content = self.bert_results_text.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("Uyarı", "Kaydedilecek BERT sonucu yok!")
            return
            
        filename = filedialog.asksaveasfilename(
            title="BERT Sonuçlarını Kaydet",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Başarılı", f"BERT sonuçları {filename} dosyasına kaydedildi!")
            except Exception as e:
                messagebox.showerror("Hata", f"Dosya kaydedilemedi: {str(e)}")
                
    def export_model_results(self):
        """Export model mapping results"""
        content = self.model_log.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("Uyarı", "Kaydedilecek model sonucu yok!")
            return
            
        filename = filedialog.asksaveasfilename(
            title="Model Sonuçlarını Kaydet",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Başarılı", f"Model sonuçları {filename} dosyasına kaydedildi!")
            except Exception as e:
                messagebox.showerror("Hata", f"Dosya kaydedilemedi: {str(e)}")
                
    def export_all_results(self):
        """Export all results"""
        content = ""
        
        # Add analysis results
        content += "=== ANALİZ SONUÇLARI ===\n\n"
        content += self.analysis_results.get(1.0, tk.END) + "\n\n"
        
        # Add BERT results
        content += "=== BERT SONUÇLARI ===\n\n"
        content += self.bert_results_text.get(1.0, tk.END) + "\n\n"
        
        # Add model results
        content += "=== MODEL SONUÇLARI ===\n\n"
        content += self.model_log.get(1.0, tk.END) + "\n\n"
        
        if not content.strip():
            messagebox.showwarning("Uyarı", "Kaydedilecek sonuç yok!")
            return
            
        filename = filedialog.asksaveasfilename(
            title="Tüm Sonuçları Kaydet",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Başarılı", f"Tüm sonuçlar {filename} dosyasına kaydedildi!")
            except Exception as e:
                messagebox.showerror("Hata", f"Dosya kaydedilemedi: {str(e)}")
                
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
    
    def process_with_bert(self):
        """Process text with BERT model"""
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
            
            # Ensure proper UTF-8 encoding for BERT processing
            text_to_process = self._ensure_utf8_text(text_to_process)
            
            self.status_var.set("BERT analizi yapılıyor...")
            self.root.update()
            
            # Check if transformers is available
            try:
                import transformers
            except ImportError:
                self.status_var.set("Transformers kütüphanesi bulunamadı")
                error_msg = (
                    "BERT analizi için transformers kütüphanesi gereklidir.\n\n"
                    "Kurulum için şu komutu çalıştırın:\n"
                    "pip install transformers torch\n\n"
                    "Veya requirements.txt kullanın:\n"
                    "pip install -r requirements.txt"
                )
                messagebox.showerror("Eksik Kütüphane", error_msg)
                return
            
            # Create BERT processor
            from nlp.custom_bert_processor import create_custom_bert_processor
            
            # Get selected model path
            model_path = self.bert_analysis_model_path.get().strip() or None
            
            bert_processor = create_custom_bert_processor(model_path=model_path)
            
            # Check if model is loaded
            if not bert_processor.is_loaded:
                self.status_var.set("BERT modeli yüklenemedi")
                error_msg = (
                    "BERT modeli yüklenemedi.\n\n"
                    "Olası nedenler:\n"
                    "- İnternet bağlantısı yok\n"
                    "- Model indirme hatası\n"
                    "- Yetersiz disk alanı\n\n"
                    "Lütfen bağlantınızı kontrol edin ve tekrar deneyin."
                )
                messagebox.showwarning("Model Yükleme Hatası", error_msg)
                return
            
            # Process text
            tokens = bert_processor.process_text(text_to_process)
            
            # Display results
            self.display_bert_results(text_to_process, tokens)
            
            self.status_var.set("BERT analizi tamamlandı")
            
        except Exception as e:
            self.status_var.set("Hata oluştu")
            error_msg = f"BERT analizi yapılamadı: {str(e)}"
            
            # Check for common issues
            if "No module named 'transformers'" in str(e):
                error_msg = (
                    "Transformers kütüphanesi bulunamadı!\n\n"
                    "Kurulum:\n"
                    "pip install transformers torch"
                )
            elif "No module named 'torch'" in str(e):
                error_msg = (
                    "PyTorch kütüphanesi bulunamadı!\n\n"
                    "Kurulum:\n"
                    "pip install torch"
                )
            
            messagebox.showerror("Hata", error_msg)
    
    def display_bert_results(self, text, tokens):
        """Display BERT analysis results"""
        self.bert_results_text.delete(1.0, tk.END)
        
        # Header
        self.bert_results_text.insert(tk.END, f"=== BERT ANALİZİ ===\n")
        self.bert_results_text.insert(tk.END, f"Metin: {text}\n\n")
        
        if not tokens:
            self.bert_results_text.insert(tk.END, "Sonuç bulunamadı.\n")
            return
        
        # Model info
        try:
            from nlp.custom_bert_processor import create_custom_bert_processor
            bert_processor = create_custom_bert_processor()
            info = bert_processor.get_model_info()
            self.bert_results_text.insert(tk.END, f"Model: {info['model_path']}\n")
            self.bert_results_text.insert(tk.END, f"Yüklendi: {'Evet' if info['is_loaded'] else 'Hayır'}\n\n")
        except:
            pass
        
        # Token analysis
        self.bert_results_text.insert(tk.END, "TOKİN ANALİZİ:\n")
        self.bert_results_text.insert(tk.END, "-" * 80 + "\n")
        self.bert_results_text.insert(tk.END, f"{'No':<3} {'Kelime':<12} {'POS':<8} {'Lemma':<12} {'Morph':<20} {'Güven':<8}\n")
        self.bert_results_text.insert(tk.END, "-" * 80 + "\n")
        
        for i, token in enumerate(tokens, 1):
            word = token['form']
            pos = token['upos'] or 'N/A'
            lemma = token['lemma'] or 'N/A'
            morph = token['morph'] or 'N/A'
            confidence = token.get('bert_confidence', 'N/A')
            
            if isinstance(confidence, (int, float)):
                confidence_str = f"{confidence:.3f}"
            else:
                confidence_str = str(confidence)
            
            # Truncate long morph strings
            if len(morph) > 18:
                morph = morph[:15] + "..."
            
            line = f"{i:<3} {word:<12} {pos:<8} {lemma:<12} {morph:<20} {confidence_str:<8}\n"
            self.bert_results_text.insert(tk.END, line)
        
        # Summary statistics
        self.bert_results_text.insert(tk.END, "\n" + "-" * 80 + "\n")
        self.bert_results_text.insert(tk.END, f"Toplam Token: {len(tokens)}\n")
        
        # POS distribution
        pos_count = {}
        confidence_scores = []
        
        for token in tokens:
            pos = token['upos'] or 'N/A'
            pos_count[pos] = pos_count.get(pos, 0) + 1
            
            confidence = token.get('bert_confidence')
            if isinstance(confidence, (int, float)):
                confidence_scores.append(confidence)
        
        if pos_count:
            self.bert_results_text.insert(tk.END, "\nPOS DAĞILIMI:\n")
            for pos, count in sorted(pos_count.items()):
                self.bert_results_text.insert(tk.END, f"  {pos}: {count}\n")
        
        if confidence_scores:
            avg_confidence = sum(confidence_scores) / len(confidence_scores)
            min_confidence = min(confidence_scores)
            max_confidence = max(confidence_scores)
            
            self.bert_results_text.insert(tk.END, f"\nGÜVEN SKORLARI:\n")
            self.bert_results_text.insert(tk.END, f"  Ortalama: {avg_confidence:.3f}\n")
            self.bert_results_text.insert(tk.END, f"  Minimum: {min_confidence:.3f}\n")
            self.bert_results_text.insert(tk.END, f"  Maksimum: {max_confidence:.3f}\n")
    
    def clear_bert_results(self):
        """Clear BERT results"""
        self.bert_results_text.delete(1.0, tk.END)
        self.selected_word.set("")
        self.test_text.set("")
        
    def run_model_mapping(self):
        """Run model mapping based on selected type"""
        try:
            if self.model_type.get() == "traditional":
                self._run_traditional_mapping()
            elif self.model_type.get() == "bert":
                self._run_bert_mapping()
            elif self.model_type.get() == "both":
                self._run_both_mapping()
            elif self.model_type.get() == "full_pipeline":
                self._run_full_pipeline()
                
        except Exception as e:
            self.status_var.set("Hata oluştu")
            messagebox.showerror("Hata", f"Model mapping yapılamadı: {str(e)}")
            
    def _run_traditional_mapping(self):
        """Run traditional ML model mapping"""
        self.status_var.set("Traditional ML model mapping yapılıyor...")
        self.model_progress['value'] = 0
        self.root.update()
        
        try:
            mapper = TurkishModelMapper(self.csv_path.get(), self.db_path.get())
            
            if not mapper.load_data():
                raise Exception("Veri yüklenemedi")
                
            mapper.build_vocabulary()
            dataset = mapper.create_training_dataset(test_size=self.test_size.get())
            
            # Export datasets
            mapper.export_to_sklearn(f"{self.output_dir.get()}/sklearn_features.pkl")
            mapper.export_to_pytorch(dataset, f"{self.output_dir.get()}/pytorch_dataset")
            mapper.export_to_tensorflow(dataset, f"{self.output_dir.get()}/tensorflow_dataset")
            mapper.save_mappings(f"{self.output_dir.get()}/vocabulary_mappings.json")
            
            # Log results
            log_text = f"Traditional ML Model Mapping Tamamlandı!\n"
            log_text += f"Vocabulary size: {mapper.vocabulary_size}\n"
            log_text += f"Tagset size: {mapper.tagset_size}\n"
            log_text += f"Train sequences: {len(dataset['train']['sequences'])}\n"
            log_text += f"Validation sequences: {len(dataset['validation']['sequences'])}\n"
            log_text += f"Test sequences: {len(dataset['test']['sequences'])}\n"
            log_text += f"Çıktı dizini: {self.output_dir.get()}\n"
            
            self.model_log.insert(tk.END, log_text)
            self.model_log.see(tk.END)
            self.model_progress['value'] = 100
            self.status_var.set("Traditional ML model mapping tamamlandı")
            
        except Exception as e:
            self.model_log.insert(tk.END, f"Hata: {str(e)}\n")
            self.model_progress['value'] = 0
            
    def _run_bert_mapping(self):
        """Run BERT model mapping"""
        self.status_var.set("BERT model mapping yapılıyor...")
        self.model_progress['value'] = 0
        self.root.update()
        
        try:
            bert_mapper = BERTModelMapper(
                self.csv_path.get(),
                self.bert_model_name.get(),
                max_seq_length=128
            )
            
            if not bert_mapper.load_data():
                raise Exception("Veri yüklenemedi")
                
            splits = bert_mapper.create_bert_training_splits(
                test_size=self.test_size.get(),
                val_size=0.1
            )
            
            if not splits:
                raise Exception("BERT splits oluşturulamadı")
            
            # Export datasets
            bert_mapper.export_for_huggingface(splits, f"{self.output_dir.get()}/huggingface_bert")
            bert_mapper.export_for_pytorch_lightning(splits, f"{self.output_dir.get()}/pytorch_lightning_bert")
            bert_mapper.create_bert_config(f"{self.output_dir.get()}/bert_config.json")
            
            # Log results
            stats = bert_mapper.get_bert_statistics()
            log_text = f"BERT Model Mapping Tamamlandı!\n"
            log_text += f"Model: {stats['bert_stats']['model_name']}\n"
            log_text += f"Vocab size: {stats['bert_stats']['vocab_size']}\n"
            log_text += f"Total tokens: {stats['basic_stats']['total_tokens']}\n"
            log_text += f"Total subwords: {stats['basic_stats']['total_subwords']}\n"
            log_text += f"Train sequences: {splits['train']['input_ids'].shape[0]}\n"
            log_text += f"Validation sequences: {splits['validation']['input_ids'].shape[0]}\n"
            log_text += f"Test sequences: {splits['test']['input_ids'].shape[0]}\n"
            log_text += f"Çıktı dizini: {self.output_dir.get()}\n"
            
            self.model_log.insert(tk.END, log_text)
            self.model_log.see(tk.END)
            self.model_progress['value'] = 100
            self.status_var.set("BERT model mapping tamamlandı")
            
        except Exception as e:
            self.model_log.insert(tk.END, f"Hata: {str(e)}\n")
            self.model_progress['value'] = 0
            
    def _run_both_mapping(self):
        """Run both traditional and BERT mapping"""
        self.status_var.set("Hem traditional hem BERT model mapping yapılıyor...")
        self.model_progress['value'] = 0
        self.root.update()
        
        try:
            # Run traditional mapping
            self._run_traditional_mapping()
            
            # Add separator
            self.model_log.insert(tk.END, "\n" + "="*50 + "\n")
            
            # Run BERT mapping
            self._run_bert_mapping()
            
            self.status_var.set("Hem traditional hem BERT model mapping tamamlandı")
            
        except Exception as e:
            self.model_log.insert(tk.END, f"Hata: {str(e)}\n")
            
    def _run_full_pipeline(self):
        """Run complete integration pipeline"""
        self.status_var.set("Tam entegrasyon pipeline'ı çalışıyor...")
        self.model_progress['value'] = 0
        self.root.update()
        
        try:
            integration = CorpusModelIntegration(
                self.csv_path.get(),
                self.db_path.get(),
                self.output_dir.get()
            )
            
            results = integration.run_full_pipeline(
                include_bert=self.include_bert.get(),
                include_traditional=self.include_traditional.get(),
                test_size=self.test_size.get(),
                bert_model=self.bert_model_name.get()
            )
            
            # Log results
            log_text = f"Tam Entegrasyon Pipeline Tamamlandı!\n"
            log_text += f"Toplam süre: {results['summary']['total_time']:.2f} saniye\n"
            log_text += f"Stages: {len(results['stages'])}\n"
            
            if 'traditional_ml' in results['stages']:
                ml_stats = results['stages']['traditional_ml']
                log_text += f"Traditional ML: {ml_stats['vocabulary_size']} kelimeler, {ml_stats['tagset_size']} etiketler\n"
                
            if 'bert_models' in results['stages']:
                bert_stats = results['stages']['bert_models']
                log_text += f"BERT Model: {bert_stats['model_name']}\n"
                
            self.model_log.insert(tk.END, log_text)
            self.model_log.see(tk.END)
            self.model_progress['value'] = 100
            self.status_var.set("Tam entegrasyon pipeline tamamlandı")
            
        except Exception as e:
            self.model_log.insert(tk.END, f"Hata: {str(e)}\n")
            self.model_progress['value'] = 0

def main():
    """Main function to run the enhanced GUI"""
    root = tk.Tk()
    app = EnhancedCorpusGUI(root)
    
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