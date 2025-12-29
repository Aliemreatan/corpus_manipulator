#!/usr/bin/env python3
"""
BERT Integration Demo for GUI

Bu script BERT modelinin GUI ile nasıl kullanılacağını gösterir.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def demo_bert_gui_integration():
    """Demonstrate BERT GUI integration"""
    print("=== BERT GUI INTEGRATION DEMO ===")
    print()
    
    print("1. GUI'yu başlatmak için:")
    print("   python run_gui.py")
    print("   veya")
    print("   py run_gui.py")
    print()
    
    print("2. GUI'da BERT kullanım adımları:")
    print()
    print("   a) Veritabanı Oluştur:")
    print("      - 'Veritabanı Dosyası' alanına corpus.db yazın")
    print("      - 'Veritabanı Oluştur' butonuna tıklayın")
    print()
    print("   b) Corpus İçeri Aktar:")
    print("      - 'Metin Klasörü' alanına sample_turkish_corpus klasörünü seçin")
    print("      - 'NLP Backend' dropdown'undan 'custom_bert' seçin")
    print("      - 'Corpus'u İçeri Aktar' butonuna tıklayın")
    print()
    print("   c) BERT Analizi:")
    print("      - 'BERT Analizi (Real-time)' bölümüne gidin")
    print("      - 'Veritabanından Kelimeleri Yükle' butonuna tıklayın")
    print("      - Kelime listesinden bir kelime çift tıklayın")
    print("      - Test metni otomatik olarak doldurulur")
    print("      - 'BERT ile Analiz Et' butonuna tıklayın")
    print("      - Sonuçları 'BERT Sonuçları' alanında görün")
    print()
    
    print("3. BERT Analizi Özellikleri:")
    print("   ✓ Real-time Turkish POS tagging")
    print("   ✓ Confidence scores")
    print("   ✓ Morphological analysis")
    print("   ✓ Word selection from database")
    print("   ✓ Custom text input support")
    print()
    
    print("4. Mevcut Backend Seçenekleri:")
    print("   - simple: Basit tokenization")
    print("   - spacy: spaCy Turkish model")
    print("   - stanza: Stanza Turkish model")
    print("   - custom_bert: Hugging Face BERT model (YENİ!)")
    print()
    
    print("5. Test Metinleri:")
    print("   - 'Ben okula gidiyorum ve kitap okuyorum.'")
    print("   - 'Türkçe dil işleme için yeni BERT modelini test ediyoruz.'")
    print("   - 'Bu bir test cümlesidir, NLP analizi için kullanılır.'")
    print()
    
    print("6. Hata Durumunda:")
    print("   - Model yüklenemezse 'simple' backend'e geçer")
    print("   - İnternet bağlantısı gerekli (model download)")
    print("   - transformers ve torch paketleri yüklü olmalı")
    print()
    
    print("7. Sonuç Formatı:")
    print("   Her token için:")
    print("   - form: Orijinal kelime")
    print("   - upos: Universal POS tag")
    print("   - lemma: Lemma (kök)")
    print("   - morph: Morfolojik özellikler")
    print("   - bert_confidence: Model güven skoru")
    print()
    
    print("8. Performans:")
    print("   - İlk yükleme: 10-30 saniye")
    print("   - Sonraki işlemler: ~100-500ms")
    print("   - Memory kullanımı: ~500MB-1GB")

def demo_bert_features():
    """Show specific BERT features"""
    print("\n=== BERT ÖZELLİKLERİ ===")
    print()
    
    try:
        from nlp.custom_bert_processor import create_custom_bert_processor
        
        print("BERT Processor oluşturuluyor...")
        bert = create_custom_bert_processor()
        
        info = bert.get_model_info()
        print(f"Model Type: {info['model_type']}")
        print(f"Model Path: {info['model_path']}")
        print(f"Is Loaded: {info['is_loaded']}")
        print(f"Supported Features: {', '.join(info['supported_features'])}")
        print()
        
        if info['is_loaded']:
            print("Test metni işleniyor...")
            test_text = "Türkçe NLP için BERT modeli test ediliyor."
            tokens = bert.process_text(test_text)
            
            print(f"İşlenen token sayısı: {len(tokens)}")
            print("\nİlk 5 token:")
            for i, token in enumerate(tokens[:5], 1):
                confidence = token.get('bert_confidence', 'N/A')
                print(f"{i}. {token['form']} -> {token['upos']} (Güven: {confidence})")
        else:
            print("Model henüz yüklenmedi. GUI'da deneyin.")
            
    except Exception as e:
        print(f"BERT test edilemedi: {e}")
        print("GUI'da deneyin.")

def main():
    """Main demo function"""
    print("BERT Model GUI Integration Demo")
    print("=" * 50)
    print()
    
    demo_bert_gui_integration()
    demo_bert_features()
    
    print("\n" + "=" * 50)
    print("Demo tamamlandı!")
    print("\nGUI'yu başlatmak için: python run_gui.py")

if __name__ == "__main__":
    main()