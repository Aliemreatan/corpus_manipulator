#!/usr/bin/env python3
"""
Corpus Data Manipulator - Demo Script

Bu script Corpus Data Manipulator'ın tüm özelliklerini gösterir:
- Corpus ingestion (Türkçe metin dosyalarını içeri alma)
- NLP işleme (tokenizasyon, lemma, POS, dependency)
- KWIC concordance araması
- Frekans analizi
- Collocation analizi (PMI, log-likelihood, t-score)
- Word sketch (dependency tabanlı)

Kullanım:
    py demo.py
"""

import sys
import os
from pathlib import Path
import json

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Simple fallback for imports in case module structure has issues
try:
    from corpus_manipulator import CorpusManipulator
except ImportError:
    # Fallback imports if module structure has issues
    from database.schema import CorpusDatabase
    from nlp.turkish_processor import TurkishNLPProcessor
    from ingestion.corpus_ingestor import CorpusIngestor
    from query.corpus_query import CorpusQuery

def create_sample_corpus():
    """Demo için örnek Türkçe korpus oluştur"""
    
    print("=== ÖRNEK KORPUS OLUŞTURMA ===")
    
    # Örnek metinler oluştur
    sample_texts = [
        {
            'filename': 'ev_metni.txt',
            'content': """
            Benim evim çok güzel bir yerde. Evin bahçesi büyük ve yeşil. 
            Evimizde üç oda var. Anne ve babam evi çok temiz tutar. 
            Komşularımız da çok iyiler. Onların evi de bizim evimize yakın.
            Evde birlikte yemek yeriz ve televizyon izleriz. 
            Evimde mutluyum çünkü ailem burada.
            """,
            'category': 'ev'
        },
        {
            'filename': 'okul_metni.txt', 
            'content': """
            Ben okula gidiyorum. Okulda çok arkadaşım var. 
            Öğretmenlerimiz çok bilgili. Matematik dersini severim.
            Okul kütüphanesinde kitap okurum. Okul bahçesinde futbol oynarım.
            Okul yemekhanesi çok lezzetli yemekler var. 
            Okul zamanım çok eğlenceli geçer. Okuldan sonra eve gelirim.
            """,
            'category': 'okul'
        },
        {
            'filename': 'kitap_metni.txt',
            'content': """
            Kitap okumayı çok severim. En sevdiğim kitap roman türü.
            Kitapta güzel hikayeler var. Yazarlar kitaplarında duygularını anlatır.
            Kitap okurken zamanın nasıl geçtiğini anlamam. 
            Kütüphaneden kitap alırım. Kitabımı dikkatli okurum.
            Kitabı bitirdiğimde çok mutlu olurum. Kitaplar bana arkadaş gibi gelir.
            """,
            'category': 'kitap'
        },
        {
            'filename': 'aile_metni.txt',
            'content': """
            Ailem çok önemli benim için. Annem ve babam beni çok severler.
            Ailecek birlikte vakit geçiririz. Ailemde kardeşim de var.
            Ailemle konuşurken her şeyimi anlatırım. 
            Ailem beni hiç yalnız bırakmaz. Ailemle tatil yaparız.
            Ailem benim için en kıymetli şey. Ailem olmadan yapamam.
            """,
            'category': 'aile'
        }
    ]
    
    # Örnek dosyaları oluştur
    sample_dir = Path("sample_turkish_corpus")
    sample_dir.mkdir(exist_ok=True)
    
    for text_data in sample_texts:
        file_path = sample_dir / text_data['filename']
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text_data['content'])
        print(f"✓ Oluşturuldu: {file_path}")
    
    return str(sample_dir)

