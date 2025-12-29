#!/usr/bin/env python3
"""
Veritabanı sorgulama örnekleri
"""

from query.corpus_query import CorpusQuery

def main():
    # Sorgu nesnesi oluştur
    query = CorpusQuery('corpus.db')

    print('=== KWIC ARAMA: "aile" ===')
    results = query.kwic_concordance('aile', window_size=3, limit=3)

    for result in results:
        left = result.get('left_context', '')
        keyword = result.get('keyword', '')
        right = result.get('right_context', '')
        print(f'... {left} [{keyword}] {right} ...')

    print('\n=== FREKANS LİSTESİ ===')
    freq_results = query.frequency_list(limit=5)
    for item in freq_results:
        print(f'{item["word"]}: {item["frequency"]} kez')

    print('\n=== KOLOKASYON ANALİZİ ===')
    coll_results = query.collocation_analysis('aile', window_size=3, limit=3)
    for item in coll_results:
        print(f'{item["collocate"]}: {item["co_occurrence_count"]} kez (score: {item["score"]:.2f})')

    query.db.close()

if __name__ == "__main__":
    main()