"""
Backend Comparison Tool: Simple vs. BERT

Bu script, veritabanındaki veya örnek cümlelerdeki analiz farklarını
yan yana (side-by-side) karşılaştırır.
"""

import sys
import os
import pandas as pd
from tabulate import tabulate

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nlp.turkish_processor import TurkishNLPProcessor

def compare_sentences(sentences):
    """Verilen cümleleri iki backend ile analiz edip karşılaştırır"""
    
    # İşlemcileri yükle
    print("Modeller yükleniyor...")
    nlp_simple = TurkishNLPProcessor(backend='simple')
    nlp_bert = TurkishNLPProcessor(backend='custom_bert')
    print("Modeller hazır.\n")
    
    for i, text in enumerate(sentences, 1):
        print(f"\n{'='*80}")
        print(f"ÖRNEK {i}: \"{text}\"")
        print(f"{'='*80}")
        
        # Analiz et
        tokens_simple = nlp_simple.process_text(text)
        tokens_bert = nlp_bert.process_text(text)
        
        # Verileri tablo için hazırla
        # BERT ve Simple token sayıları farklı olabilir, o yüzden satır satır eşleştirmek zor olabilir.
        # Bu yüzden yan yana iki ayrı tablo yerine, hizalanmış bir görünüm deneyeceğiz.
        
        print("\n--- DETAYLI KARŞILAŞTIRMA ---\\n")
        
        # Simple Sonuçları
        simple_data = []
        for t in tokens_simple:
            # Fallback to 'word' or 'text' if 'form' is missing
            word = t.get('form', t.get('word', t.get('text', '')))
            simple_data.append([word, t.get('upos'), t.get('upos_tr')])
            
        # BERT Sonuçları
        bert_data = []
        for t in tokens_bert:
            word = t.get('form', t.get('word', t.get('text', '')))
            conf = t.get('bert_confidence', 0.0)
            conf_str = f"%{int(conf*100)}" if conf else "N/A"
            bert_data.append([word, t.get('upos'), t.get('upos_tr'), conf_str])
            
        # Pandas DataFrame ile gösterim (daha okunaklı)
        df_simple = pd.DataFrame(simple_data, columns=["Token", "Simple POS", "TR Etiket"])
        df_bert = pd.DataFrame(bert_data, columns=["Token", "BERT POS", "TR Etiket", "Güven"])
        
        print(">>> SIMPLE (ESKİ YÖNTEM):")
        print(tabulate(df_simple, headers='keys', tablefmt='simple_grid'))
        
        print("\n>>> BERT (YENİ YÖNTEM):")
        print(tabulate(df_bert, headers='keys', tablefmt='simple_grid'))
        
        # Kritik Farklar Analizi
        print("\n>>> KRİTİK FARKLAR:")
        analyze_differences(tokens_simple, tokens_bert)

def analyze_differences(simple, bert):
    """Otomatik fark analizi"""
    
    # Basit kelime eşleştirme (tam eşleşmeyebilir ama fikir verir)
    simple_map = {}
    for t in simple:
        word = t.get('form', t.get('word', t.get('text', ''))).lower()
        simple_map[word] = t.get('upos')
        
    bert_map = {}
    for t in bert:
        word = t.get('form', t.get('word', t.get('text', ''))).lower()
        bert_map[word] = t.get('upos')
    
    found_diff = False
    for word, simple_pos in simple_map.items():
        if word in bert_map:
            bert_pos = bert_map[word]
            if simple_pos != bert_pos:
                # Sadece anlamlı farkları göster (NOUN vs PROPN farkı bazen önemsizdir)
                if simple_pos is None: simple_pos = "None"
                if bert_pos is None: bert_pos = "None"
                
                print(f"  * '{word}': Simple[{simple_pos}] -> BERT[{bert_pos}]")
                found_diff = True
                
    if not found_diff:
        print("  (Belirgin bir etiket farkı bulunamadı)")

if __name__ == "__main__":
    # Test Cümleleri (Zor örnekler seçtim)
    test_sentences = [
        "Ben okula gidiyorum.",                  # Standart cümle
        "Yüzü bana döndü.",                      # Eş sesli: Yüz (Face vs 100)
        "Kırmızı elma çürüdü.",                  # Sıfat Tamlaması
        "Ahmet topu attı."
    ]
    
    compare_sentences(test_sentences)
