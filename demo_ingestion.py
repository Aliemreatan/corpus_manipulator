#!/usr/bin/env python3
"""
Veritabanına örnek veri ekleme örneği
"""

from ingestion.corpus_ingestor import CorpusIngestor

def main():
    print("=== VERİ İNGESTION ÖRNEĞİ ===")

    # Corpus ingestor oluştur (basit backend ile)
    ingestor = CorpusIngestor('corpus.db', 'simple')

    # Sample klasöründen 2 dosya işle
    try:
        print("Sample klasöründen dosyalar işleniyor...")
        stats = ingestor.ingest_directory('sample_turkish_corpus', max_files=2)

        print("✅ Başarıyla tamamlandı!")
        print(f"İşlenen doküman sayısı: {stats['documents_processed']}")
        print(f"İşlenen cümle sayısı: {stats['sentences_processed']}")
        print(f"İşlenen token sayısı: {stats['tokens_processed']}")
        print(f"Hata sayısı: {stats['errors']}")

    except Exception as e:
        print(f"❌ Hata oluştu: {e}")

if __name__ == "__main__":
    main()