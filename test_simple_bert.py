#!/usr/bin/env python3
"""
Simple BERT mapping test - no unicode characters
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from nlp.custom_bert_processor import CustomBERTProcessor

def test_mapping():
    """Test BERT mapping function"""
    print("=== BERT Mapping Test ===")
    
    processor = CustomBERTProcessor()
    
    # Test the critical cases
    test_cases = [
        ("at", "NOUN", "Expected: NOUN (horse)"),
        ("kosuyor", "VERB", "Expected: VERB (running)"),
        ("test", "NOUN", "Expected: NOUN (default)")
    ]
    
    print("\nTesting critical words:")
    for word, label, desc in test_cases:
        result = processor._map_bert_label_to_pos(label, word)
        print(f"{word:10s} + {label:10s} -> {result:8s} | {desc}")
    
    # Test label mapping
    print("\nTesting label mappings:")
    test_labels = ["NOUN", "VERB", "ADJ", "FIIL-VERB", "AD-NOUN"]
    for label in test_labels:
        result = processor._map_bert_label_to_pos(label, "test")
        print(f"{label:12s} -> {result:8s}")
    
    # Test with actual processing
    print("\nTesting actual processing:")
    test_words = ["at", "kosuyor", "kitap"]
    
    for word in test_words:
        try:
            tokens = processor.process_text(word)
            if tokens:
                token = tokens[0]
                print(f"{word:10s} -> {token.get('upos', 'UNKNOWN'):8s} (confidence: {token.get('bert_confidence', 0):.3f})")
            else:
                print(f"{word:10s} -> No tokens")
        except Exception as e:
            print(f"{word:10s} -> ERROR: {str(e)}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_mapping()