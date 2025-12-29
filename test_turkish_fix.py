#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Turkish POS tagging fixes
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_turkish_words():
    """Test the specific examples mentioned by user"""
    print("TESTING TURKISH POS TAGGING")
    print("=" * 40)
    
    try:
        from nlp.custom_bert_processor import create_custom_bert_processor
        
        bert = create_custom_bert_processor()
        
        # Test cases from user
        test_words = ["at", "koşuyor"]
        
        for word in test_words:
            print(f"\nTesting word: '{word}'")
            tokens = bert.process_text(word)
            
            if tokens:
                token = tokens[0]
                word_form = token['form']
                pos = token['upos']
                confidence = token.get('bert_confidence', 'N/A')
                
                print(f"  Form: {word_form}")
                print(f"  POS: {pos}")
                print(f"  Confidence: {confidence}")
                
                # Check expected results
                if word == "at":
                    expected = "NOUN"
                    status = "✅ CORRECT" if pos == expected else "❌ WRONG"
                    print(f"  Expected: {expected} -> {status}")
                elif word == "koşuyor":
                    expected = "VERB"
                    status = "✅ CORRECT" if pos == expected else "❌ WRONG"
                    print(f"  Expected: {expected} -> {status}")
            else:
                print(f"  No tokens processed for '{word}'")
        
        # Test sentence
        print(f"\nTesting sentence: 'At koşuyor.'")
        sentence = "At koşuyor."
        tokens = bert.process_text(sentence)
        
        if tokens:
            print("Results:")
            for i, token in enumerate(tokens, 1):
                word = token['form']
                pos = token['upos']
                print(f"  {i}. {word} -> {pos}")
        else:
            print("No tokens processed")
            
        print("\n" + "=" * 40)
        print("Test completed!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_turkish_words()