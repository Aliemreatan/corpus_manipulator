#!/usr/bin/env python3
"""
Veritabanı şemasını göster
"""

from database.schema import CorpusDatabase

def main():
    # Veritabanı şemasını göster
    db = CorpusDatabase('corpus.db')
    db.connect()
    db.create_schema()

    # Tablo bilgilerini al
    schema_info = db.get_schema_info()

    print('=== VERİTABANI TABLOLAR ===')
    for table_name, table_info in schema_info['tables'].items():
        print(f'\n{table_name.upper()}:')
        for col in table_info['columns']:
            pk = ' (PRIMARY KEY)' if col['pk'] else ''
            print(f'  - {col["name"]}: {col["type"]}{pk}')

    print(f'\nFTS Tablosu: {schema_info["fts_table"]}')

    print('\n=== VERİ AKIŞI ===')
    print('1. CorpusIngestor: Dosyaları oku -> NLP işle -> Veritabanına kaydet')
    print('2. CorpusQuery: Veritabanından KWIC/frekans/kolokasyon sorgula')
    print('3. GUI: Sorgu sonuçlarını göster')

    db.close()

if __name__ == "__main__":
    main()