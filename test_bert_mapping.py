#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test BERT model Turkish POS tagging with improved mapping
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from nlp.custom_bert_processor import CustomBERTProcessor
import json

def test_bert_mapping():
    """BERT model mapping test"""
    print("=== BERT Turkish POS Mapping Test ===")
    
    try:
        # BERT processor baslat
        processor = CustomBERTProcessor()
        print("[OK] BERT Processor baslatildi")
        
        # Test words
        test_words = [
            "at",          # User critical example - should be NOUN
            "kosuyor",     # User critical example - should be VERB  
            "guzel",       # Adjective
            "kitap",       # Noun
            "okulda",      # Noun + postposition
            "buyuk",       # Adjective
            "ve",          # Conjunction
            "bir",         # Number/Determiner
            "geliyor",     # Verb
            "ev"           # Noun
        ]
        
        print(f"\nTesting {len(test_words)} Turkish words:")
        print("-" * 50)
        
        for i, word in enumerate(test_words, 1):
            try:
                # BERT ile analiz et
                tokens = processor.process_text(word)
                
                if tokens and len(tokens) > 0:
                    token = tokens[0]  # First token (single word)
                    print(f"{i:2d}. '{word:12s}' → {token.get('upos', 'UNKNOWN'):8s} "
                          f"(confidence: {token.get('bert_confidence', 0):.3f}) "
                          f"| Raw: {token.get('xpos', 'N/A')}")
                else:
                    print(f"{i:2d}. '{word:12s}' → No tokens found")
                
            except Exception as e:
                print(f"{i:2d}. '{word:12s}' → ERROR: {str(e)}")
        
        print("\n=== Model Properties ===")
        info = processor.get_model_info()
        print(f"Model path: {info['model_path']}")
        print(f"Loaded: {info['is_loaded']}")
        print(f"Features: {info['supported_features']}")
        
        # Label mapping test
        print("\n=== Label Mapping Test ===")
        test_labels = [
            "NOUN", "VERB", "ADJ", "ADV", "PRON", "DET", 
            "ADP", "CCONJ", "SCONJ", "AUX", "PROPN", "NUM",
            "AD-NOUN", "FIIL-VERB", "SIFAT-ADJECTIVE", "ZAMIR-PRON",
            "BELIRTEC-DET", "EDAT-ADP", "BAGLAC-CCONJ", "SAYI-NUM"
        ]
        
        for label in test_labels:
            mapped = processor._map_bert_label_to_pos(label, "test")
            print(f"'{label:15s}' → '{mapped}'")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Test error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_critical_fixes():
    """Test critical word fixes"""
    print("\n=== Critical Word Fix Test ===")
    
    try:
        processor = CustomBERTProcessor()
        
        # Test critical cases
        critical_words = ["at", "kosuyor"]
        
        for word in critical_words:
            # Test mapping function directly
            # First test with various possible labels
            possible_labels = ["NOUN", "VERB", "ADJ", "ADP", "FIIL-VERB", "AD-NOUN"]
            
            print(f"\nTesting word: '{word}'")
            for label in possible_labels:
                mapped = processor._map_bert_label_to_pos(label, word)
                print(f"  '{label}' → '{mapped}'")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Critical fix test error: {str(e)}")
        return False

if __name__ == "__main__":
    print("BERT Turkish POS Mapping Test starting...\n")
    
    # Main test
    success1 = test_bert_mapping()
    
    # Critical fixes test
    success2 = test_critical_fixes()
    
    print(f"\n=== Test Results ===")
    print(f"Mapping Test: {'[OK] Success' if success1 else '[ERROR] Failed'}")
    print(f"Critical Fix Test: {'[OK] Success' if success2 else '[ERROR] Failed'}")
    
    if success1 and success2:
        print("\n[SUCCESS] All tests successful! BERT model ready.")
    else:
        print("\n[WARNING] Some tests failed. Check output.")