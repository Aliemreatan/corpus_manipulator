#!/usr/bin/env python3
"""
Veritabanındaki veriyi kontrol et
"""

import sqlite3

def main():
    conn = sqlite3.connect('corpus.db')
    cursor = conn.cursor()

    # Veritabanı durumu
    cursor.execute('SELECT COUNT(*) FROM documents')
    print(f'Doküman sayısı: {cursor.fetchone()[0]}')

    cursor.execute('SELECT COUNT(*) FROM sentences')
    print(f'Cümle sayısı: {cursor.fetchone()[0]}')

    cursor.execute('SELECT COUNT(*) FROM tokens')
    token_count = cursor.fetchone()[0]
    print(f'Token sayısı: {token_count}')

    # Örnek tokenlar
    if token_count > 0:
        print('\n=== ÖRNEK TOKENLAR ===')
        cursor.execute('SELECT form, norm, upos FROM tokens LIMIT 5')
        for row in cursor.fetchall():
            print(f'{row[0]} -> norm: {row[1]}, pos: {row[2]}')

    conn.close()

if __name__ == "__main__":
    main()