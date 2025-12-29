"""
Update Database with BERT POS Tags

Bu script mevcut bir veritabanındaki tüm cümleleri tarar,
BERT modeli ile yeniden işler ve POS taglerini günceller.

Kullanım:
    python update_db_with_bert.py <veritabanı_dosyası>
"""

import sys
import os
import sqlite3
import logging
from typing import List, Dict, Any
from tqdm import tqdm

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nlp.custom_bert_processor import create_custom_bert_processor

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseUpdater:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        self.bert = None
        
    def connect(self):
        """Veritabanına bağlan"""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Veritabanı bulunamadı: {self.db_path}")
            
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        logger.info(f"Veritabanına bağlanıldı: {self.db_path}")

    def load_bert(self):
        """BERT modelini yükle"""
        logger.info("BERT modeli yükleniyor... (Bu işlem biraz sürebilir)")
        self.bert = create_custom_bert_processor()
        
        if not self.bert.is_loaded:
            logger.warning("BERT modeli tam yüklenemedi! Basit işleme modunda çalışacak.")
        else:
            logger.info("BERT modeli başarıyla yüklendi.")

    def update_all_sentences(self):
        """Tüm cümleleri yeniden işle ve güncelle"""
        if not self.conn:
            self.connect()
        if not self.bert:
            self.load_bert()
            
        cursor = self.conn.cursor()
        
        # 1. Tüm cümleleri çek
        logger.info("Veritabanındaki cümleler okunuyor...")
        cursor.execute("SELECT sent_id, doc_id, sent_text FROM sentences")
        sentences = cursor.fetchall()
        total_sentences = len(sentences)
        logger.info(f"Toplam {total_sentences} cümle işlenecek.")
        
        # 2. İşlem döngüsü
        updated_count = 0
        error_count = 0
        
        # Batch işlemi için transaction başlat
        self.conn.execute("BEGIN TRANSACTION")
        
        try:
            for row in tqdm(sentences, desc="BERT ile Etiketleniyor"):
                sent_id = row['sent_id']
                doc_id = row['doc_id']
                text = row['sent_text']
                
                try:
                    # BERT ile işle
                    tokens = self.bert.process_text(text)
                    
                    # Eski tokenları sil (bu cümle için)
                    self.conn.execute("DELETE FROM tokens WHERE sent_id = ?", (sent_id,))
                    
                    # Yeni tokenları ekle
                    self._insert_tokens(doc_id, sent_id, tokens)
                    
                    updated_count += 1
                    
                    # Her 100 cümlede bir commit yap (güvenlik ve performans için)
                    if updated_count % 100 == 0:
                        self.conn.commit()
                        self.conn.execute("BEGIN TRANSACTION")
                        
                except Exception as e:
                    logger.error(f"Cümle {sent_id} işlenirken hata: {e}")
                    error_count += 1
            
            # Son commit
            self.conn.commit()
            logger.info("GÜNCELLEME TAMAMLANDI!")
            logger.info(f"Başarılı: {updated_count}")
            logger.info(f"Hatalı: {error_count}")
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Kritik hata, değişiklikler geri alındı: {e}")
            raise

    def _insert_tokens(self, doc_id: int, sent_id: int, tokens: List[Dict[str, Any]]):
        """Token listesini veritabanına ekle"""
        query = """
            INSERT INTO tokens (
                doc_id, sent_id, token_number, form, norm, lemma, upos, xpos,
                morph, dep_head, dep_rel, start_char, end_char,
                is_punctuation, is_space
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        data = []
        for i, token in enumerate(tokens):
            data.append((
                doc_id,
                sent_id,
                i,  # token_number
                token.get('word', token.get('form', '')),
                token['norm'],
                token.get('lemma'), # BERT lemma üretmeyebilir, None olabilir
                token.get('upos'),  # BERT'ten gelen POS Tag (NOUN, VERB vb.)
                token.get('xpos'),  # Varsa language specific POS
                token.get('morph'),
                token.get('dep_head'),
                token.get('dep_rel'),
                token['start_char'],
                token['end_char'],
                int(token.get('is_punctuation', 0)),
                int(token.get('is_space', 0))
            ))
            
        self.conn.executemany(query, data)

    def close(self):
        if self.conn:
            self.conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Kullanım: python update_db_with_bert.py <veritabanı_dosyası>")
        print("Örnek: python update_db_with_bert.py corpus.db")
        
        # Varsayılan olarak demo veritabanını dene
        default_db = "working_example.db"
        if os.path.exists(default_db):
            print(f"\nOtomatik olarak {default_db} kullanılıyor...")
            updater = DatabaseUpdater(default_db)
            updater.update_all_sentences()
            updater.close()
        else:
            sys.exit(1)
    else:
        db_file = sys.argv[1]
        updater = DatabaseUpdater(db_file)
        updater.update_all_sentences()
        updater.close()
