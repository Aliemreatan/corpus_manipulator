#!/usr/bin/env python3
"""
Test script for Sketch Engine-like features
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_realtime_nlp_backends():
    """Test real-time NLP analysis with different backends"""
    print("=== TESTING REAL-TIME NLP BACKENDS ===")

    test_text = "Türkçe dil işleme için BERT modeli kullanıyoruz."

    backends = ["simple", "stanza", "spacy", "custom_bert"]

    for backend in backends:
        print(f"\n--- Testing {backend.upper()} backend ---")
        try:
            from nlp.turkish_processor import TurkishNLPProcessor
            processor = TurkishNLPProcessor(backend=backend)
            tokens = processor.process_text(test_text)

            print(f"✓ {backend.upper()}: {len(tokens)} tokens processed")

            if tokens:
                # Show first token
                first_token = tokens[0]
                if isinstance(first_token, dict):
                    word = first_token.get('word', first_token.get('text', 'N/A'))
                    print(f"  Sample: {word}")
                else:
                    print(f"  Sample: {first_token}")

        except Exception as e:
            print(f"✗ {backend.upper()}: Failed - {str(e)}")

def test_corpus_sources():
    """Test different corpus source types"""
    print("\n=== TESTING CORPUS SOURCES ===")

    # Test file-based analysis
    print("--- Testing file-based analysis ---")
    try:
        from pathlib import Path
        sample_file = Path("sample_turkish_corpus/aile_metni.txt")

        if sample_file.exists():
            with open(sample_file, 'r', encoding='utf-8') as f:
                text = f.read()

            # Simple frequency analysis
            import re
            from collections import Counter

            words = re.findall(r'\b\w+\b', text.lower())
            word_counts = Counter(words)

            print(f"✓ File analysis: {len(words)} words, {len(word_counts)} unique")
            print(f"  Top words: {word_counts.most_common(3)}")
        else:
            print("✗ Sample file not found")

    except Exception as e:
        print(f"✗ File analysis failed: {str(e)}")

if __name__ == "__main__":
    test_realtime_nlp_backends()
    test_corpus_sources()
    print("\n=== TEST COMPLETE ===")