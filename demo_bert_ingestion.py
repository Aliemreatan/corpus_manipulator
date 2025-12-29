#!/usr/bin/env python3
"""
BERT backend ile veri ingestion örneği
"""

import os
from ingestion.corpus_ingestor import CorpusIngestor

def main():
    # Eski veritabanını temizle
    if os.path.exists('corpus.db'):
        os.remove('corpus.db')
        print('Eski veritabanı temizlendi')

    print("=== BERT BACKEND İLE İNGESTION ===")

    # BERT backend ile ingestion
    ingestor = CorpusIngestor('corpus.db', 'custom_bert')

    try:
        stats = ingestor.ingest_directory('sample_turkish_corpus', max_files=1)
        print("✅ Başarıyla tamamlandı!")
        print(f"İşlenen doküman: {stats['documents_processed']}")
        print(f"İşlenen token: {stats['tokens_processed']}")

    except Exception as e:
        print(f"❌ Hata: {e}")

if __name__ == "__main__":
    main()