def run_demo():
    """Ana demo fonksiyonu"""
    
    print("=" * 60)
    print("CORPUS DATA MANIPULATOR - TÜRKÇE DEMO")
    print("=" * 60)
    
    # 1. Örnek korpus oluştur
    print("\n1. ÖRNEK KORPUS OLUŞTURMA")
    print("-" * 30)
    corpus_dir = create_sample_corpus()
    
    # 2. Corpus Manipulator oluştur
    print("\n2. CORPUS MANIPULATOR BAŞLATMA")
    print("-" * 30)
    db_path = "demo_corpus.db"
    
    try:
        # Try to import and use CorpusManipulator
        try:
            corpus = CorpusManipulator(db_path, nlp_backend='simple')
            nlp_info = corpus.get_nlp_info()
            print(f"✓ NLP Backend: {nlp_info['backend']}")
            print(f"✓ Özellikler: {nlp_info['features_available']}")
            using_main_api = True
        except ImportError:
            # Fallback to direct component usage
            print("✓ Fallback mode: Direct component usage")
            print("  - CorpusDatabase")
            print("  - TurkishNLPProcessor") 
            print("  - CorpusIngestor")
            print("  - CorpusQuery")
            using_main_api = False
            
    except Exception as e:
        print(f"✗ Hata: {e}")
        return
    
    # 3. Corpus içeri aktarma
    print("\n3. CORPUS İÇERİ AKTARMA")
    print("-" * 30)
    try:
        if using_main_api:
            stats = corpus.ingest_directory(corpus_dir)
        else:
            # Fallback ingestion
            ingestor = CorpusIngestor(db_path, nlp_backend='simple')
            stats = ingestor.ingest_directory(corpus_dir)
            ingestor.close()
        
        print(f"✓ İşlenen dosya sayısı: {stats['documents_processed']}")
        print(f"✓ İşlenen cümle sayısı: {stats['sentences_processed']}")
        print(f"✓ İşlenen token sayısı: {stats['tokens_processed']}")
    except Exception as e:
        print(f"✗ Hata: {e}")
        return
    
    # 4. Veritabanı istatistikleri
    print("\n4. VERİTABANI İSTATİSTİKLERİ")
    print("-" * 30)
    try:
        if using_main_api:
            db_stats = corpus.get_stats()
        else:
            # Fallback stats
            query = CorpusQuery(db_path)
            db_stats = query.get_processing_stats()
            query.close()
        
        print(f"✓ Toplam belge: {db_stats['database_stats']['total_documents']}")
        print(f"✓ Toplam cümle: {db_stats['database_stats']['total_sentences']}")
        print(f"✓ Toplam token: {db_stats['database_stats']['total_tokens']}")
        print(f"✓ Benzersiz kelime: {db_stats['database_stats']['unique_words']}")
    except Exception as e:
        print(f"✗ Hata: {e}")
    
    # 5. KWIC arama
    print("\n5. KWIC CONCORDANCE ARAMA")
    print("-" * 30)
    try:
        kwic_results = corpus.kwic_search("ev", window_size=3, limit=5)
        print(f"✓ 'ev' kelimesi için {len(kwic_results)} KWIC sonucu bulundu:")
        for i, result in enumerate(kwic_results[:3], 1):
            context = f"{result['left_context']} [[[{result['keyword']}]] {result['right_context']}"
            print(f"  {i}. {context}")
    except Exception as e:
        print(f"✗ KWIC hatası: {e}")
    
    # 6. Frekans analizi
    print("\n6. FREKANS ANALİZİ")
    print("-" * 30)
    try:
        freq_results = corpus.frequency_list(word_type='norm', limit=10)
        print("✓ En sık kullanılan 10 kelime:")
        for item in freq_results:
            print(f"  {item['word']}: {item['frequency']} kez")
    except Exception as e:
        print(f"✗ Frekans analizi hatası: {e}")
    
    # 7. Lemma + POS frekans
    print("\n7. LEMMA + POS FREKANS")
    print("-" * 30)
    try:
        lemmapos_results = corpus.frequency_list_lemmapos(limit=10)
        print("✓ En sık lemma+POS kombinasyonları:")
        for item in lemmapos_results:
            print(f"  {item['lemma']} ({item['pos']}): {item['frequency']} kez")
    except Exception as e:
        print(f"✗ Lemma+POS hatası: {e}")
    
    # 8. Collocation analizi
    print("\n8. COLLOCATION ANALİZİ")
    print("-" * 30)
    try:
        colloc_results = corpus.collocation_analysis("ev", word_type='norm', window_size=3)
        print(f"✓ 'ev' kelimesi için collocation sonuçları:")
        for item in colloc_results[:5]:
            print(f"  {item['collocate']}: {item['co_occurrence_count']} birlikte, PMI: {item['score']:.3f}")
    except Exception as e:
        print(f"✗ Collocation hatası: {e}")
    
    # 9. Word sketch
    print("\n9. WORD SKETCH ANALİZİ")
    print("-" * 30)
    try:
        sketch = corpus.word_sketch("ev")
        print(f"✓ 'ev' kelimesi için dependency relations:")
        for relation, words in sketch.items():
            print(f"  {relation}: {len(words)} bağlantı")
            for word_info in words[:3]:  # İlk 3'ünü göster
                print(f"    - {word_info['related_word']} ({word_info['frequency']} kez)")
    except Exception as e:
        print(f"✗ Word sketch hatası: {e}")
    
    # 10. Hızlı arama fonksiyonları
    print("\n10. HIZLI ARAMA FONKSİYONLARI")
    print("-" * 30)
    try:
        # Form ile arama
        form_results = corpus.search_by_form("okul", limit=3)
        print(f"✓ 'okul' formu ile arama: {len(form_results)} sonuç")
        
        # Lemma ile arama
        lemma_results = corpus.search_by_lemma("ev", limit=3)
        print(f"✓ 'ev' lemma ile arama: {len(lemma_results)} sonuç")
        
    except Exception as e:
        print(f"✗ Hızlı arama hatası: {e}")
    
    # 11. Context manager kullanımı
    print("\n11. CONTEXT MANAGER KULLANIMI")
    print("-" * 30)
    try:
        with CorpusManipulator(db_path, nlp_backend='simple') as corpus2:
            stats2 = corpus2.get_stats()
            print(f"✓ Context manager ile bağlantı: {stats2['database_stats']['total_tokens']} token")
    except Exception as e:
        print(f"✗ Context manager hatası: {e}")
    
    # Kullanım örnekleri
    print("\nKullanım örnekleri:")
    if using_main_api:
        print("  corpus = CorpusManipulator('my_corpus.db')")
        print("  corpus.ingest_directory('./my_texts')")
        print("  results = corpus.kwic_search('kelime')")
    else:
        print("  # Fallback kullanım:")
        print("  db = CorpusDatabase('my_corpus.db')")
        print("  nlp = TurkishNLPProcessor()")
        print("  ingestor = CorpusIngestor('my_corpus.db')")
        print("  query = CorpusQuery('my_corpus.db')")
    
    # Temizlik
    if using_main_api:
        corpus.close()
    
    print("\n" + "=" * 60)
    print("DEMO TAMAMLANDI!")
    print("=" * 60)
    print(f"✓ Demo veritabanı: {db_path}")
    print("✓ Şimdi kendi metinlerinizle deneyebilirsiniz!")

if __name__ == "__main__":
    run_demo()