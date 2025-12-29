#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple verification of Turkish POS tagging fixes
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("TURKISH POS TAGGING VERIFICATION")
print("=" * 40)

try:
    from nlp.custom_bert_processor import create_custom_bert_processor
    
    print("Creating BERT processor...")
    bert = create_custom_bert_processor()
    
    # Test the specific examples from user
    test_cases = [
        ("at", "NOUN"),  # "at" should be NOUN (horse)
        ("koşuyor", "VERB")  # "koşuyor" should be VERB (running)
    ]
    
    print("\nTesting Turkish words:")
    all_correct = True
    
    for word, expected_pos in test_cases:
        print(f"\nTesting: '{word}'")
        tokens = bert.process_text(word)
        
        if tokens:
            actual_pos = tokens[0]['upos']
            is_correct = actual_pos == expected_pos
            status = "✅ CORRECT" if is_correct else "❌ WRONG"
            
            print(f"  Expected: {expected_pos}")
            print(f"  Got: {actual_pos}")
            print(f"  Status: {status}")
            
            if not is_correct:
                all_correct = False
        else:
            print(f"  No tokens processed for '{word}'")
            all_correct = False
    
    print("\n" + "=" * 40)
    if all_correct:
        print("🎉 SUCCESS: All Turkish POS tests passed!")
        print("The BERT model now correctly classifies:")
        print("- 'at' as NOUN (noun)")
        print("- 'koşuyor' as VERB (verb)")
    else:
        print("⚠️ Some tests failed. Model may need adjustment.")
        
    print("\nYou can now test this in the GUI!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()